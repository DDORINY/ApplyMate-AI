export type JobMatchStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export type JobMatchGrade = "EXCELLENT" | "GOOD" | "MODERATE" | "LOW" | "VERY_LOW";

export type JobMatchRecommendationStatus =
  | "STRONGLY_RECOMMENDED"
  | "RECOMMENDED"
  | "CONSIDER"
  | "NOT_RECOMMENDED"
  | "INSUFFICIENT_DATA";

export type JobMatchFeedbackType =
  | "ACCURATE"
  | "TOO_HIGH"
  | "TOO_LOW"
  | "MISSING_STRENGTH"
  | "MISSING_RISK"
  | "OTHER";

export type JobMatchScores = {
  role: number;
  skill: number;
  experience: number;
  project: number;
  preference: number;
  risk: number;
};

export type JobMatchPublic = {
  id: number;
  user_id: number;
  job_posting_id: number;
  job_analysis_id: number;
  status: JobMatchStatus;
  total_score: number;
  grade: JobMatchGrade;
  recommendation_status: JobMatchRecommendationStatus;
  scores: JobMatchScores;
  matched_skills: Record<string, unknown>[];
  missing_skills: Record<string, unknown>[];
  matched_projects: Record<string, unknown>[];
  strengths: Record<string, unknown>[];
  gaps: Record<string, unknown>[];
  risks: Record<string, unknown>[];
  recommendation_summary: string | null;
  profile_completeness: number;
  profile_hash: string;
  job_analysis_hash: string;
  calculation_version: string;
  explanation_provider: string;
  is_outdated: boolean;
  calculated_at: string | null;
  created_at: string;
  updated_at: string;
};

export type JobMatchRunPublic = {
  id: number;
  job_match_id: number | null;
  user_id: number;
  job_posting_id: number;
  job_analysis_id: number;
  status: JobMatchStatus;
  profile_hash: string;
  job_analysis_hash: string;
  calculation_version: string;
  total_score: number | null;
  result_snapshot: Record<string, unknown> | null;
  error_code: string | null;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
  created_at: string;
};

export type JobMatchRunsData = {
  items: JobMatchRunPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type JobMatchFeedbackPublic = {
  id: number;
  job_match_id: number;
  user_id: number;
  feedback_type: JobMatchFeedbackType;
  rating: number | null;
  comment: string | null;
  created_at: string;
  updated_at: string;
};

export type JobMatchFeedbackListData = {
  items: JobMatchFeedbackPublic[];
};
