import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  CalendarConnectData,
  CalendarIntegrationStatusData,
  CalendarSettingsPayload,
  CalendarSyncErrorPublic,
  CalendarSyncResult,
  CalendarSyncRunPublic,
  EventSyncStatusData,
  ExternalCalendarPublic,
} from "@/types/calendar-integration";

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as ApiErrorResponse;
    return new Error(body.error.message);
  } catch {
    return new Error("Calendar integration request failed.");
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

export async function getCalendarIntegrationStatus() {
  return request<CalendarIntegrationStatusData>("/integrations/calendar/status");
}

export async function startCalendarConnection() {
  return request<CalendarConnectData>("/integrations/calendar/connect", {
    method: "POST",
    body: JSON.stringify({ redirect_path: "/settings/integrations" }),
  });
}

export async function listExternalCalendars() {
  return request<ExternalCalendarPublic[]>("/integrations/calendar/calendars");
}

export async function updateCalendarIntegrationSettings(payload: CalendarSettingsPayload) {
  return request<CalendarIntegrationStatusData>("/integrations/calendar/settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function disconnectCalendarIntegration() {
  return request<{ disconnected: boolean }>("/integrations/calendar/connection", { method: "DELETE" });
}

export async function syncCalendar() {
  return request<CalendarSyncResult>("/integrations/calendar/sync", { method: "POST" });
}

export async function listCalendarSyncRuns() {
  return request<CalendarSyncRunPublic[]>("/integrations/calendar/sync-runs");
}

export async function listCalendarSyncErrors() {
  return request<CalendarSyncErrorPublic[]>("/integrations/calendar/errors");
}

export async function syncCalendarEvent(eventId: number) {
  return request<CalendarSyncResult>(`/calendar/events/${eventId}/sync`, { method: "POST" });
}

export async function getCalendarEventSyncStatus(eventId: number) {
  return request<EventSyncStatusData>(`/calendar/events/${eventId}/sync-status`);
}
