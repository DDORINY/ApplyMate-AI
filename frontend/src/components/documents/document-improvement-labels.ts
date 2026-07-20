import type { DocumentImprovementRiskLevel, DocumentImprovementRunStatus, DocumentImprovementType } from "@/types/document-improvement";

export const documentImprovementTypeLabels: Record<DocumentImprovementType, string> = {
  CLARITY: "명확성",
  CONCISENESS: "간결화",
  PROFESSIONAL_TONE: "전문적 톤",
  JOB_ALIGNMENT: "직무 적합도",
  COMPANY_ALIGNMENT: "기업 인재상 연결",
  SKILL_EMPHASIS: "기술 강조",
  EXPERIENCE_EMPHASIS: "경력 강조",
  PROJECT_EMPHASIS: "프로젝트 강조",
  ACHIEVEMENT_EMPHASIS: "성과 강조",
  STRUCTURE: "구조 정리",
  GRAMMAR: "문법 교정",
  LENGTH_REDUCTION: "분량 축소",
  LENGTH_EXPANSION: "분량 확장",
  CUSTOM: "직접 요청",
};

export const documentImprovementStatusLabels: Record<DocumentImprovementRunStatus, string> = {
  PENDING: "대기",
  PROCESSING: "처리 중",
  COMPLETED: "완료",
  FAILED: "실패",
  INVALID_OUTPUT: "응답 오류",
  REVIEW_REQUIRED: "검토 필요",
  APPLIED: "적용 완료",
  REJECTED: "거절",
};

export const documentImprovementRiskLabels: Record<DocumentImprovementRiskLevel, string> = {
  LOW: "낮음",
  MEDIUM: "중간",
  HIGH: "높음",
};
