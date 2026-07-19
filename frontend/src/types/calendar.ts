import type { ApplicationOptionItem } from "./application";

export type ScheduleEventType =
  | "APPLICATION_DEADLINE"
  | "DOCUMENT_RESULT"
  | "CODING_TEST"
  | "ASSIGNMENT_DEADLINE"
  | "INTERVIEW"
  | "FINAL_INTERVIEW"
  | "FINAL_RESULT"
  | "OFFER_RESPONSE_DEADLINE"
  | "USER_EVENT";

export type ScheduleEventStatus =
  | "SCHEDULED"
  | "CONFIRMED"
  | "COMPLETED"
  | "CANCELLED"
  | "MISSED"
  | "TENTATIVE";

export type ScheduleConfidence = "CONFIRMED" | "ESTIMATED" | "USER_INPUT" | "AI_EXTRACTED" | "EMAIL_EXTRACTED";
export type ScheduleReminderType = "IN_APP" | "EMAIL" | "PUSH";
export type ScheduleReminderStatus = "ACTIVE" | "INACTIVE" | "SENT" | "FAILED";
export type ScheduleHistoryAction =
  | "CREATED"
  | "UPDATED"
  | "STATUS_CHANGED"
  | "REMINDER_CHANGED"
  | "CANCELLED"
  | "COMPLETED"
  | "ARCHIVED";
export type ScheduleHistorySource = "USER" | "SYSTEM" | "AI" | "EMAIL";

export type ScheduleReminderPayload = {
  reminder_type?: ScheduleReminderType;
  minutes_before: number;
};

export type ScheduleEventPayload = {
  application_id?: number | null;
  job_id?: number | null;
  title: string;
  description?: string | null;
  event_type?: ScheduleEventType;
  status?: ScheduleEventStatus;
  confidence?: ScheduleConfidence;
  start_at: string;
  end_at: string;
  all_day?: boolean;
  timezone?: string;
  location?: string | null;
  online_url?: string | null;
  source?: string | null;
  source_reference?: string | null;
  confirmation_required?: boolean;
  reminders?: ScheduleReminderPayload[];
};

export type ScheduleConflictItem = {
  id: number;
  title: string;
  event_type: ScheduleEventType;
  status: ScheduleEventStatus;
  start_at: string;
  end_at: string;
};

export type ScheduleEventPublic = {
  id: number;
  user_id: number;
  application_id: number | null;
  job_id: number | null;
  title: string;
  description: string | null;
  event_type: ScheduleEventType;
  status: ScheduleEventStatus;
  effective_status: ScheduleEventStatus;
  confidence: ScheduleConfidence;
  start_at: string;
  end_at: string;
  all_day: boolean;
  timezone: string;
  location: string | null;
  online_url: string | null;
  source: string | null;
  source_reference: string | null;
  is_archived: boolean;
  completed_at: string | null;
  cancelled_at: string | null;
  confirmation_required: boolean;
  reminders_count: number;
  has_conflict: boolean;
  conflicting_events: ScheduleConflictItem[];
  is_overdue: boolean;
  is_due_soon: boolean;
  days_remaining: number | null;
  hours_remaining: number | null;
  created_at: string;
  updated_at: string;
};

export type ScheduleEventListData = {
  items: ScheduleEventPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type ScheduleReminderPublic = {
  id: number;
  event_id: number;
  user_id: number;
  reminder_type: ScheduleReminderType;
  minutes_before: number;
  scheduled_at: string;
  status: ScheduleReminderStatus;
  sent_at: string | null;
  failed_at: string | null;
  error_code: string | null;
  created_at: string;
  updated_at: string;
};

export type ScheduleEventHistoryPublic = {
  id: number;
  event_id: number;
  user_id: number;
  action: ScheduleHistoryAction;
  previous_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  changed_fields: string[] | null;
  source: ScheduleHistorySource;
  created_at: string;
};

export type ScheduleOptionsData = {
  event_types: ScheduleEventType[];
  statuses: ScheduleEventStatus[];
  confidences: ScheduleConfidence[];
  reminder_types: ScheduleReminderType[];
  reminder_presets: number[];
  applications: ApplicationOptionItem[];
  jobs: ApplicationOptionItem[];
};

export type ScheduleUpcomingData = {
  items: ScheduleEventPublic[];
  thresholds: number[];
};
