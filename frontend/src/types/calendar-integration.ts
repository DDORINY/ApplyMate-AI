export type CalendarSyncDirection = "INTERNAL_TO_GOOGLE" | "GOOGLE_TO_INTERNAL" | "BIDIRECTIONAL";
export type CalendarConnectionStatus = "ACTIVE" | "REAUTH_REQUIRED" | "DISCONNECTED" | "ERROR";
export type CalendarSyncStatus =
  | "SYNCED"
  | "PENDING"
  | "CONFLICT"
  | "DELETED_INTERNAL"
  | "DELETED_EXTERNAL"
  | "FAILED";
export type SyncRunStatus = "RUNNING" | "COMPLETED" | "FAILED" | "PARTIAL_FAILED";

export type CalendarIntegrationStatusData = {
  connected: boolean;
  provider: string;
  email: string | null;
  display_name: string | null;
  scopes: string[];
  selected_calendar_id: string | null;
  selected_calendar_name: string | null;
  selected_calendar_timezone: string | null;
  sync_direction: CalendarSyncDirection | null;
  sync_enabled: boolean;
  status: CalendarConnectionStatus | null;
  last_sync_at: string | null;
  needs_verification: boolean;
};

export type CalendarConnectData = {
  authorization_url: string;
  state: string;
  provider: string;
  scopes: string[];
};

export type ExternalCalendarPublic = {
  id: string;
  name: string;
  timezone: string;
  primary: boolean;
  access_role: string;
  writable: boolean;
  selected: boolean;
};

export type CalendarSettingsPayload = {
  selected_calendar_id?: string | null;
  sync_direction?: CalendarSyncDirection | null;
  sync_enabled?: boolean | null;
};

export type CalendarSyncMappingPublic = {
  id: number;
  schedule_event_id: number;
  external_calendar_id: string;
  external_event_id: string;
  external_etag: string | null;
  sync_status: CalendarSyncStatus;
  last_synced_at: string | null;
  updated_at: string;
};

export type CalendarSyncRunPublic = {
  id: number;
  direction: CalendarSyncDirection;
  status: SyncRunStatus;
  started_at: string;
  completed_at: string | null;
  created_count: number;
  updated_count: number;
  deleted_count: number;
  skipped_count: number;
  conflict_count: number;
  error_count: number;
};

export type CalendarSyncErrorPublic = {
  id: number;
  sync_run_id: number | null;
  mapping_id: number | null;
  error_code: string;
  safe_message: string;
  retryable: boolean;
  created_at: string;
};

export type CalendarSyncResult = {
  run: CalendarSyncRunPublic;
  mappings: CalendarSyncMappingPublic[];
  errors: CalendarSyncErrorPublic[];
};

export type EventSyncStatusData = {
  connected: boolean;
  mapping: CalendarSyncMappingPublic | null;
  last_error: CalendarSyncErrorPublic | null;
};
