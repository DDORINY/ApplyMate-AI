# Schedule Management Policy

## Base principles

- Schedule data is user-owned data. Every read, update, delete, reminder, and history endpoint must validate `user_id`.
- Schedule status and schedule confidence are separate concepts.
- AI-extracted or email-extracted schedule candidates must not be displayed as confirmed schedules.
- v0.4.1 does not send real email, push, or external calendar notifications.

## Status policy

- `SCHEDULED`: default creation status
- `CONFIRMED`: confirmed by official source or user
- `COMPLETED`: completed schedule
- `CANCELLED`: cancelled schedule
- `MISSED`: computed read-time display status for overdue active events
- `TENTATIVE`: tentative schedule

## Confidence policy

- `USER_INPUT`: directly entered by the user
- `CONFIRMED`: verified from official source
- `ESTIMATED`: estimated by system logic
- `AI_EXTRACTED`: extracted by AI and needs confirmation
- `EMAIL_EXTRACTED`: reserved for future email extraction

## Reminder policy

- v0.4.1 stores and displays reminders only.
- Real email, push, and external calendar delivery is deferred.
- Duplicate reminders are blocked by event, reminder type, and `minutes_before`.
- Reminders for completed or cancelled schedules become inactive.

## Conflict policy

Conflict means an active, non-archived event for the same user overlaps the candidate time range.

```text
existing.start_at < new.end_at AND existing.end_at > new.start_at
```

Conflicts are warnings and do not block saving by default.
