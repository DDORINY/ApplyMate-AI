# Gmail Data Policy

ApplyMate AI는 Gmail을 채용 메일 분석 후보 생성 목적으로만 사용한다.

## 원칙

- Gmail OAuth는 로그인/Calendar OAuth와 분리한다.
- v0.5.1 scope는 읽기 전용 `gmail.readonly`만 사용한다.
- 사용자의 승인 없이 Gmail 메일을 수정, 삭제, 발송하지 않는다.
- 사용자의 승인 없이 지원 상태를 변경하거나 일정을 생성하지 않는다.
- 메일 HTML 원문, inline image, attachment 원문은 저장하지 않는다.

## 저장 데이터

- provider message id
- thread id
- sender, sender domain
- subject
- received_at
- snippet
- sanitized text hash
- 제한된 sanitized text
- classification
- confidence
- candidate evidence

## NEEDS_VERIFICATION

실제 Gmail OAuth token exchange, message search, message fetch는 운영 Google Cloud 설정 후 별도 검증이 필요하다.
