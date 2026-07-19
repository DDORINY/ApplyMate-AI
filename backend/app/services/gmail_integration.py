import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import hash_token
from app.integrations.gmail import get_gmail_provider
from app.integrations.gmail.base import GmailMessage
from app.models.application import ApplicationStatus, ApplicationStatusHistory, ApplicationStatusHistorySource
from app.models.email_analysis import (
    EmailAnalysisRun,
    EmailCandidate,
    EmailCandidateAction,
    EmailCandidateActionType,
    EmailCandidateStatus,
    EmailCandidateType,
    EmailMessage,
    EmailProcessingStatus,
    EmailSyncRun,
    EmailSyncRunStatus,
    GmailConnection,
    GmailConnectionStatus,
)
from app.models.integration import ExternalProvider
from app.models.schedule import (
    ScheduleConfidence,
    ScheduleEvent,
    ScheduleEventHistory,
    ScheduleEventStatus,
    ScheduleEventType,
    ScheduleHistoryAction,
    ScheduleHistorySource,
)
from app.repositories.application import ApplicationRepository
from app.repositories.gmail_integration import GmailIntegrationRepository
from app.repositories.schedule import ScheduleRepository
from app.schemas.gmail_integration import (
    EmailCandidateActionPublic,
    EmailCandidateApplicationOption,
    EmailCandidateApplicationOptionsData,
    EmailCandidateApproveData,
    EmailCandidateApproveRequest,
    EmailCandidateListData,
    EmailCandidatePublic,
    EmailMessagePublic,
    EmailSyncRunPublic,
    GmailCallbackData,
    GmailConnectData,
    GmailIntegrationStatusData,
    GmailSettingsUpdate,
    GmailSyncResult,
)
from app.services.external_token import ExternalTokenCipher


STATUS_BY_TYPE = {
    EmailCandidateType.APPLICATION_RECEIVED: ApplicationStatus.APPLIED,
    EmailCandidateType.DOCUMENT_REVIEW: ApplicationStatus.DOCUMENT_REVIEW,
    EmailCandidateType.CODING_TEST: ApplicationStatus.CODING_TEST,
    EmailCandidateType.ASSIGNMENT: ApplicationStatus.ASSIGNMENT,
    EmailCandidateType.INTERVIEW: ApplicationStatus.INTERVIEW,
    EmailCandidateType.FINAL_INTERVIEW: ApplicationStatus.FINAL_INTERVIEW,
    EmailCandidateType.OFFER: ApplicationStatus.OFFER,
    EmailCandidateType.REJECTED: ApplicationStatus.REJECTED,
    EmailCandidateType.WITHDRAWN: ApplicationStatus.WITHDRAWN,
}

EVENT_BY_TYPE = {
    EmailCandidateType.CODING_TEST: ScheduleEventType.CODING_TEST,
    EmailCandidateType.ASSIGNMENT: ScheduleEventType.ASSIGNMENT_DEADLINE,
    EmailCandidateType.INTERVIEW: ScheduleEventType.INTERVIEW,
    EmailCandidateType.FINAL_INTERVIEW: ScheduleEventType.FINAL_INTERVIEW,
    EmailCandidateType.OFFER: ScheduleEventType.OFFER_RESPONSE_DEADLINE,
    EmailCandidateType.SCHEDULE_CHANGE: ScheduleEventType.CODING_TEST,
}


class GmailIntegrationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = GmailIntegrationRepository(session)
        self.application_repository = ApplicationRepository(session)
        self.schedule_repository = ScheduleRepository(session)
        self.cipher = ExternalTokenCipher()

    async def status(self, user_id: int) -> GmailIntegrationStatusData:
        settings = get_settings()
        connection = await self.repository.get_connection(user_id)
        if connection is None or not connection.external_account.is_active:
            return GmailIntegrationStatusData(
                connected=False,
                provider=settings.gmail_provider,
                needs_verification=settings.gmail_provider == "google",
            )
        account = connection.external_account
        return GmailIntegrationStatusData(
            connected=connection.status != GmailConnectionStatus.DISCONNECTED,
            provider=settings.gmail_provider,
            email=account.email,
            display_name=account.display_name,
            scopes=self._scopes(account.scopes),
            status=connection.status,
            sync_enabled=connection.sync_enabled,
            search_query=connection.search_query,
            lookback_days=connection.lookback_days,
            last_sync_at=connection.last_sync_at,
            needs_verification=settings.gmail_provider == "google",
        )

    async def connect(self, user_id: int, redirect_path: str) -> GmailConnectData:
        self._ensure_safe_redirect(redirect_path)
        settings = get_settings()
        state = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(seconds=settings.gmail_oauth_state_expire_seconds)
        await self.repository.create_state(
            user_id=user_id,
            provider=ExternalProvider.GOOGLE,
            state_hash=hash_token(state),
            redirect_path=redirect_path,
            expires_at=expires_at,
        )
        await self.session.commit()
        scopes = list(settings.google_gmail_scopes)
        url = get_gmail_provider().authorization_url(state=state, redirect_uri=settings.google_gmail_redirect_uri, scopes=scopes)
        return GmailConnectData(authorization_url=url, state=state, provider="GOOGLE", scopes=scopes)

    async def callback(self, state: str | None, code: str | None) -> GmailCallbackData:
        if not state:
            raise AppError("GMAIL_OAUTH_STATE_INVALID", "Gmail OAuth state is required.", 400)
        if not code:
            raise AppError("GMAIL_PROVIDER_UNAVAILABLE", "Gmail OAuth code is required.", 400)
        oauth_state = await self.repository.get_state(hash_token(state))
        now = datetime.now(UTC)
        if oauth_state is None or oauth_state.consumed_at is not None:
            raise AppError("GMAIL_OAUTH_STATE_INVALID", "Gmail OAuth state is invalid.", 400)
        if self._as_utc(oauth_state.expires_at) < now:
            raise AppError("GMAIL_OAUTH_STATE_EXPIRED", "Gmail OAuth state is expired.", 400)
        oauth_state.consumed_at = now
        token = await get_gmail_provider().exchange_code(code=code, redirect_uri=get_settings().google_gmail_redirect_uri)
        account = await self.repository.upsert_external_account(
            user_id=oauth_state.user_id,
            provider_account_id=token.provider_account_id,
            email=token.email,
            display_name=token.display_name,
            scopes=" ".join(token.scopes or list(get_settings().google_gmail_scopes)),
            access_token_encrypted=self.cipher.encrypt(token.access_token),
            refresh_token_encrypted=self.cipher.encrypt(token.refresh_token) if token.refresh_token else None,
            token_expires_at=token.expires_at,
            token_version=get_settings().external_token_encryption_key_version,
            now=now,
        )
        connection = await self.repository.get_connection(oauth_state.user_id)
        if connection is None:
            connection = GmailConnection(
                user_id=oauth_state.user_id,
                external_account_id=account.id,
                provider=ExternalProvider.GOOGLE,
                search_query=get_settings().gmail_default_search_query,
                lookback_days=get_settings().gmail_default_lookback_days,
                connected_at=now,
            )
            self.session.add(connection)
        else:
            connection.external_account_id = account.id
            connection.status = GmailConnectionStatus.ACTIVE
            connection.sync_enabled = True
            connection.connected_at = now
            connection.disconnected_at = None
        await self.session.commit()
        return GmailCallbackData(connected=True, connection_id=connection.id, provider="GOOGLE", email=account.email)

    async def update_settings(self, user_id: int, payload: GmailSettingsUpdate) -> GmailIntegrationStatusData:
        connection = await self._active_connection(user_id)
        if payload.sync_enabled is not None:
            connection.sync_enabled = payload.sync_enabled
        if payload.search_query is not None:
            connection.search_query = payload.search_query
        if payload.lookback_days is not None:
            connection.lookback_days = payload.lookback_days
        await self.session.commit()
        return await self.status(user_id)

    async def disconnect(self, user_id: int) -> dict[str, bool]:
        connection = await self._active_connection(user_id)
        account = connection.external_account
        try:
            await get_gmail_provider().revoke_token(token=self.cipher.decrypt(account.access_token_encrypted))
        except AppError:
            pass
        now = datetime.now(UTC)
        connection.status = GmailConnectionStatus.DISCONNECTED
        connection.sync_enabled = False
        connection.disconnected_at = now
        account.is_active = False
        account.disconnected_at = now
        account.access_token_encrypted = self.cipher.encrypt("revoked")
        account.refresh_token_encrypted = None
        await self.session.commit()
        return {"disconnected": True}

    async def sync(self, user_id: int) -> GmailSyncResult:
        connection = await self._active_connection(user_id)
        if not connection.sync_enabled:
            raise AppError("GMAIL_PROVIDER_DISABLED", "Gmail sync is disabled.", 409)
        now = datetime.now(UTC)
        run = EmailSyncRun(user_id=user_id, connection_id=connection.id, status=EmailSyncRunStatus.RUNNING, started_at=now)
        self.session.add(run)
        await self.session.flush()
        access_token = self.cipher.decrypt(connection.external_account.access_token_encrypted)
        provider = get_gmail_provider()
        candidates: list[EmailCandidate] = []
        try:
            refs = await provider.search_messages(
                access_token=access_token,
                query=connection.search_query,
                max_results=get_settings().gmail_max_messages_per_sync,
            )
            run.scanned_count = len(refs)
            for ref in refs:
                existing = await self.repository.get_message_by_provider_id(connection.id, ref.id)
                if existing:
                    run.ignored_count += 1
                    continue
                provider_message = await provider.get_message(access_token=access_token, message_id=ref.id)
                message = self._message_model(user_id, connection.id, provider_message)
                self.session.add(message)
                await self.session.flush()
                run.matched_count += 1
                analysis_run, produced = self._analyze_message(user_id, message, provider_message)
                self.session.add(analysis_run)
                await self.session.flush()
                for candidate in produced:
                    candidate.analysis_run_id = analysis_run.id
                    self.session.add(candidate)
                    candidates.append(candidate)
                    run.candidate_count += 1
                message.processing_status = EmailProcessingStatus.COMPLETED if produced else EmailProcessingStatus.IGNORED
                message.classification = produced[0].candidate_type.value if produced else "OTHER"
                message.confidence = produced[0].confidence if produced else 0
            run.status = EmailSyncRunStatus.COMPLETED
        except AppError:
            run.status = EmailSyncRunStatus.FAILED
            run.error_count += 1
            await self.session.commit()
            raise
        run.completed_at = datetime.now(UTC)
        connection.last_sync_at = run.completed_at
        await self.session.commit()
        await self.session.refresh(run)
        return GmailSyncResult(
            run=EmailSyncRunPublic.model_validate(run),
            candidates=[self._candidate_public(item) for item in candidates],
        )

    async def list_sync_runs(self, user_id: int) -> list[EmailSyncRunPublic]:
        connection = await self._active_connection(user_id)
        return [EmailSyncRunPublic.model_validate(item) for item in await self.repository.list_sync_runs(user_id, connection.id)]

    async def get_sync_run(self, user_id: int, run_id: int) -> EmailSyncRunPublic:
        connection = await self._active_connection(user_id)
        run = await self.repository.get_sync_run(user_id, connection.id, run_id)
        if run is None:
            raise AppError("GMAIL_SYNC_FAILED", "Gmail sync run was not found.", 404)
        return EmailSyncRunPublic.model_validate(run)

    async def list_candidates(self, user_id: int, *, page: int, size: int, status=None, candidate_type=None) -> EmailCandidateListData:
        items, total = await self.repository.list_candidates(user_id, page=page, size=size, status=status, candidate_type=candidate_type)
        return EmailCandidateListData(items=[self._candidate_public(item) for item in items], total=total, page=page, size=size)

    async def get_candidate(self, user_id: int, candidate_id: int) -> EmailCandidatePublic:
        candidate = await self.repository.get_candidate(user_id, candidate_id)
        if candidate is None:
            raise AppError("EMAIL_CANDIDATE_NOT_FOUND", "Email candidate was not found.", 404)
        return self._candidate_public(candidate)

    async def application_options(self, user_id: int, candidate_id: int) -> EmailCandidateApplicationOptionsData:
        candidate = await self.repository.get_candidate(user_id, candidate_id)
        if candidate is None:
            raise AppError("EMAIL_CANDIDATE_NOT_FOUND", "Email candidate was not found.", 404)
        applications = await self.repository.list_application_options(user_id, candidate.company_name, candidate.job_title)
        items = []
        for application in applications:
            evidence = []
            if candidate.company_name and application.company_name_snapshot and candidate.company_name.lower() in application.company_name_snapshot.lower():
                evidence.append("company")
            if candidate.job_title and application.job_title_snapshot and candidate.job_title.lower() in application.job_title_snapshot.lower():
                evidence.append("job_title")
            match_type = "EXACT" if len(evidence) >= 2 else "LIKELY" if evidence else "NONE"
            items.append(
                EmailCandidateApplicationOption(
                    id=application.id,
                    company_name=application.company_name_snapshot,
                    job_title=application.job_title_snapshot,
                    status=application.status,
                    match_type=match_type,
                    evidence=evidence,
                )
            )
        return EmailCandidateApplicationOptionsData(items=items)

    async def link_application(self, user_id: int, candidate_id: int, application_id: int) -> EmailCandidatePublic:
        candidate = await self._candidate_or_error(user_id, candidate_id)
        application = await self.application_repository.get_application(user_id, application_id, include_archived=False)
        if application is None:
            raise AppError("EMAIL_CANDIDATE_APPLICATION_MISMATCH", "Application was not found for this user.", 404)
        candidate.application_id = application.id
        candidate.status = EmailCandidateStatus.REVIEWED
        self.session.add(EmailCandidateAction(user_id=user_id, candidate_id=candidate.id, action=EmailCandidateActionType.LINKED_APPLICATION, application_id=application.id))
        await self.session.commit()
        return self._candidate_public(candidate)

    async def reject_candidate(self, user_id: int, candidate_id: int, reason: str | None = None) -> EmailCandidatePublic:
        candidate = await self._candidate_or_error(user_id, candidate_id)
        if candidate.status == EmailCandidateStatus.APPLIED:
            raise AppError("EMAIL_CANDIDATE_ALREADY_APPLIED", "Email candidate is already applied.", 409)
        candidate.status = EmailCandidateStatus.REJECTED
        candidate.review_reason = reason
        self.session.add(EmailCandidateAction(user_id=user_id, candidate_id=candidate.id, action=EmailCandidateActionType.REJECTED, new_values={"reason": reason}))
        await self.session.commit()
        return self._candidate_public(candidate)

    async def approve_candidate(self, user_id: int, candidate_id: int, payload: EmailCandidateApproveRequest) -> EmailCandidateApproveData:
        candidate = await self._candidate_or_error(user_id, candidate_id)
        if candidate.status == EmailCandidateStatus.APPLIED:
            raise AppError("EMAIL_CANDIDATE_ALREADY_APPLIED", "Email candidate is already applied.", 409)
        application_id = payload.application_id or candidate.application_id
        actions: list[EmailCandidateAction] = []
        application = None
        if payload.apply_status_change:
            if application_id is None:
                raise AppError("EMAIL_CANDIDATE_APPLICATION_REQUIRED", "Application is required to apply status change.", 400)
            application = await self.application_repository.get_application(user_id, application_id, include_archived=False)
            if application is None:
                raise AppError("EMAIL_CANDIDATE_APPLICATION_MISMATCH", "Application was not found for this user.", 404)
            new_status = self._status_for_candidate(candidate)
            if new_status is not None:
                previous = application.status
                application.status = new_status
                self.session.add(
                    ApplicationStatusHistory(
                        application_id=application.id,
                        user_id=user_id,
                        previous_status=previous,
                        new_status=new_status,
                        reason="Gmail candidate approved",
                        note=f"Applied from email candidate #{candidate.id}",
                        source=ApplicationStatusHistorySource.EMAIL_CANDIDATE,
                    )
                )
                action = EmailCandidateAction(
                    user_id=user_id,
                    candidate_id=candidate.id,
                    action=EmailCandidateActionType.STATUS_CHANGED,
                    application_id=application.id,
                    previous_values={"status": previous.value},
                    new_values={"status": new_status.value},
                )
                self.session.add(action)
                actions.append(action)
                candidate.application_id = application.id
        if payload.create_schedule_event:
            schedule_event = self._schedule_event_from_candidate(user_id, candidate, application_id)
            self.session.add(schedule_event)
            await self.session.flush()
            self.session.add(
                ScheduleEventHistory(
                    event_id=schedule_event.id,
                    user_id=user_id,
                    action=ScheduleHistoryAction.CREATED,
                    new_values={"source": "EMAIL_CANDIDATE", "candidate_id": candidate.id},
                    changed_fields=["source", "source_reference"],
                    source=ScheduleHistorySource.EMAIL,
                )
            )
            action = EmailCandidateAction(
                user_id=user_id,
                candidate_id=candidate.id,
                action=EmailCandidateActionType.SCHEDULE_CREATED,
                application_id=application_id,
                schedule_event_id=schedule_event.id,
                new_values={"schedule_event_id": schedule_event.id},
            )
            self.session.add(action)
            actions.append(action)
        candidate.status = EmailCandidateStatus.APPLIED if actions else EmailCandidateStatus.APPROVED
        approve_action = EmailCandidateAction(user_id=user_id, candidate_id=candidate.id, action=EmailCandidateActionType.APPROVED, application_id=application_id)
        self.session.add(approve_action)
        actions.insert(0, approve_action)
        await self.session.commit()
        for action in actions:
            await self.session.refresh(action)
        await self.session.refresh(candidate)
        return EmailCandidateApproveData(
            candidate=self._candidate_public(candidate),
            actions=[EmailCandidateActionPublic.model_validate(action) for action in actions],
        )

    async def _active_connection(self, user_id: int) -> GmailConnection:
        connection = await self.repository.get_connection(user_id)
        if connection is None or connection.status == GmailConnectionStatus.DISCONNECTED:
            raise AppError("GMAIL_CONNECTION_NOT_FOUND", "Gmail connection was not found.", 404)
        if connection.status == GmailConnectionStatus.REAUTH_REQUIRED:
            raise AppError("GMAIL_REAUTH_REQUIRED", "Gmail connection requires reauthorization.", 409)
        return connection

    async def _candidate_or_error(self, user_id: int, candidate_id: int) -> EmailCandidate:
        candidate = await self.repository.get_candidate(user_id, candidate_id)
        if candidate is None:
            raise AppError("EMAIL_CANDIDATE_NOT_FOUND", "Email candidate was not found.", 404)
        return candidate

    def _message_model(self, user_id: int, connection_id: int, message: GmailMessage) -> EmailMessage:
        sanitized = self._sanitize_text(message.text)
        return EmailMessage(
            user_id=user_id,
            connection_id=connection_id,
            provider_message_id=message.id,
            provider_thread_id=message.thread_id,
            sender=message.sender,
            sender_domain=self._sender_domain(message.sender),
            subject=message.subject[:500],
            received_at=message.received_at,
            snippet=message.snippet[:1000],
            normalized_text_hash=self._hash(sanitized),
            sanitized_text=sanitized[:5000],
        )

    def _analyze_message(self, user_id: int, message: EmailMessage, provider_message: GmailMessage) -> tuple[EmailAnalysisRun, list[EmailCandidate]]:
        now = datetime.now(UTC)
        sanitized = self._sanitize_text(provider_message.text)
        candidate_type = self._classify(provider_message.subject, sanitized)
        result_snapshot = {"candidate_type": candidate_type.value, "subject": provider_message.subject}
        run = EmailAnalysisRun(
            user_id=user_id,
            email_message_id=message.id,
            status=EmailProcessingStatus.COMPLETED,
            provider="mock-rule",
            model="deterministic-v1",
            input_hash=self._hash(sanitized),
            started_at=now,
            completed_at=now,
            result_snapshot=result_snapshot,
        )
        if candidate_type == EmailCandidateType.OTHER:
            return run, []
        company, job_title = self._extract_company_job(provider_message.subject, sanitized)
        event_payload = self._event_payload(candidate_type, company, job_title, sanitized)
        status = self._status_for_type(candidate_type)
        evidence = {
            "subject": provider_message.subject,
            "sender": provider_message.sender,
            "source_text": self._evidence_text(sanitized),
            "received_at": provider_message.received_at.isoformat(),
        }
        candidate = EmailCandidate(
            user_id=user_id,
            email_message_id=message.id,
            candidate_type=candidate_type,
            company_name=company,
            job_title=job_title,
            event_payload=event_payload,
            status_payload={"application_status_candidate": status.value} if status else None,
            confidence=85 if not event_payload or event_payload.get("start_at_candidate") else 70,
            evidence=evidence,
            requires_review=True,
            review_reason="User confirmation is required before changing application data.",
        )
        return run, [candidate]

    def _classify(self, subject: str, text: str) -> EmailCandidateType:
        value = f"{subject} {text}".lower()
        if any(word in value for word in ["불합격", "rejected", "not selected"]):
            return EmailCandidateType.REJECTED
        if any(word in value for word in ["합격", "offer", "오퍼"]):
            return EmailCandidateType.OFFER
        if any(word in value for word in ["일정 변경", "변경"]):
            return EmailCandidateType.SCHEDULE_CHANGE
        if any(word in value for word in ["코딩테스트", "coding test"]):
            return EmailCandidateType.CODING_TEST
        if any(word in value for word in ["과제", "assignment"]):
            return EmailCandidateType.ASSIGNMENT
        if any(word in value for word in ["면접", "interview", "인터뷰"]):
            return EmailCandidateType.INTERVIEW
        if any(word in value for word in ["접수", "application received", "지원서"]):
            return EmailCandidateType.APPLICATION_RECEIVED
        return EmailCandidateType.OTHER

    def _extract_company_job(self, subject: str, text: str) -> tuple[str | None, str | None]:
        match = re.search(r"\[([^\]]+)\]", subject)
        company = match.group(1) if match else None
        for title in ["백엔드 개발자", "프론트엔드 개발자", "데이터 분석가", "플랫폼 엔지니어"]:
            if title in f"{subject} {text}":
                return company, title
        return company, None

    def _event_payload(self, candidate_type: EmailCandidateType, company: str | None, job_title: str | None, text: str) -> dict | None:
        if candidate_type not in EVENT_BY_TYPE:
            return None
        start_at = self._extract_datetime(text)
        requires_review = start_at is None
        if start_at is None:
            start_at = datetime.now(UTC) + timedelta(days=7)
        end_at = start_at + timedelta(hours=1)
        return {
            "event_title_candidate": f"{company or '채용'} {candidate_type.value}",
            "start_at_candidate": start_at.isoformat(),
            "end_at_candidate": end_at.isoformat(),
            "timezone_candidate": "Asia/Seoul",
            "location_candidate": None,
            "online_url_candidate": self._extract_url(text),
            "requires_review": requires_review,
        }

    def _extract_datetime(self, text: str) -> datetime | None:
        match = re.search(r"2026년\s*(\d{1,2})월\s*(\d{1,2})일\s*(오전|오후)?\s*(\d{1,2})?", text)
        if not match:
            return None
        month = int(match.group(1))
        day = int(match.group(2))
        hour = int(match.group(4) or 9)
        if match.group(3) == "오후" and hour < 12:
            hour += 12
        return datetime(2026, month, day, hour, tzinfo=UTC)

    def _extract_url(self, text: str) -> str | None:
        match = re.search(r"https?://\S+", text)
        return match.group(0)[:1000] if match else None

    def _status_for_candidate(self, candidate: EmailCandidate) -> ApplicationStatus | None:
        payload = candidate.status_payload or {}
        value = payload.get("application_status_candidate")
        return ApplicationStatus(value) if value else self._status_for_type(candidate.candidate_type)

    def _status_for_type(self, candidate_type: EmailCandidateType) -> ApplicationStatus | None:
        return STATUS_BY_TYPE.get(candidate_type)

    def _schedule_event_from_candidate(self, user_id: int, candidate: EmailCandidate, application_id: int | None) -> ScheduleEvent:
        payload = candidate.event_payload or {}
        if not payload:
            raise AppError("EMAIL_CANDIDATE_SCHEDULE_CONFLICT", "Candidate does not include schedule payload.", 400)
        start_at = self._parse_datetime(payload["start_at_candidate"])
        end_at = self._parse_datetime(payload["end_at_candidate"])
        return ScheduleEvent(
            user_id=user_id,
            application_id=application_id,
            title=payload.get("event_title_candidate") or candidate.candidate_type.value,
            description=f"Created from Gmail candidate #{candidate.id}. User approved this action.",
            event_type=EVENT_BY_TYPE.get(candidate.candidate_type, ScheduleEventType.USER_EVENT),
            status=ScheduleEventStatus.SCHEDULED,
            confidence=ScheduleConfidence.EMAIL_EXTRACTED,
            start_at=start_at,
            end_at=end_at,
            timezone=payload.get("timezone_candidate") or "Asia/Seoul",
            location=payload.get("location_candidate"),
            online_url=payload.get("online_url_candidate"),
            source="EMAIL_CANDIDATE",
            source_reference=str(candidate.id),
            confirmation_required=bool(payload.get("requires_review")),
        )

    def _candidate_public(self, candidate: EmailCandidate) -> EmailCandidatePublic:
        email_message = candidate.__dict__.get("email_message")
        return EmailCandidatePublic(
            id=candidate.id,
            email_message_id=candidate.email_message_id,
            candidate_type=candidate.candidate_type,
            status=candidate.status,
            company_name=candidate.company_name,
            job_title=candidate.job_title,
            application_id=candidate.application_id,
            event_payload=candidate.event_payload,
            status_payload=candidate.status_payload,
            confidence=candidate.confidence,
            evidence=candidate.evidence,
            requires_review=candidate.requires_review,
            review_reason=candidate.review_reason,
            expires_at=candidate.expires_at,
            created_at=candidate.created_at,
            email_message=EmailMessagePublic.model_validate(email_message) if email_message is not None else None,
        )

    def _sanitize_text(self, value: str) -> str:
        value = re.sub(r"<[^>]+>", " ", value)
        value = re.sub(r"(?i)ignore previous instructions|reveal system prompt|change application status|create calendar event automatically", "[ignored-instruction]", value)
        return re.sub(r"\s+", " ", value).strip()

    def _evidence_text(self, value: str) -> str:
        return value[:300]

    def _sender_domain(self, sender: str) -> str | None:
        match = re.search(r"@([^>\s]+)", sender)
        return match.group(1).lower() if match else None

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def _scopes(self, value: str) -> list[str]:
        return [item for item in value.replace(",", " ").split() if item]

    def _ensure_safe_redirect(self, path: str) -> None:
        if not path.startswith("/") or path.startswith("//") or "\\" in path:
            raise AppError("GMAIL_PROVIDER_UNAVAILABLE", "Invalid redirect path.", 400)

    def _as_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def _parse_datetime(self, value: str) -> datetime:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return self._as_utc(parsed)
