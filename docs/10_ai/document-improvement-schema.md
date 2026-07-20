# Document Improvement Schema

문서 기준 버전: `v0.7.0`

## Structured output

```json
{
  "summary": "개선 요약",
  "overall_feedback": "전체 피드백",
  "suggested_title": "개선 제목",
  "suggested_content": "개선된 전체 문서",
  "sentence_suggestions": [
    {
      "paragraph_index": 0,
      "sentence_index": 0,
      "original_text": "원문",
      "suggested_text": "개선 문장",
      "change_type": "REWRITE",
      "reason": "변경 이유",
      "evidence": [
        {
          "source_type": "CURRENT_DOCUMENT",
          "source_id": "1",
          "source_text": "근거 텍스트"
        }
      ],
      "risk_level": "LOW",
      "selected": true
    }
  ],
  "warnings": [],
  "missing_information": [],
  "used_sources": [],
  "confidence": {
    "overall": 0.72
  }
}
```

## Validation rules

- `sentence_suggestions`는 빈 배열이 아니어야 한다.
- `original_text`와 `suggested_text`는 비어 있으면 안 된다.
- 사실 변경 제안은 evidence를 포함해야 한다.
- 근거가 불충분한 항목은 warning 또는 missing information으로 표시한다.
