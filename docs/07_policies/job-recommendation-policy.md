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

## v0.6.1 Automation Policy

- Recommendation automation starts disabled and `MANUAL`.
- `run-if-due` only evaluates execution conditions and calls the existing `RULE_BASED` recommendation service.
- Snapshot change detection is calculated by Backend.
- Notification candidates are stored for user review, but no email or push is sent.
- Dashboard reads existing Snapshot data and does not trigger recommendation generation.
- External job crawling, AI/ML recommendation calls, automatic application submission, and automatic feedback learning remain excluded.
