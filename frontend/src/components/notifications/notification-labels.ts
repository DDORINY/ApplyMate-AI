import type { NotificationEventType, NotificationPriority, NotificationStatus } from "@/types/notification";

export const notificationEventLabels: Record<NotificationEventType, string> = {
  SCHEDULE_REMINDER: "일정 리마인더",
  APPLICATION_DEADLINE: "지원 마감",
  INTERVIEW_REMINDER: "면접 알림",
  ASSESSMENT_DEADLINE: "과제/평가 마감",
  JOB_RECOMMENDATION_NEW: "새 추천 공고",
  JOB_RECOMMENDATION_SCORE_UP: "추천 점수 상승",
  GMAIL_CANDIDATE_CREATED: "메일 후보",
  APPLICATION_STATUS_CHANGED: "지원 상태 변경",
  DOCUMENT_IMPROVEMENT_COMPLETED: "문서 개선 완료",
  DOCUMENT_IMPROVEMENT_FAILED: "문서 개선 실패",
  CALENDAR_SYNC_FAILED: "Calendar 동기화 실패",
  GMAIL_SYNC_FAILED: "Gmail 동기화 실패",
  SYSTEM: "시스템",
};

export const notificationStatusLabels: Record<NotificationStatus, string> = {
  UNREAD: "읽지 않음",
  READ: "읽음",
  DISMISSED: "해제",
  ARCHIVED: "보관",
  EXPIRED: "만료",
};

export const notificationPriorityLabels: Record<NotificationPriority, string> = {
  LOW: "낮음",
  NORMAL: "보통",
  HIGH: "높음",
  URGENT: "긴급",
};
