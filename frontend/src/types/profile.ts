export type CareerLevel = "ENTRY" | "JUNIOR" | "MID" | "SENIOR" | "CAREER_CHANGE";
export type ProficiencyLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT";
export type EmploymentType =
  | "FULL_TIME"
  | "CONTRACT"
  | "INTERN"
  | "FREELANCE"
  | "PART_TIME"
  | "SELF_EMPLOYED"
  | "OTHER";
export type RemotePreference = "ONSITE" | "HYBRID" | "REMOTE" | "ANY";
export type ExcludedConditionType =
  | "EMPLOYMENT_TYPE"
  | "LOCATION"
  | "COMPANY_SIZE"
  | "REQUIRED_SKILL"
  | "EXCLUDED_KEYWORD"
  | "MINIMUM_EXPERIENCE"
  | "EDUCATION_REQUIREMENT"
  | "OTHER";
export type PortfolioLinkType = "GITHUB" | "NOTION" | "PORTFOLIO" | "BLOG" | "LINKEDIN" | "OTHER";

export type CareerProfile = {
  id: number;
  display_name: string;
  headline: string | null;
  career_level: CareerLevel;
  years_of_experience: number;
  desired_job_title: string;
  introduction: string | null;
};

export type UserSkill = {
  id: number;
  proficiency_level: ProficiencyLevel;
  years_of_experience: number;
  is_primary: boolean;
  skill: {
    id: number;
    name: string;
    normalized_name: string;
    category: string;
  };
};

export type Experience = {
  id: number;
  company_name: string;
  position: string;
  employment_type: EmploymentType;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
  achievements: string | null;
};

export type Project = {
  id: number;
  name: string;
  summary: string | null;
  role: string | null;
  start_date: string;
  end_date: string | null;
  is_ongoing: boolean;
  repository_url: string | null;
  service_url: string | null;
  skills: Array<{ id: number; name: string }>;
};

export type JobPreference = {
  id: number;
  preferred_employment_types: EmploymentType[];
  preferred_locations: string[];
  preferred_company_sizes: string[];
  remote_preference: RemotePreference;
  minimum_salary: number | null;
  desired_roles: string[];
  priority_keywords: string[];
};

export type ExcludedCondition = {
  id: number;
  condition_type: ExcludedConditionType;
  value: string;
  reason: string | null;
  is_active: boolean;
};

export type PortfolioLink = {
  id: number;
  link_type: PortfolioLinkType;
  title: string;
  url: string;
  is_primary: boolean;
  display_order: number;
};
