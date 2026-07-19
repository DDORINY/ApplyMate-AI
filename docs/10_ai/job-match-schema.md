# v0.2.2 적합도 분석 결과 스키마

```json
{
  "total_score": 78,
  "grade": "GOOD",
  "recommendation_status": "RECOMMENDED",
  "scores": {
    "role": 90,
    "skill": 75,
    "experience": 85,
    "project": 75,
    "preference": 80,
    "risk": 65
  },
  "matched_skills": [
    {
      "name": "Python",
      "requirement": "REQUIRED",
      "user_source": "USER_SKILL",
      "evidence": "Python"
    }
  ],
  "missing_skills": [
    {
      "name": "PostgreSQL",
      "requirement": "PREFERRED",
      "impact": "MEDIUM"
    }
  ],
  "matched_projects": [
    {
      "project_id": 1,
      "title": "ApplyMate",
      "matched_skills": ["python", "fastapi"],
      "matched_keywords": ["api"],
      "reason": "Project evidence overlaps with job skills or responsibilities."
    }
  ],
  "strengths": [],
  "gaps": [],
  "risks": [],
  "recommendation_summary": "공고 요구사항과 사용자 프로필의 핵심 근거가 잘 맞습니다.",
  "profile_completeness": 80,
  "calculation_version": "v1"
}
```

저장 API 응답에는 위 결과에 더해 `id`, `user_id`, `job_posting_id`, `job_analysis_id`, hash, 생성/수정 시각, `is_outdated`가 포함됩니다.
