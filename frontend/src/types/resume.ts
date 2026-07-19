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
