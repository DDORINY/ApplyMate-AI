export type CompanySize =
  | "LARGE_ENTERPRISE"
  | "MAJOR_AFFILIATE"
  | "MID_SIZED"
  | "SMALL_BUSINESS"
  | "STARTUP"
  | "PUBLIC_ORGANIZATION"
  | "UNKNOWN";

export type JobSourceType = "MANUAL" | "URL";
export type JobPostingStatus = "SAVED" | "REVIEWING" | "INTERESTED" | "EXCLUDED" | "CLOSED";
export type JobEmploymentType =
  | "FULL_TIME"
  | "CONTRACT"
  | "INTERN"
  | "PART_TIME"
  | "FREELANCE"
  | "OTHER"
  | "UNKNOWN";
export type JobWorkType = "ONSITE" | "HYBRID" | "REMOTE" | "UNKNOWN";
export type JobDeadlineType = "FIXED" | "UNTIL_FILLED" | "ONGOING" | "UNKNOWN";

export type CompanyPublic = {
  id: number;
  name: string;
  normalized_name: string;
  website_url: string | null;
  industry: string | null;
  company_size: CompanySize;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type JobPostingPublic = {
  id: number;
  user_id: number;
  company_id: number;
  company: CompanyPublic;
  title: string;
  position: string | null;
  employment_type: JobEmploymentType;
  career_requirement: string | null;
  education_requirement: string | null;
  location: string | null;
  work_type: JobWorkType;
  salary_min: number | null;
  salary_max: number | null;
  salary_text: string | null;
  description: string | null;
  requirements: string | null;
  preferred_qualifications: string | null;
  benefits: string | null;
  recruitment_process: string | null;
  source_type: JobSourceType;
  source_url: string | null;
  source_site: string | null;
  original_content: string | null;
  published_at: string | null;
  deadline_at: string | null;
  deadline_type: JobDeadlineType;
  status: JobPostingStatus;
  is_favorite: boolean;
  notes: string | null;
  collected_at: string | null;
  created_at: string;
  updated_at: string;
};

export type JobPostingListData = {
  items: JobPostingPublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type JobPostingImportData = {
  job: JobPostingPublic;
  import_status: "SUCCESS" | "PARTIAL";
  extracted_fields: string[];
  warnings: string[];
};

export type JobPostingPayload = {
  company_name: string;
  company_website_url?: string | null;
  company_size?: CompanySize;
  title: string;
  position?: string | null;
  employment_type?: JobEmploymentType;
  career_requirement?: string | null;
  education_requirement?: string | null;
  location?: string | null;
  work_type?: JobWorkType;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_text?: string | null;
  description?: string | null;
  requirements?: string | null;
  preferred_qualifications?: string | null;
  benefits?: string | null;
  recruitment_process?: string | null;
  source_type?: JobSourceType;
  source_url?: string | null;
  published_at?: string | null;
  deadline_at?: string | null;
  deadline_type?: JobDeadlineType;
  status?: JobPostingStatus;
  is_favorite?: boolean;
  notes?: string | null;
};
