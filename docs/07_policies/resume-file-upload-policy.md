# Resume File Upload Policy

## 목적

v0.3.0 이력서 업로드 기능의 파일 보안, 저장, 다운로드, 삭제 정책을 정의한다.

## 허용 파일

| 유형 | 확장자 | MIME | 실제 검증 |
| --- | --- | --- | --- |
| PDF | `.pdf` | `application/pdf` | magic bytes `%PDF-` |
| DOCX | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | ZIP 구조, `[Content_Types].xml`, `word/document.xml` |

## 파일명 정책

- 원본 파일명은 표시용 메타데이터로만 저장한다.
- 원본 파일명은 저장 경로에 사용하지 않는다.
- 내부 저장명은 UUID 기반이다.
- 경로 구분자 `/`, `\`를 포함한 파일명은 거부한다.
- NULL byte와 제어 문자를 포함한 파일명은 거부한다.
- 허용 확장자를 숨긴 다중 확장자는 거부한다.

## 크기 제한

- 업로드는 64KB chunk 단위로 읽는다.
- 누적 크기가 `RESUME_MAX_FILE_SIZE_BYTES`를 초과하면 즉시 중단한다.
- SHA-256 hash는 chunk read 중 계산한다.

## 저장 정책

- LocalFileStorage를 기본 구현으로 사용한다.
- 저장 경로는 `RESUME_STORAGE_DIR` 아래여야 한다.
- 저장 전후로 path traversal 가능성을 차단한다.
- 같은 사용자 기준 `(user_id, file_hash)` 중복 업로드를 차단한다.

## 다운로드 정책

- Access Token이 필요하다.
- `resume_id`, `file_id`, `user_id`를 함께 검증한다.
- DB에는 있으나 저장소에 없는 파일은 `RESUME_FILE_MISSING_ON_STORAGE`로 응답한다.
- `Content-Disposition: attachment`를 사용한다.
- `filename*` 방식으로 원본 파일명을 인코딩한다.
- `X-Content-Type-Options: nosniff`를 설정한다.
