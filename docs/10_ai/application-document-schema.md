# Application Document Schema

Version: `v0.3.3`

## Provider output

```json
{
  "title": "Backend Engineer 지원동기",
  "document_type": "MOTIVATION",
  "content": "문서 본문",
  "blocks": [
    {
      "sequence": 1,
      "text": "문단 또는 문장",
      "source_references": [
        {
          "source_type": "job_posting",
          "source_id": "1",
          "field_path": "description",
          "evidence_text": "근거 텍스트"
        }
      ],
      "confidence": 0.72,
      "requires_review": false,
      "review_reason": null
    }
  ],
  "warnings": [],
  "requires_review": false,
  "character_count_candidate": 500
}
```

## Server-side counts

The server recalculates:

- `character_count`
- `character_count_without_spaces`
- `word_count`
- `paragraph_count`
- `limit_exceeded`

## Review states

Document status becomes `REVIEW_REQUIRED` when the provider marks review required, source validation produces warnings, or the final content exceeds the configured limit.
