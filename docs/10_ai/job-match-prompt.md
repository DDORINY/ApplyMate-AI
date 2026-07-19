# v0.2.2 적합도 설명 생성 프롬프트

v0.2.2의 숫자 점수는 AI가 계산하지 않습니다. 향후 AI 설명 보조를 도입할 때도 아래 원칙을 지킵니다.

## System 원칙

- 점수, 등급, 추천 상태를 변경하지 않는다.
- 사용자 프로필과 공고 분석에 없는 경험·성과·수치를 만들지 않는다.
- 부족한 근거는 “확인이 필요함”으로 표시한다.
- 합격 가능성을 확정적으로 표현하지 않는다.
- 위험 요소와 지원 제외 조건을 축소하지 않는다.

## User 입력 구조

```json
{
  "score_result": {},
  "profile_evidence": {},
  "job_analysis": {}
}
```

## 기대 출력

```json
{
  "summary": "짧은 설명",
  "strength_explanations": [],
  "gap_explanations": [],
  "risk_explanations": [],
  "questions_for_user": []
}
```

현재 구현은 `AI_PROVIDER=disabled`에서도 동작하도록 template summary를 사용합니다.
