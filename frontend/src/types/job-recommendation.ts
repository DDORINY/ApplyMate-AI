export type JobRecommendationGrade = "EXCELLENT" | "GOOD" | "POSSIBLE" | "LOW" | "BLOCKED";
export type JobRecommendationStatus = "ACTIVE" | "OUTDATED" | "HIDDEN" | "ARCHIVED";
export type JobRecommendationType = "RULE_BASED";
export type JobRecommendationFeedbackType = "INTERESTED" | "NOT_INTERESTED" | "HIDDEN" | "APPLIED" | "SAVED_FOR_LATER";
export type JobRecommendationFeedbackReason =
  | "LOCATION"
  | "SALARY"
  | "ROLE"
  | "TECH_STACK"
  | "EXPERIENCE"
  | "EMPLOYMENT_TYPE"
  | "COMPANY"
  | "OTHER";

export type JobRecommendationReason = {
  id: number;
  reason_type: string;
  requirement_type: string;
  label: string;
  normalized_value: string | null;
  match_status: "MATCHED" | "MISSING" | "UNKNOWN" | "NOT_APPLICABLE";
  weight: number;
  score_delta: number;
  severity: "REQUIRED" | "PREFERRED" | "INFO";
  evidence: string | null;
  created_at: string;
};

export type JobRecommendationFeedback = {
  id: number;
  user_id: number;
  recommendation_id: number;
  feedback_type: JobRecommendationFeedbackType;
  reason_code: JobRecommendationFeedbackReason | null;
  comment: string | null;
  created_at: string;
  updated_at: string;
};

export type JobRecommendationJobSummary = {
  id: number;
  title: string;
  position: string | null;
  company_name: string;
  employment_type: string;
  location: string | null;
  deadline_at: string | null;
  status: string;
};

export type JobRecommendation = {
  id: number;
  user_id: number;
  job_id: number;
  run_id: number;
  score: number;
  grade: JobRecommendationGrade;
  recommendation_type: JobRecommendationType;
  has_blocking_mismatch: boolean;
  matched_count: number;
  missing_count: number;
  unknown_count: number;
  policy_version: string;
  score_breakdown: Record<string, number>;
  input_snapshot: Record<string, unknown>;
  missing_profile_fields: string[];
  outdated: boolean;
  status: JobRecommendationStatus;
  generated_at: string;
  created_at: string;
  updated_at: string;
  job: JobRecommendationJobSummary;
  reasons: JobRecommendationReason[];
  feedback: JobRecommendationFeedback | null;
};

export type JobRecommendationListData = {
  items: JobRecommendation[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type JobRecommendationGenerateData = {
  run_id: number;
  status: "PROCESSING" | "COMPLETED" | "FAILED";
  policy_version: string;
  input_job_count: number;
  recommended_count: number;
  excluded_count: number;
  failed_count: number;
};

export type JobRecommendationPolicyData = {
  recommendation_type: JobRecommendationType;
  policy_version: string;
  score_range: string;
  weights: Record<string, number>;
  grades: Record<string, string>;
  note: string;
};
