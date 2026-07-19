import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  ScheduleConfidence,
  ScheduleConflictItem,
  ScheduleEventListData,
  ScheduleEventPayload,
  ScheduleEventPublic,
  ScheduleEventStatus,
  ScheduleEventType,
  ScheduleEventHistoryPublic,
  ScheduleOptionsData,
  ScheduleReminderPayload,
  ScheduleReminderPublic,
  ScheduleUpcomingData,
} from "@/types/calendar";

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as ApiErrorResponse;
    return new Error(body.error.message);
  } catch {
    return new Error("요청 처리 중 오류가 발생했습니다.");
  }
}

function authHeaders() {
  const token = getAccessToken();
  if (!token) {
    throw new Error("로그인이 필요합니다.");
  }
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

async function request<TData>(path: string, init: RequestInit = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...authHeaders(),
      ...(init.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json() as Promise<ApiResponse<TData>>;
}

function toSearch(params: Record<string, unknown>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export type CalendarEventListParams = {
  page?: number;
  size?: number;
  start_from?: string;
  start_to?: string;
  event_type?: ScheduleEventType | "";
  status?: ScheduleEventStatus | "";
  confidence?: ScheduleConfidence | "";
  application_id?: number | "";
  job_id?: number | "";
  has_reminder?: boolean | "";
  include_archived?: boolean;
  keyword?: string;
  sort?: string;
  order?: "asc" | "desc";
};

export async function listCalendarEvents(params: CalendarEventListParams = {}) {
  const suffix = toSearch(params);
  return request<ScheduleEventListData>(`/calendar/events${suffix ? `?${suffix}` : ""}`);
}

export async function getCalendarEvent(eventId: number) {
  return request<ScheduleEventPublic>(`/calendar/events/${eventId}`);
}

export async function createCalendarEvent(payload: ScheduleEventPayload) {
  return request<ScheduleEventPublic>("/calendar/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateCalendarEvent(eventId: number, payload: Partial<ScheduleEventPayload>) {
  return request<ScheduleEventPublic>(`/calendar/events/${eventId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function archiveCalendarEvent(eventId: number) {
  return request<{ archived: boolean }>(`/calendar/events/${eventId}`, { method: "DELETE" });
}

export async function changeCalendarEventStatus(eventId: number, status: ScheduleEventStatus) {
  return request<ScheduleEventPublic>(`/calendar/events/${eventId}/status`, {
    method: "POST",
    body: JSON.stringify({ status }),
  });
}

export async function listCalendarEventHistory(eventId: number) {
  return request<ScheduleEventHistoryPublic[]>(`/calendar/events/${eventId}/history`);
}

export async function listCalendarEventReminders(eventId: number) {
  return request<ScheduleReminderPublic[]>(`/calendar/events/${eventId}/reminders`);
}

export async function createCalendarEventReminder(eventId: number, payload: ScheduleReminderPayload) {
  return request<ScheduleReminderPublic>(`/calendar/events/${eventId}/reminders`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deleteCalendarEventReminder(eventId: number, reminderId: number) {
  return request<{ deleted: boolean }>(`/calendar/events/${eventId}/reminders/${reminderId}`, {
    method: "DELETE",
  });
}

export async function listCalendarConflicts(startAt: string, endAt: string, excludeEventId?: number) {
  const suffix = toSearch({ start_at: startAt, end_at: endAt, exclude_event_id: excludeEventId });
  return request<ScheduleConflictItem[]>(`/calendar/conflicts?${suffix}`);
}

export async function listUpcomingCalendarEvents(hours = 168, size = 20) {
  return request<ScheduleUpcomingData>(`/calendar/upcoming?hours=${hours}&size=${size}`);
}

export async function getCalendarOptions() {
  return request<ScheduleOptionsData>("/calendar/options");
}
