import type {
  ApplicationChannel,
  ApplicationNoteType,
  ApplicationPriority,
  ApplicationStatus,
} from "@/types/application";

export const applicationStatusLabels: Record<ApplicationStatus, string> = {
  SAVED: "저장",
  PREPARING: "준비 중",
  APPLIED: "지원 완료",
  DOCUMENT_REVIEW: "서류 검토",
  CODING_TEST: "코딩 테스트",
  ASSIGNMENT: "과제",
  INTERVIEW: "면접",
  FINAL_INTERVIEW: "최종 면접",
  OFFER: "오퍼",
  REJECTED: "불합격",
  WITHDRAWN: "지원 철회",
  CLOSED: "종료",
};

export const applicationChannelLabels: Record<ApplicationChannel, string> = {
  COMPANY_SITE: "기업 채용 사이트",
  JOB_PORTAL: "채용 포털",
  EMAIL: "이메일",
  REFERRAL: "추천",
  RECRUITER: "리크루터",
  TALENT_POOL: "인재풀",
  OFFLINE: "오프라인",
  OTHER: "기타",
};

export const applicationPriorityLabels: Record<ApplicationPriority, string> = {
  LOW: "낮음",
  NORMAL: "보통",
  HIGH: "높음",
  URGENT: "긴급",
};

export const applicationNoteTypeLabels: Record<ApplicationNoteType, string> = {
  GENERAL: "일반",
  CONTACT: "담당자",
  INTERVIEW: "면접",
  DOCUMENT: "문서",
  RESULT: "결과",
  REMINDER: "리마인더",
};

export const applicationStatusOptions = Object.keys(applicationStatusLabels) as ApplicationStatus[];
export const applicationChannelOptions = Object.keys(applicationChannelLabels) as ApplicationChannel[];
export const applicationPriorityOptions = Object.keys(applicationPriorityLabels) as ApplicationPriority[];
export const applicationNoteTypeOptions = Object.keys(applicationNoteTypeLabels) as ApplicationNoteType[];
