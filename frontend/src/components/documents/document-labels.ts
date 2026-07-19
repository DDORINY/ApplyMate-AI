import type {
  ApplicationDocumentStatus,
  ApplicationDocumentTone,
  ApplicationDocumentType,
} from "@/types/application-document";

export const documentTypeLabels: Record<ApplicationDocumentType, string> = {
  MOTIVATION: "지원동기",
  JOB_COMPETENCY: "직무 역량",
  SELF_INTRODUCTION: "자기소개",
  PROJECT_EXPERIENCE: "프로젝트 경험",
  CAREER_EXPERIENCE: "경력 경험",
  FUTURE_PLAN: "입사 후 포부",
  FREE_FORM: "자유 문항",
  CUSTOM_QUESTION: "사용자 문항",
};

export const documentStatusLabels: Record<ApplicationDocumentStatus, string> = {
  DRAFT: "초안 전",
  GENERATING: "생성 중",
  COMPLETED: "완료",
  FAILED: "실패",
  REVIEW_REQUIRED: "검토 필요",
  ARCHIVED: "보관됨",
};

export const documentToneLabels: Record<ApplicationDocumentTone, string> = {
  PROFESSIONAL: "전문적으로",
  CONCISE: "간결하게",
  CONFIDENT: "자신감 있게",
  HUMBLE: "겸손하게",
  TECHNICAL: "기술 중심",
  STORYTELLING: "스토리텔링",
};
