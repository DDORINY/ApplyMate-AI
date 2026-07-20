export type JobRecommendationGrade = "EXCELLENT" | "GOOD" | "POSSIBLE" | "LOW" | "BLOCKED";
export type JobRecommendationStatus = "ACTIVE" | "OUTDATED" | "HIDDEN" | "ARCHIVED";
export type JobRecommendationType = "RULE_BASED";
export type JobRecommendationFeedbackType = "INTERESTED" | "NOT_INTERESTED" | "HIDDEN" | "APPLIED" | "SAVED_FOR_LATER";
export type RecommendationRunFrequency = "MANUAL" | "DAILY" | "WEEKLY";
export type RecommendationChangeType = "NEW" | "UNCHANGED" | "SCORE_UP" | "SCORE_DOWN" | "GRADE_UP" | "GRADE_DOWN" | "REMOVED" | "OUTDATED";
export type RecommendationConfidence = "HIGH" | "MEDIUM" | "LOW";
export type RecommendationNotificationStatus = "PENDING" | "READ" | "DISMISSED" | "EXPIRED";
export type RecommendationNotificationType =
  | "NEW_HIGH_SCORE_RECOMMENDATION"
  | "RECOMMENDATION_SCORE_INCREASED"
  | "RECOMMENDATION_GRADE_INCREASED"
  | "APPLICATION_DEADLINE_APPROACHING"
  | "RECOMMENDATION_BECAME_OUTDATED";
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
  latest_change_type: RecommendationChangeType | null;
  previous_score: number | null;
  score_delta: number | null;
  previous_grade: string | null;
  rank: number | null;
  rank_delta: number | null;
  missing_job_fields: string[];
  data_completeness_score: number | null;
  recommendation_confidence: RecommendationConfidence | null;
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

export type JobRecommendationSettings = {
  id: number;
  user_id: number;
  enabled: boolean;
  frequency: RecommendationRunFrequency;
  preferred_run_hour: number;
  timezone: string;
  minimum_score: number;
  include_jobs_without_analysis: boolean;
  exclude_applied_jobs: boolean;
  exclude_hidden_jobs: boolean;
  notify_new_recommendations: boolean;
  notify_score_changes: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  created_at: string;
  updated_at: string;
};

export type JobRecommendationRunIfDueData = {
  executed: boolean;
  skip_reason: string | null;
  run_id: number | null;
  snapshot_id: number | null;
  recommended_count: number;
  new_count: number;
  changed_count: number;
  removed_count: number;
  next_run_at: string | null;
  message: string;
};

export type JobRecommendationSnapshotItem = {
  id: number;
  snapshot_id: number;
  recommendation_id: number | null;
  job_id: number;
  score: number;
  grade: string;
  rank: number;
  blocking_mismatch: boolean;
  change_type: RecommendationChangeType;
  previous_score: number | null;
  score_delta: number | null;
  previous_grade: string | null;
  rank_delta: number | null;
  reason_summary: string[];
  missing_job_fields: string[];
  data_completeness_score: number;
  recommendation_confidence: RecommendationConfidence;
  created_at: string;
};

export type JobRecommendationSnapshot = {
  id: number;
  user_id: number;
  run_id: number;
  profile_hash: string;
  policy_version: string;
  input_job_count: number;
  recommended_count: number;
  new_count: number;
  changed_count: number;
  removed_count: number;
  generated_at: string;
  created_at: string;
  items: JobRecommendationSnapshotItem[];
};

export type JobRecommendationSnapshotListData = {
  items: JobRecommendationSnapshot[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type RecommendationNotification = {
  id: number;
  user_id: number;
  recommendation_id: number | null;
  snapshot_id: number;
  snapshot_item_id: number | null;
  notification_type: RecommendationNotificationType;
  status: RecommendationNotificationStatus;
  title: string;
  message: string;
  payload: Record<string, unknown> | null;
  expires_at: string | null;
  read_at: string | null;
  dismissed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type RecommendationNotificationListData = {
  items: RecommendationNotification[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};
