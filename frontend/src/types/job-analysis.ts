export type JobAnalysisStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export type AIProviderStatusData = {
  active_provider: string;
  enabled: boolean;
  model: string | null;
  analysis_available: boolean;
};

export type JobAnalysisPublic = {
  id: number;
  job_posting_id: number;
  user_id: number;
  status: JobAnalysisStatus;
  schema_version: string;
  prompt_version: string;
  input_hash: string;
  input_length: number;
  summary: string | null;
  position_data: Record<string, unknown> | null;
  responsibilities: Record<string, unknown>[] | null;
  required_qualifications: Record<string, unknown>[] | null;
  preferred_qualifications: Record<string, unknown>[] | null;
  technical_skills: Record<string, unknown>[] | null;
  experience_data: Record<string, unknown> | null;
  education_data: Record<string, unknown> | null;
  work_conditions: Record<string, unknown> | null;
  recruitment_process: string[] | null;
  deadline_data: Record<string, unknown> | null;
  company_values: Record<string, unknown>[] | null;
  keywords: string[] | null;
  warnings: Record<string, unknown>[] | null;
  confidence: Record<string, unknown> | null;
  is_user_edited: boolean;
  is_outdated: boolean;
  analyzed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type JobAnalysisRunPublic = {
  id: number;
  job_posting_id: number;
  job_analysis_id: number | null;
  user_id: number;
  status: JobAnalysisStatus;
  provider: string;
  model: string | null;
  schema_version: string;
  prompt_version: string;
  input_hash: string;
  input_length: number;
  request_id: string | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  latency_ms: number | null;
  error_code: string | null;
  error_message: string | null;
  raw_response: string | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
};

export type JobAnalysisRunsData = {
  items: JobAnalysisRunPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};
