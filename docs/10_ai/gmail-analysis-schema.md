# Gmail Analysis Schema

```json
{
  "candidate_type": "INTERVIEW",
  "company_name_candidate": "Example",
  "job_title_candidate": "Backend Engineer",
  "event_title_candidate": "Example interview",
  "start_at_candidate": "2026-07-25T14:00:00+09:00",
  "end_at_candidate": "2026-07-25T15:00:00+09:00",
  "timezone_candidate": "Asia/Seoul",
  "location_candidate": null,
  "online_url_candidate": null,
  "application_status_candidate": "INTERVIEW",
  "confidence": 85,
  "requires_review": true,
  "evidence": {
    "subject": "Interview invitation",
    "sender": "hr@example.com",
    "source_text": "Interview on July 25 at 2 PM",
    "received_at": "2026-07-20T00:00:00Z"
  }
}
```

모호한 날짜나 부족한 근거는 확정하지 않고 `requires_review=true`로 처리한다.
