import type {
  CompanySize,
  JobDeadlineType,
  JobEmploymentType,
  JobPostingStatus,
  JobSourceType,
  JobWorkType,
} from "@/types/job";

export const statusLabels: Record<JobPostingStatus, string> = {
  SAVED: "저장",
  REVIEWING: "검토 중",
  INTERESTED: "관심",
  EXCLUDED: "제외",
  CLOSED: "마감",
};

export const employmentTypeLabels: Record<JobEmploymentType, string> = {
  FULL_TIME: "정규직",
  CONTRACT: "계약직",
  INTERN: "인턴",
  PART_TIME: "파트타임",
  FREELANCE: "프리랜서",
  OTHER: "기타",
  UNKNOWN: "미정",
};

export const workTypeLabels: Record<JobWorkType, string> = {
  ONSITE: "출근",
  HYBRID: "하이브리드",
  REMOTE: "원격",
  UNKNOWN: "미정",
};

export const deadlineTypeLabels: Record<JobDeadlineType, string> = {
  FIXED: "고정 마감",
  UNTIL_FILLED: "채용 시 마감",
  ONGOING: "상시 채용",
  UNKNOWN: "미정",
};

export const sourceTypeLabels: Record<JobSourceType, string> = {
  MANUAL: "직접 입력",
  URL: "URL 등록",
};

export const companySizeLabels: Record<CompanySize, string> = {
  LARGE_ENTERPRISE: "대기업",
  MAJOR_AFFILIATE: "대기업 계열",
  MID_SIZED: "중견기업",
  SMALL_BUSINESS: "중소기업",
  STARTUP: "스타트업",
  PUBLIC_ORGANIZATION: "공공기관",
  UNKNOWN: "미정",
};
