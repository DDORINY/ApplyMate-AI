export type ResumeSourceType = "USER_UPLOAD" | "MANUAL";

export type ResumeFilePublic = {
  id: number;
  resume_id: number;
  original_filename: string;
  content_type: string;
  file_extension: string;
  file_size: number;
  file_hash: string;
  uploaded_at: string;
  created_at: string;
};

export type ResumePublic = {
  id: number;
  title: string;
  description: string | null;
  source_type: ResumeSourceType;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  files: ResumeFilePublic[];
};

export type ResumeListData = {
  items: ResumePublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type ResumePayload = {
  title: string;
  description?: string | null;
  source_type?: ResumeSourceType;
  is_default?: boolean;
};

export type ResumeExtractionStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "TEXT_NOT_FOUND"
  | "OCR_REQUIRED";

export type ResumePageText = {
  page: number;
  text: string;
  page_break_supported?: boolean;
};

export type ResumeSectionCandidate = {
  section: string;
  confidence: number;
  text: string;
};

export type ResumeFileExtractionPublic = {
  id: number;
  resume_file_id: number;
  extraction_status: ResumeExtractionStatus;
  status: ResumeExtractionStatus;
  raw_text: string | null;
  edited_text: string | null;
  extracted_text: string | null;
  page_texts: ResumePageText[];
  section_candidates: ResumeSectionCandidate[];
  page_count: number;
  character_count: number;
  text_length: number;
  input_hash: string;
  source_file_hash: string;
  parser_version: string;
  is_outdated: boolean;
  is_user_edited: boolean;
  current_run_id: number | null;
  error_code: string | null;
  error_message: string | null;
  extracted_at: string;
  created_at: string;
  updated_at: string;
};

export type ResumeExtractionRunPublic = {
  id: number;
  extraction_id: number | null;
  resume_file_id: number;
  status: ResumeExtractionStatus;
  input_hash: string;
  extractor: string;
  extractor_version: string;
  started_at: string;
  completed_at: string | null;
  error_code: string | null;
  error_message: string | null;
  page_count: number;
  character_count: number;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type ResumeExtractionRunListData = {
  items: ResumeExtractionRunPublic[];
};

export type ResumeAnalysisStatus =
  | "PENDING"
  | "PROCESSING"
  | "COMPLETED"
  | "FAILED"
  | "INVALID_OUTPUT"
  | "PROVIDER_UNAVAILABLE";

export type ResumeAnalysisEvidence = {
  source: "RAW_TEXT" | "EDITED_TEXT" | "SECTION_CANDIDATE" | "USER_PROFILE";
  source_text: string;
  start_offset: number | null;
  end_offset: number | null;
  page_number: number | null;
  section_candidate: string | null;
  extraction_id: number | null;
};

export type ResumeAnalysisStructuredData = {
  summary: string;
  headline: string | null;
  skills: Array<Record<string, unknown> & { name: string; evidence?: ResumeAnalysisEvidence[] }>;
  experiences: Array<Record<string, unknown>>;
  projects: Array<Record<string, unknown>>;
  education: Array<Record<string, unknown>>;
  certifications: Array<Record<string, unknown>>;
  achievements: Array<Record<string, unknown>>;
  awards: Array<Record<string, unknown>>;
  portfolio_links: string[];
  languages: string[];
  contact: Record<string, unknown>;
  other_sections: Array<Record<string, unknown>>;
  keywords: string[];
  warnings: Array<{ code: string; message: string }>;
  confidence: Record<string, number>;
};

export type ResumeAnalysisPublic = {
  id: number;
  resume_id: number;
  resume_file_id: number;
  extraction_id: number;
  user_id: number;
  status: ResumeAnalysisStatus;
  provider: string | null;
  model: string | null;
  prompt_version: string;
  schema_version: string;
  input_hash: string;
  resume_file_hash: string;
  extraction_run_id: number | null;
  input_source: string;
  input_length: number;
  summary: string | null;
  structured_result: ResumeAnalysisStructuredData | null;
  edited_result: ResumeAnalysisStructuredData | null;
  result: ResumeAnalysisStructuredData | null;
  profile_candidates: Array<Record<string, unknown>>;
  is_user_edited: boolean;
  is_outdated: boolean;
  latest_run_id: number | null;
  error_code: string | null;
  error_message: string | null;
  analyzed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ResumeAnalysisRunPublic = {
  id: number;
  analysis_id: number | null;
  resume_id: number;
  resume_file_id: number;
  extraction_id: number;
  user_id: number;
  status: ResumeAnalysisStatus;
  provider: string;
  model: string | null;
  prompt_version: string;
  schema_version: string;
  input_hash: string;
  input_source: string;
  input_length: number;
  started_at: string;
  completed_at: string | null;
  error_code: string | null;
  error_message: string | null;
  result_snapshot: ResumeAnalysisStructuredData | null;
  usage_metadata: Record<string, unknown>;
  raw_response_metadata: Record<string, unknown>;
  created_at: string;
};

export type ResumeAnalysisRunsData = {
  items: ResumeAnalysisRunPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type ResumeProfileCandidateData = {
  items: Array<Record<string, unknown>>;
};
