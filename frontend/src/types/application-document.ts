export type ApplicationDocumentType =
  | "MOTIVATION"
  | "JOB_COMPETENCY"
  | "SELF_INTRODUCTION"
  | "PROJECT_EXPERIENCE"
  | "CAREER_EXPERIENCE"
  | "FUTURE_PLAN"
  | "FREE_FORM"
  | "CUSTOM_QUESTION";

export type ApplicationDocumentStatus =
  | "DRAFT"
  | "GENERATING"
  | "COMPLETED"
  | "FAILED"
  | "REVIEW_REQUIRED"
  | "ARCHIVED";

export type ApplicationDocumentTone =
  | "PROFESSIONAL"
  | "CONCISE"
  | "CONFIDENT"
  | "HUMBLE"
  | "TECHNICAL"
  | "STORYTELLING";

export type GenerationRunStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "INVALID_OUTPUT"
  | "PROVIDER_UNAVAILABLE";

export type ApplicationDocumentSourceReference = {
  source_type: string;
  source_id: string;
  field_path: string | null;
  evidence_text: string;
  page_number?: number | null;
  section?: string | null;
  start_offset?: number | null;
  end_offset?: number | null;
};

export type ApplicationDocumentBlock = {
  sequence: number;
  text: string;
  source_references: ApplicationDocumentSourceReference[];
  confidence: number;
  requires_review: boolean;
  review_reason: string | null;
};

export type ApplicationDocumentVersionPublic = {
  id: number;
  document_id: number;
  user_id: number;
  version_number: number;
  content: string;
  content_blocks: ApplicationDocumentBlock[] | Record<string, unknown>[];
  character_count: number;
  character_count_without_spaces: number;
  word_count: number;
  paragraph_count: number;
  limit_exceeded: boolean;
  is_ai_generated: boolean;
  is_user_edited: boolean;
  generation_run_id: number | null;
  change_summary: string | null;
  created_at: string;
};

export type ApplicationDocumentPublic = {
  id: number;
  user_id: number;
  job_id: number | null;
  resume_id: number | null;
  resume_file_id: number | null;
  resume_analysis_id: number | null;
  job_analysis_id: number | null;
  job_match_id: number | null;
  document_type: ApplicationDocumentType;
  title: string;
  question: string | null;
  instructions: string | null;
  tone: ApplicationDocumentTone;
  language: string;
  character_limit: number | null;
  minimum_character_count: number | null;
  target_character_count: number | null;
  maximum_character_count: number | null;
  focus_points: string[];
  avoid_phrases: string[];
  settings: Record<string, unknown>;
  status: ApplicationDocumentStatus;
  current_version_number: number | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  current_version: ApplicationDocumentVersionPublic | null;
};

export type ApplicationDocumentListData = {
  items: ApplicationDocumentPublic[];
  total: number;
  page: number;
  size: number;
};

export type ApplicationDocumentPayload = {
  title: string;
  document_type: ApplicationDocumentType;
  job_id?: number | null;
  resume_id?: number | null;
  resume_file_id?: number | null;
  resume_analysis_id?: number | null;
  job_analysis_id?: number | null;
  job_match_id?: number | null;
  question?: string | null;
  instructions?: string | null;
  tone?: ApplicationDocumentTone;
  language?: string;
  character_limit?: number | null;
  focus_points?: string[];
  avoid_phrases?: string[];
};

export type ApplicationDocumentSourcePublic = {
  id: number;
  document_id: number;
  version_id: number;
  source_type: string;
  source_id: string;
  field_path: string | null;
  source_snapshot: Record<string, unknown>;
  evidence: ApplicationDocumentSourceReference;
  created_at: string;
};

export type GenerationRunPublic = {
  id: number;
  document_id: number;
  status: GenerationRunStatus;
  provider: string;
  model: string | null;
  error_code: string | null;
  safe_error_message: string | null;
  usage_metadata: Record<string, unknown>;
  result_snapshot: Record<string, unknown> | null;
  created_at: string;
};

export type DocumentProviderStatus = {
  active_provider: string;
  enabled: boolean;
  model: string | null;
  generation_available: boolean;
};
