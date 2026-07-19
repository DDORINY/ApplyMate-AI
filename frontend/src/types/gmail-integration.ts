import type { ApplicationStatus } from "@/types/application";

export type GmailConnectionStatus = "ACTIVE" | "REAUTH_REQUIRED" | "DISCONNECTED" | "ERROR";
export type EmailSyncRunStatus = "RUNNING" | "COMPLETED" | "FAILED" | "PARTIAL_FAILED";
export type EmailCandidateType =
  | "APPLICATION_RECEIVED"
  | "DOCUMENT_REVIEW"
  | "CODING_TEST"
  | "ASSIGNMENT"
  | "INTERVIEW"
  | "FINAL_INTERVIEW"
  | "OFFER"
  | "REJECTED"
  | "WITHDRAWN"
  | "SCHEDULE_CHANGE"
  | "RECRUITER_CONTACT"
  | "OTHER";
export type EmailCandidateStatus = "NEW" | "REVIEWED" | "APPROVED" | "REJECTED" | "APPLIED" | "EXPIRED";

export type GmailIntegrationStatusData = {
  connected: boolean;
  provider: string;
  email?: string | null;
  display_name?: string | null;
  scopes: string[];
  status?: GmailConnectionStatus | null;
  sync_enabled: boolean;
  search_query?: string | null;
  lookback_days?: number | null;
  last_sync_at?: string | null;
  needs_verification: boolean;
};

export type GmailConnectData = {
  authorization_url: string;
  state: string;
  provider: string;
  scopes: string[];
};

export type EmailSyncRunPublic = {
  id: number;
  status: EmailSyncRunStatus;
  started_at: string;
  completed_at?: string | null;
  scanned_count: number;
  matched_count: number;
  candidate_count: number;
  ignored_count: number;
  error_count: number;
};

export type EmailMessagePublic = {
  id: number;
  sender: string;
  sender_domain?: string | null;
  subject: string;
  received_at: string;
  snippet?: string | null;
  classification?: string | null;
  confidence: number;
};

export type EmailCandidatePublic = {
  id: number;
  email_message_id: number;
  candidate_type: EmailCandidateType;
  status: EmailCandidateStatus;
  company_name?: string | null;
  job_title?: string | null;
  application_id?: number | null;
  event_payload?: Record<string, unknown> | null;
  status_payload?: Record<string, unknown> | null;
  confidence: number;
  evidence: Record<string, unknown>;
  requires_review: boolean;
  review_reason?: string | null;
  created_at: string;
  email_message?: EmailMessagePublic | null;
};

export type EmailCandidateListData = {
  items: EmailCandidatePublic[];
  total: number;
  page: number;
  size: number;
};

export type GmailSyncResult = {
  run: EmailSyncRunPublic;
  candidates: EmailCandidatePublic[];
};

export type EmailCandidateApplicationOption = {
  id: number;
  company_name?: string | null;
  job_title?: string | null;
  status: ApplicationStatus;
  match_type: string;
  evidence: string[];
};

export type EmailCandidateApplicationOptionsData = {
  items: EmailCandidateApplicationOption[];
};
