export type ApplicationStatus =
  | "SAVED"
  | "PREPARING"
  | "APPLIED"
  | "DOCUMENT_REVIEW"
  | "CODING_TEST"
  | "ASSIGNMENT"
  | "INTERVIEW"
  | "FINAL_INTERVIEW"
  | "OFFER"
  | "REJECTED"
  | "WITHDRAWN"
  | "CLOSED";

export type ApplicationChannel =
  | "COMPANY_SITE"
  | "JOB_PORTAL"
  | "EMAIL"
  | "REFERRAL"
  | "RECRUITER"
  | "TALENT_POOL"
  | "OFFLINE"
  | "OTHER";

export type ApplicationPriority = "LOW" | "NORMAL" | "HIGH" | "URGENT";
export type ApplicationStatusHistorySource = "USER" | "SYSTEM" | "EMAIL_CANDIDATE" | "CALENDAR_SYNC";
export type ApplicationNoteType = "GENERAL" | "CONTACT" | "INTERVIEW" | "DOCUMENT" | "RESULT" | "REMINDER";

export type ApplicationPublic = {
  id: number;
  user_id: number;
  job_id: number | null;
  resume_id: number | null;
  resume_file_id: number | null;
  application_document_id: number | null;
  application_document_version_id: number | null;
  status: ApplicationStatus;
  applied_at: string | null;
  planned_apply_at: string | null;
  application_channel: ApplicationChannel;
  application_url: string | null;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  source: string | null;
  priority: ApplicationPriority;
  result_announced_at: string | null;
  closed_at: string | null;
  company_name_snapshot: string | null;
  job_title_snapshot: string | null;
  job_url_snapshot: string | null;
  is_archived: boolean;
  archived_at: string | null;
  notes_count: number;
  created_at: string;
  updated_at: string;
};

export type ApplicationPayload = {
  job_id?: number | null;
  resume_id?: number | null;
  resume_file_id?: number | null;
  application_document_id?: number | null;
  application_document_version_id?: number | null;
  status?: ApplicationStatus;
  applied_at?: string | null;
  planned_apply_at?: string | null;
  application_channel?: ApplicationChannel;
  application_url?: string | null;
  contact_name?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  source?: string | null;
  priority?: ApplicationPriority;
  result_announced_at?: string | null;
  closed_at?: string | null;
};

export type ApplicationListData = {
  items: ApplicationPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type ApplicationStatusHistoryPublic = {
  id: number;
  application_id: number;
  user_id: number;
  previous_status: ApplicationStatus | null;
  new_status: ApplicationStatus;
  changed_at: string;
  reason: string | null;
  note: string | null;
  source: ApplicationStatusHistorySource;
  created_at: string;
};

export type ApplicationNotePublic = {
  id: number;
  application_id: number;
  user_id: number;
  content: string;
  note_type: ApplicationNoteType;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
};

export type ApplicationNotePayload = {
  content?: string;
  note_type?: ApplicationNoteType;
  is_pinned?: boolean;
};

export type ApplicationOptionItem = {
  id: number;
  label: string;
  description: string | null;
  disabled_reason: string | null;
  metadata: Record<string, unknown>;
};

export type ApplicationOptionsData = {
  jobs: ApplicationOptionItem[];
  resumes: ApplicationOptionItem[];
  resume_files: ApplicationOptionItem[];
  resume_analyses: ApplicationOptionItem[];
  job_analyses: ApplicationOptionItem[];
  job_matches: ApplicationOptionItem[];
  application_documents: ApplicationOptionItem[];
  application_document_versions: ApplicationOptionItem[];
};
