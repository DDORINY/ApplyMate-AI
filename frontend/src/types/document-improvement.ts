export type DocumentImprovementType =
  | "CLARITY"
  | "CONCISENESS"
  | "PROFESSIONAL_TONE"
  | "JOB_ALIGNMENT"
  | "COMPANY_ALIGNMENT"
  | "SKILL_EMPHASIS"
  | "EXPERIENCE_EMPHASIS"
  | "PROJECT_EMPHASIS"
  | "ACHIEVEMENT_EMPHASIS"
  | "STRUCTURE"
  | "GRAMMAR"
  | "LENGTH_REDUCTION"
  | "LENGTH_EXPANSION"
  | "CUSTOM";

export type DocumentImprovementRunStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "INVALID_OUTPUT"
  | "REVIEW_REQUIRED"
  | "APPLIED"
  | "REJECTED";

export type DocumentImprovementSuggestionStatus = "PENDING" | "APPROVED" | "REJECTED" | "APPLIED";
export type DocumentImprovementRiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type DocumentImprovementChangeType = "REWRITE" | "ADD" | "DELETE" | "STRUCTURE" | "GRAMMAR" | "TONE" | "LENGTH";

export type DocumentImprovementCreatePayload = {
  improvement_type: DocumentImprovementType;
  custom_instruction?: string | null;
  base_version_id?: number | null;
  target_min_length?: number | null;
  target_max_length?: number | null;
  target_tone?: string | null;
  source_ids?: number[];
};

export type DocumentImprovementSuggestionPublic = {
  id: number;
  run_id: number;
  paragraph_index: number;
  sentence_index: number;
  original_text: string;
  suggested_text: string;
  change_type: DocumentImprovementChangeType;
  reason: string;
  evidence: Record<string, unknown>[];
  risk_level: DocumentImprovementRiskLevel;
  status: DocumentImprovementSuggestionStatus;
  selected: boolean;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentImprovementRunPublic = {
  id: number;
  user_id: number;
  application_document_id: number;
  base_version_id: number;
  result_version_id: number | null;
  status: DocumentImprovementRunStatus;
  improvement_type: DocumentImprovementType;
  custom_instruction: string | null;
  target_min_length: number | null;
  target_max_length: number | null;
  target_tone: string | null;
  provider: string;
  model: string | null;
  prompt_version: string;
  schema_version: string;
  input_hash: string;
  source_hash: string;
  outdated: boolean;
  started_at: string;
  completed_at: string | null;
  error_code: string | null;
  safe_error_message: string | null;
  overall_feedback: string | null;
  suggested_title: string | null;
  suggested_content: string | null;
  warnings: string[];
  missing_information: string[];
  confidence: Record<string, number>;
  usage_metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  suggestions: DocumentImprovementSuggestionPublic[];
  sources: Array<Record<string, unknown>>;
  actions: Array<Record<string, unknown>>;
};

export type DocumentImprovementListData = {
  items: DocumentImprovementRunPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type DocumentImprovementApplyData = {
  applied: boolean;
  version_id: number;
  version_number: number;
  applied_suggestion_count: number;
};
