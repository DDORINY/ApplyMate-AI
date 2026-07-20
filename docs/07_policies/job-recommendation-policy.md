# Job Recommendation Policy

## Scope

v0.6.0 recommendations are rule-based and use only ApplyMate AI data owned by the current user.

## Recommendation type

```text
RULE_BASED
```

Do not label v0.6.0 recommendations as AI, machine learning, or automatic external collection.

## Score weights

| Factor | Max score |
| --- | ---: |
| Role match | 25 |
| Skill match | 25 |
| Experience match | 15 |
| Employment type | 10 |
| Location | 10 |
| Project/domain evidence | 10 |
| User preference/history | 5 |

## Grades

- `EXCELLENT`: 85~100
- `GOOD`: 70~84
- `POSSIBLE`: 50~69
- `LOW`: 0~49
- `BLOCKED`: required condition mismatch exists

## Feedback

Feedback is stored but does not automatically train or adjust weights in v0.6.0.

`HIDDEN` and `NOT_INTERESTED` can exclude the same job from later generation.
