from math import ceil

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import utc_now
from app.models.job_recommendation import JobRecommendationGrade
from app.models.job_recommendation_automation import (
    JobRecommendationSnapshot,
    JobRecommendationSnapshotItem,
    RecommendationChangeReason,
    RecommendationChangeType,
    RecommendationConfidence,
    RecommendationNotificationCandidate,
    RecommendationNotificationType,
)
from app.repositories.job_recommendation import JobRecommendationRepository
from app.repositories.job_recommendation_automation import JobRecommendationAutomationRepository
from app.schemas.job_recommendation_automation import (
    JobRecommendationChangeListData,
    JobRecommendationSnapshotItemPublic,
    JobRecommendationSnapshotListData,
    JobRecommendationSnapshotPublic,
)
from app.services.job_recommendation_policy import POLICY_VERSION, RecommendationProfile, profile_hash


GRADE_ORDER = {
    JobRecommendationGrade.BLOCKED.value: 0,
    JobRecommendationGrade.LOW.value: 1,
    JobRecommendationGrade.POSSIBLE.value: 2,
    JobRecommendationGrade.GOOD.value: 3,
    JobRecommendationGrade.EXCELLENT.value: 4,
}


class JobRecommendationSnapshotService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = JobRecommendationAutomationRepository(session)
        self.recommendation_repository = JobRecommendationRepository(session)

    async def create_for_run(self, user_id: int, run_id: int, minimum_score: int = 0) -> JobRecommendationSnapshot:
        profile = await self.recommendation_repository.get_profile_bundle(user_id)
        current_profile_hash = profile_hash(
            RecommendationProfile(
                profile=profile[0],
                skills=profile[1],
                experiences=profile[2],
                projects=profile[3],
                preferences=profile[4],
            )
        )
        recommendations = [
            recommendation
            for recommendation in await self.repository.recommendations_for_run(user_id, run_id)
            if recommendation.score >= minimum_score
        ]
        previous = await self.repository.latest_snapshot(user_id)
        previous_by_job = {item.job_id: item for item in previous.items} if previous else {}

        snapshot = JobRecommendationSnapshot(
            user_id=user_id,
            run_id=run_id,
            profile_hash=current_profile_hash,
            policy_version=POLICY_VERSION,
            input_job_count=len(recommendations),
            recommended_count=0,
            generated_at=utc_now(),
        )
        self.session.add(snapshot)
        await self.session.flush()

        new_count = 0
        changed_count = 0
        current_job_ids: set[int] = set()
        for rank, recommendation in enumerate(recommendations, start=1):
            current_job_ids.add(recommendation.job_id)
            previous_item = previous_by_job.get(recommendation.job_id)
            change_type = RecommendationChangeType.NEW
            previous_score = None
            previous_grade = None
            score_delta = None
            rank_delta = None
            if previous_item:
                previous_score = previous_item.score
                previous_grade = previous_item.grade
                score_delta = recommendation.score - previous_item.score
                rank_delta = previous_item.rank - rank
                change_type = self._change_type(previous_item, recommendation)
            if change_type == RecommendationChangeType.NEW:
                new_count += 1
            elif change_type != RecommendationChangeType.UNCHANGED:
                changed_count += 1

            item = JobRecommendationSnapshotItem(
                snapshot_id=snapshot.id,
                recommendation_id=recommendation.id,
                job_id=recommendation.job_id,
                score=recommendation.score,
                grade=recommendation.grade.value,
                rank=rank,
                blocking_mismatch=recommendation.has_blocking_mismatch,
                change_type=change_type,
                previous_score=previous_score,
                score_delta=score_delta,
                previous_grade=previous_grade,
                rank_delta=rank_delta,
                change_reason=self._change_reason(previous_item, recommendation),
                reason_summary=[reason.label for reason in recommendation.reasons[:3]],
                missing_job_fields=self._missing_job_fields(recommendation),
                data_completeness_score=self._data_completeness_score(recommendation),
                recommendation_confidence=self._confidence(recommendation),
            )
            self.session.add(item)
            await self.session.flush()
            await self._create_notifications(user_id, snapshot.id, item, recommendation)

        removed_count = 0
        if previous:
            removed_count = len(set(previous_by_job) - current_job_ids)

        snapshot.recommended_count = len(recommendations)
        snapshot.new_count = new_count
        snapshot.changed_count = changed_count
        snapshot.removed_count = removed_count
        await self.session.commit()
        refreshed = await self.repository.get_snapshot(user_id, snapshot.id)
        return refreshed or snapshot

    def _change_type(self, previous_item, recommendation) -> RecommendationChangeType:
        if recommendation.outdated:
            return RecommendationChangeType.OUTDATED
        current_grade = recommendation.grade.value
        previous_grade = previous_item.grade
        if GRADE_ORDER.get(current_grade, 0) > GRADE_ORDER.get(previous_grade, 0):
            return RecommendationChangeType.GRADE_UP
        if GRADE_ORDER.get(current_grade, 0) < GRADE_ORDER.get(previous_grade, 0):
            return RecommendationChangeType.GRADE_DOWN
        if recommendation.score > previous_item.score:
            return RecommendationChangeType.SCORE_UP
        if recommendation.score < previous_item.score:
            return RecommendationChangeType.SCORE_DOWN
        return RecommendationChangeType.UNCHANGED

    def _change_reason(self, previous_item, recommendation) -> RecommendationChangeReason:
        if not previous_item:
            return RecommendationChangeReason.UNKNOWN
        return RecommendationChangeReason.UNKNOWN

    def _missing_job_fields(self, recommendation) -> list[str]:
        missing: list[str] = []
        job = recommendation.job
        if not job.position:
            missing.append("position")
        if not job.location:
            missing.append("location")
        if not job.deadline_at:
            missing.append("deadline_at")
        return missing

    def _data_completeness_score(self, recommendation) -> int:
        missing_count = len(recommendation.missing_profile_fields or []) + len(self._missing_job_fields(recommendation))
        return max(40, 100 - missing_count * 15)

    def _confidence(self, recommendation) -> RecommendationConfidence:
        score = self._data_completeness_score(recommendation)
        if score >= 85:
            return RecommendationConfidence.HIGH
        if score >= 65:
            return RecommendationConfidence.MEDIUM
        return RecommendationConfidence.LOW

    async def _create_notifications(self, user_id: int, snapshot_id: int, item: JobRecommendationSnapshotItem, recommendation) -> None:
        candidates: list[tuple[RecommendationNotificationType, str, str]] = []
        if item.change_type == RecommendationChangeType.NEW and item.score >= 80:
            candidates.append(
                (
                    RecommendationNotificationType.NEW_HIGH_SCORE_RECOMMENDATION,
                    "새 고득점 추천 공고",
                    f"{recommendation.job.title} 추천 점수가 {item.score}점입니다.",
                )
            )
        if item.change_type == RecommendationChangeType.SCORE_UP:
            candidates.append(
                (
                    RecommendationNotificationType.RECOMMENDATION_SCORE_INCREASED,
                    "추천 점수 상승",
                    f"{recommendation.job.title} 추천 점수가 {item.score_delta}점 상승했습니다.",
                )
            )
        if item.change_type == RecommendationChangeType.GRADE_UP:
            candidates.append(
                (
                    RecommendationNotificationType.RECOMMENDATION_GRADE_INCREASED,
                    "추천 등급 상승",
                    f"{recommendation.job.title} 추천 등급이 상승했습니다.",
                )
            )
        if item.change_type == RecommendationChangeType.OUTDATED:
            candidates.append(
                (
                    RecommendationNotificationType.RECOMMENDATION_BECAME_OUTDATED,
                    "추천 재계산 필요",
                    f"{recommendation.job.title} 추천 결과가 오래되었습니다.",
                )
            )
        for notification_type, title, message in candidates:
            exists = await self.repository.notification_exists(user_id, snapshot_id, recommendation.id, notification_type.value)
            if exists:
                continue
            self.session.add(
                RecommendationNotificationCandidate(
                    user_id=user_id,
                    recommendation_id=recommendation.id,
                    snapshot_id=snapshot_id,
                    snapshot_item_id=item.id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    payload={"score": item.score, "change_type": item.change_type.value},
                )
            )

    async def list_snapshots(self, user_id: int, page: int, size: int) -> JobRecommendationSnapshotListData:
        snapshots, total = await self.repository.list_snapshots(user_id, page, size)
        return JobRecommendationSnapshotListData(
            items=[self.public_snapshot(snapshot) for snapshot in snapshots],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    async def get_snapshot(self, user_id: int, snapshot_id: int) -> JobRecommendationSnapshotPublic:
        from app.core.exceptions import AppError

        snapshot = await self.repository.get_snapshot(user_id, snapshot_id)
        if not snapshot:
            raise AppError("RECOMMENDATION_SNAPSHOT_NOT_FOUND", "추천 Snapshot을 찾을 수 없습니다.", 404)
        return self.public_snapshot(snapshot)

    async def list_changes(
        self,
        user_id: int,
        *,
        page: int,
        size: int,
        change_type: RecommendationChangeType | None,
    ) -> JobRecommendationChangeListData:
        items, total = await self.repository.list_changes(user_id, page=page, size=size, change_type=change_type)
        return JobRecommendationChangeListData(
            items=[self.public_item(item) for item in items],
            page=page,
            size=size,
            total=total,
            total_pages=ceil(total / size) if total else 0,
        )

    def public_snapshot(self, snapshot: JobRecommendationSnapshot) -> JobRecommendationSnapshotPublic:
        return JobRecommendationSnapshotPublic(
            id=snapshot.id,
            user_id=snapshot.user_id,
            run_id=snapshot.run_id,
            profile_hash=snapshot.profile_hash,
            policy_version=snapshot.policy_version,
            input_job_count=snapshot.input_job_count,
            recommended_count=snapshot.recommended_count,
            new_count=snapshot.new_count,
            changed_count=snapshot.changed_count,
            removed_count=snapshot.removed_count,
            generated_at=snapshot.generated_at,
            created_at=snapshot.created_at,
            items=[self.public_item(item) for item in snapshot.items],
        )

    def public_item(self, item: JobRecommendationSnapshotItem) -> JobRecommendationSnapshotItemPublic:
        return JobRecommendationSnapshotItemPublic(
            id=item.id,
            snapshot_id=item.snapshot_id,
            recommendation_id=item.recommendation_id,
            job_id=item.job_id,
            score=item.score,
            grade=item.grade,
            rank=item.rank,
            blocking_mismatch=item.blocking_mismatch,
            change_type=item.change_type,
            previous_score=item.previous_score,
            score_delta=item.score_delta,
            previous_grade=item.previous_grade,
            rank_delta=item.rank_delta,
            change_reason=item.change_reason,
            reason_summary=item.reason_summary or [],
            missing_job_fields=item.missing_job_fields or [],
            data_completeness_score=item.data_completeness_score,
            recommendation_confidence=item.recommendation_confidence,
            created_at=item.created_at,
        )
