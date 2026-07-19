export type DashboardPeriod = "7d" | "30d" | "90d" | "all" | "custom";

export type DashboardSummary = {
  total_applications: number;
  preparing_applications: number;
  in_progress_applications: number;
  interview_applications: number;
  offer_applications: number;
  rejected_applications: number;
  withdrawn_applications: number;
  closed_applications: number;
  week_events: number;
  upcoming_deadlines: number;
  due_soon_jobs: number;
};

export type DashboardApplicationStatusCount = {
  group: string;
  label: string;
  count: number;
  percentage: number;
  statuses: string[];
};

export type DashboardApplicationActivity = {
  new_applications: number;
  status_changes: number;
  period_start: string | null;
  period_end: string | null;
};

export type DashboardScheduleItem = {
  id: number;
  title: string;
  event_type: string;
  status: string;
  effective_status: string;
  confidence: string;
  start_at: string;
  end_at: string;
  all_day: boolean;
  timezone: string;
  application_id: number | null;
  job_id: number | null;
  company_name: string | null;
  job_title: string | null;
  location: string | null;
  online_url: string | null;
  has_conflict: boolean;
  hours_remaining: number | null;
};

export type DashboardDeadlineItem = {
  kind: "SCHEDULE" | "JOB";
  id: number;
  title: string;
  due_at: string;
  hours_remaining: number | null;
  company_name: string | null;
  job_title: string | null;
  status: string | null;
  confidence: string | null;
  link_path: string;
};

export type DashboardPreparingApplication = {
  id: number;
  company_name: string | null;
  job_title: string | null;
  status: string;
  priority: string;
  planned_apply_at: string | null;
  resume_id: number | null;
  application_document_id: number | null;
  hours_until_planned_apply: number | null;
  link_path: string;
};

export type DashboardRecentJobAnalysis = {
  id: number;
  job_id: number;
  company_name: string | null;
  job_title: string | null;
  status: string;
  provider: string | null;
  summary: string | null;
  technical_skills: string[];
  is_outdated: boolean;
  updated_at: string;
  link_path: string;
};

export type DashboardRecentMatch = {
  id: number;
  job_id: number;
  company_name: string | null;
  job_title: string | null;
  status: string;
  total_score: number;
  grade: string;
  recommendation_status: string;
  strengths: string[];
  gaps: string[];
  updated_at: string;
  link_path: string;
};

export type DashboardRecentResumeAnalysis = {
  id: number;
  resume_id: number;
  resume_file_id: number;
  resume_title: string | null;
  filename: string | null;
  status: string;
  provider: string | null;
  summary: string | null;
  skills_count: number;
  experiences_count: number;
  is_outdated: boolean;
  updated_at: string;
  link_path: string;
};

export type DashboardRecentDocument = {
  id: number;
  title: string;
  document_type: string;
  status: string;
  company_name: string | null;
  job_title: string | null;
  current_version_number: number | null;
  updated_at: string;
  link_path: string;
};

export type DashboardActivityItem = {
  id: string;
  activity_type: string;
  title: string;
  occurred_at: string;
  link_path: string | null;
  metadata: Record<string, unknown>;
};

export type DashboardData = {
  summary: DashboardSummary;
  application_status_counts: DashboardApplicationStatusCount[];
  application_activity: DashboardApplicationActivity;
  today_events: DashboardScheduleItem[];
  week_events: DashboardScheduleItem[];
  upcoming_deadlines: DashboardDeadlineItem[];
  due_soon_jobs: DashboardDeadlineItem[];
  preparing_applications: DashboardPreparingApplication[];
  recent_job_analyses: DashboardRecentJobAnalysis[];
  recent_matches: DashboardRecentMatch[];
  recent_resume_analyses: DashboardRecentResumeAnalysis[];
  recent_documents: DashboardRecentDocument[];
  recent_activities: DashboardActivityItem[];
  generated_at: string;
  timezone: string;
  period: DashboardPeriod;
  period_start: string | null;
  period_end: string | null;
};
