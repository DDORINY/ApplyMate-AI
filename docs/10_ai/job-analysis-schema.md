# 채용공고 AI 분석 Schema

Schema version: `v1`

```json
{
  "summary": "공고 전체 요약",
  "position": {
    "title": "AI Backend Developer",
    "category": "BACKEND",
    "seniority": "ENTRY",
    "employment_type": "FULL_TIME"
  },
  "responsibilities": [
    {
      "text": "AI 서비스 API 개발",
      "importance": "HIGH",
      "evidence": "공고 원문 근거"
    }
  ],
  "required_qualifications": [
    {
      "text": "Python 기반 백엔드 개발 경험",
      "category": "TECHNICAL",
      "importance": "REQUIRED",
      "evidence": "공고 원문 근거"
    }
  ],
  "preferred_qualifications": [],
  "technical_skills": [
    {
      "name": "Python",
      "category": "LANGUAGE",
      "requirement": "REQUIRED",
      "evidence": "공고 원문 근거"
    }
  ],
  "experience": {
    "minimum_years": null,
    "maximum_years": null,
    "entry_level_allowed": null,
    "description": "경력 조건 원문"
  },
  "education": {
    "minimum_level": "UNKNOWN",
    "description": "학력 조건 원문"
  },
  "work_conditions": {
    "location": "Seoul",
    "work_type": "HYBRID",
    "employment_type": "FULL_TIME"
  },
  "recruitment_process": ["서류", "면접"],
  "deadline": {
    "type": "FIXED",
    "date": "2026-08-31T14:59:59Z",
    "description": "마감일 원문"
  },
  "company_values": [],
  "keywords": ["Python", "FastAPI"],
  "warnings": [
    {
      "code": "UNCLEAR_EXPERIENCE",
      "message": "경력 조건이 명확하지 않습니다."
    }
  ],
  "confidence": {
    "overall": 0.8,
    "responsibilities": 0.8,
    "qualifications": 0.8,
    "skills": 0.8,
    "deadline": 0.8
  }
}
```

confidence는 0 이상 1 이하의 보조 지표입니다. 사용자에게 합격 가능성처럼 확정적으로 표현하지 않습니다.
