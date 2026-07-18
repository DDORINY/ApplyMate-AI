from dataclasses import dataclass, field
from html.parser import HTMLParser
import ipaddress
import socket
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from app.core.exceptions import AppError

MAX_REDIRECTS = 3
MAX_RESPONSE_BYTES = 1_000_000
REQUEST_TIMEOUT_SECONDS = 5
USER_AGENT = "ApplyMateAI/0.2.0 job-url-import"


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


@dataclass
class ImportedUrlContent:
    final_url: str
    source_site: str | None
    title: str | None
    description: str | None
    text: str | None
    extracted_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class HtmlSummaryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.in_ignored = False
        self.title_parts: list[str] = []
        self.body_parts: list[str] = []
        self.meta_description: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value for key, value in attrs}
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() in {"script", "style", "noscript"}:
            self.in_ignored = True
        if tag.lower() == "meta" and attrs_dict.get("name", "").lower() == "description":
            content = attrs_dict.get("content")
            if content:
                self.meta_description = content.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        if tag.lower() in {"script", "style", "noscript"}:
            self.in_ignored = False

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self.in_title:
            self.title_parts.append(text)
        elif not self.in_ignored:
            self.body_parts.append(text)

    @property
    def title(self) -> str | None:
        value = " ".join(self.title_parts).strip()
        return value or None

    @property
    def body_text(self) -> str | None:
        value = " ".join(self.body_parts).strip()
        return value[:20_000] or None


def is_blocked_host(hostname: str) -> bool:
    lowered = hostname.strip().lower()
    blocked_hosts = {"localhost", "metadata.google.internal", "host.docker.internal"}
    if lowered in blocked_hosts or lowered.endswith(".local"):
        return True
    try:
        addresses = socket.getaddrinfo(lowered, None)
    except socket.gaierror as exc:
        raise AppError(
            "JOB_POSTING_URL_INVALID", "URL의 호스트를 확인할 수 없습니다.", 422
        ) from exc
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return True
    return False


def validate_external_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise AppError("JOB_POSTING_URL_INVALID", "http 또는 https URL만 등록할 수 있습니다.", 422)
    if parsed.username or parsed.password:
        raise AppError(
            "JOB_POSTING_URL_INVALID", "인증정보가 포함된 URL은 사용할 수 없습니다.", 422
        )
    if is_blocked_host(parsed.hostname):
        raise AppError(
            "JOB_POSTING_URL_BLOCKED", "내부 네트워크로 향하는 URL은 등록할 수 없습니다.", 422
        )
    return url


def fetch_url_content(url: str) -> ImportedUrlContent:
    current_url = validate_external_url(url)
    for _ in range(MAX_REDIRECTS + 1):
        request = Request(current_url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
        try:
            response = build_opener(NoRedirectHandler).open(
                request, timeout=REQUEST_TIMEOUT_SECONDS
            )
        except HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308}:
                response = exc
            else:
                raise AppError(
                    "JOB_POSTING_URL_FETCH_FAILED", "URL 내용을 가져오지 못했습니다.", 502
                ) from exc
        except OSError as exc:
            raise AppError(
                "JOB_POSTING_URL_FETCH_FAILED", "URL 내용을 가져오지 못했습니다.", 502
            ) from exc
        status = getattr(response, "status", getattr(response, "code", 200))
        if status in {301, 302, 303, 307, 308}:
            location = response.headers.get("Location")
            if not location:
                raise AppError(
                    "JOB_POSTING_URL_FETCH_FAILED", "redirect 위치를 확인할 수 없습니다.", 502
                )
            current_url = validate_external_url(urljoin(current_url, location))
            continue

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type.lower():
            raise AppError(
                "JOB_POSTING_URL_UNSUPPORTED_CONTENT", "HTML 응답만 가져올 수 있습니다.", 415
            )
        content = response.read(MAX_RESPONSE_BYTES + 1)
        if len(content) > MAX_RESPONSE_BYTES:
            raise AppError(
                "JOB_POSTING_URL_CONTENT_TOO_LARGE", "URL 응답이 허용 크기를 초과했습니다.", 413
            )
        return parse_html(current_url, content)

    raise AppError("JOB_POSTING_URL_BLOCKED", "redirect 횟수가 허용 범위를 초과했습니다.", 422)


def parse_html(final_url: str, content: bytes) -> ImportedUrlContent:
    parser = HtmlSummaryParser()
    parser.feed(content.decode("utf-8", errors="ignore"))
    extracted_fields: list[str] = []
    warnings: list[str] = []
    if parser.title:
        extracted_fields.append("title")
    if parser.meta_description:
        extracted_fields.append("description")
    if parser.body_text:
        extracted_fields.append("original_content")
    if not extracted_fields:
        warnings.append("HTML에서 자동 추출 가능한 내용을 찾지 못했습니다.")
    parsed = urlparse(final_url)
    return ImportedUrlContent(
        final_url=final_url,
        source_site=parsed.netloc.lower() if parsed.netloc else None,
        title=parser.title,
        description=parser.meta_description,
        text=parser.body_text,
        extracted_fields=extracted_fields,
        warnings=warnings,
    )
