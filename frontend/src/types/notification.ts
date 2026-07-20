export type NotificationEventType =
  | "SCHEDULE_REMINDER"
  | "APPLICATION_DEADLINE"
  | "INTERVIEW_REMINDER"
  | "ASSESSMENT_DEADLINE"
  | "JOB_RECOMMENDATION_NEW"
  | "JOB_RECOMMENDATION_SCORE_UP"
  | "GMAIL_CANDIDATE_CREATED"
  | "APPLICATION_STATUS_CHANGED"
  | "DOCUMENT_IMPROVEMENT_COMPLETED"
  | "DOCUMENT_IMPROVEMENT_FAILED"
  | "CALENDAR_SYNC_FAILED"
  | "GMAIL_SYNC_FAILED"
  | "SYSTEM";

export type NotificationStatus = "UNREAD" | "READ" | "DISMISSED" | "ARCHIVED" | "EXPIRED";
export type NotificationPriority = "LOW" | "NORMAL" | "HIGH" | "URGENT";
export type NotificationDeliveryStatus = "PENDING" | "PROCESSING" | "SENT" | "FAILED" | "RETRY_SCHEDULED" | "CANCELLED" | "SKIPPED";

export type NotificationPublic = {
  id: number;
  event_type: NotificationEventType;
  priority: NotificationPriority;
  status: NotificationStatus;
  title: string;
  message: string;
  source_type: string;
  source_id: string;
  source_url: string | null;
  created_at: string;
  read_at: string | null;
};

export type NotificationListData = {
  items: NotificationPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type NotificationUnreadCountData = {
  unread_count: number;
};

export type NotificationSettingPublic = {
  in_app_enabled: boolean;
  email_enabled: boolean;
  push_enabled: boolean;
  timezone: string;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  schedule_reminder_enabled: boolean;
  application_deadline_enabled: boolean;
  recommendation_enabled: boolean;
  gmail_candidate_enabled: boolean;
  document_improvement_enabled: boolean;
  sync_error_enabled: boolean;
  default_reminder_minutes: number;
  daily_digest_enabled: boolean;
  daily_digest_hour: number;
};

export type NotificationDeliveryPublic = {
  id: number;
  notification_id: number;
  channel: "IN_APP" | "EMAIL" | "PUSH";
  status: NotificationDeliveryStatus;
  provider: string;
  attempt_count: number;
  error_code: string | null;
  safe_error_message: string | null;
};
