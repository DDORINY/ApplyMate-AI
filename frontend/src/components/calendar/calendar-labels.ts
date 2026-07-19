import type { ScheduleConfidence, ScheduleEventStatus, ScheduleEventType, ScheduleReminderType } from "@/types/calendar";

export const scheduleEventTypeLabels: Record<ScheduleEventType, string> = {
  APPLICATION_DEADLINE: "지원 마감",
  DOCUMENT_RESULT: "서류 결과",
  CODING_TEST: "코딩 테스트",
  ASSIGNMENT_DEADLINE: "과제 마감",
  INTERVIEW: "면접",
  FINAL_INTERVIEW: "최종 면접",
  FINAL_RESULT: "최종 결과",
  OFFER_RESPONSE_DEADLINE: "오퍼 응답 기한",
  USER_EVENT: "개인 일정",
};

export const scheduleEventStatusLabels: Record<ScheduleEventStatus, string> = {
  SCHEDULED: "예정",
  CONFIRMED: "확정",
  COMPLETED: "완료",
  CANCELLED: "취소",
  MISSED: "놓친 일정",
  TENTATIVE: "잠정",
};

export const scheduleConfidenceLabels: Record<ScheduleConfidence, string> = {
  CONFIRMED: "공식 확정",
  ESTIMATED: "추정",
  USER_INPUT: "사용자 입력",
  AI_EXTRACTED: "AI 추출",
  EMAIL_EXTRACTED: "이메일 추출",
};

export const scheduleReminderTypeLabels: Record<ScheduleReminderType, string> = {
  IN_APP: "앱 내 알림",
  EMAIL: "이메일",
  PUSH: "푸시",
};

export const scheduleEventTypeOptions = Object.keys(scheduleEventTypeLabels) as ScheduleEventType[];
export const scheduleEventStatusOptions = Object.keys(scheduleEventStatusLabels) as ScheduleEventStatus[];
export const scheduleConfidenceOptions = Object.keys(scheduleConfidenceLabels) as ScheduleConfidence[];

export function formatScheduleDateTime(value: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ko-KR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function formatRemaining(hours: number | null) {
  if (hours === null) return "-";
  if (hours < 0) return "기한 지남";
  if (hours < 24) return `${hours}시간 남음`;
  return `${Math.floor(hours / 24)}일 남음`;
}
