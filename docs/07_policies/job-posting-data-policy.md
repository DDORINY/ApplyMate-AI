# 채용공고 데이터 정책

## 원칙

- 사용자가 직접 등록하거나 명시적으로 입력한 URL의 채용공고만 저장한다.
- 무단 대규모 crawling, 사이트별 scraper, robots 정책을 우회하는 수집은 v0.2.0 범위에 포함하지 않는다.
- URL 등록은 편의 기능이며 자동 추출 결과는 사용자가 확인해야 한다.
- 마감일이 명확하지 않으면 `deadline_type=UNKNOWN` 또는 `UNTIL_FILLED`, `ONGOING`으로 저장한다.

## URL 등록 제한

- 허용 scheme: `http`, `https`
- 차단 대상: localhost, loopback, private network, link-local, multicast, reserved IP
- redirect 대상도 재검증한다.
- HTML 응답만 처리한다.
- 응답 크기는 제한한다.

## 개인정보와 보안

- URL 수집 실패 시 내부 네트워크 정보와 원본 예외 세부 사항을 사용자에게 그대로 노출하지 않는다.
- OAuth token, API key, password, session token은 공고 본문이나 로그에 저장하지 않는다.
- URL 원문은 `source_url`, 추출 텍스트는 `original_content`로 분리한다.
