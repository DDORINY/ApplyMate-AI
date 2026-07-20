import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  NotificationDeliveryPublic,
  NotificationListData,
  NotificationPublic,
  NotificationSettingPublic,
  NotificationStatus,
  NotificationUnreadCountData,
} from "@/types/notification";

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

export async function listNotifications(params: { page?: number; status?: NotificationStatus | "" } = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set("page", String(params.page));
  if (params.status) search.set("status", params.status);
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<NotificationListData>(`/notifications${suffix}`);
}

export async function getNotificationUnreadCount() {
  return request<NotificationUnreadCountData>("/notifications/unread-count");
}

export async function markNotificationRead(notificationId: number) {
  return request<NotificationPublic>(`/notifications/${notificationId}/read`, { method: "PATCH" });
}

export async function dismissNotification(notificationId: number) {
  return request<NotificationPublic>(`/notifications/${notificationId}/dismiss`, { method: "PATCH" });
}

export async function archiveNotification(notificationId: number) {
  return request<NotificationPublic>(`/notifications/${notificationId}/archive`, { method: "PATCH" });
}

export async function readAllNotifications() {
  return request<NotificationUnreadCountData>("/notifications/read-all", { method: "POST" });
}

export async function runDueNotifications() {
  return request<Record<string, unknown>>("/notifications/run-due", { method: "POST" });
}

export async function getNotificationSettings() {
  return request<NotificationSettingPublic>("/notification-settings");
}

export async function updateNotificationSettings(payload: Partial<NotificationSettingPublic>) {
  return request<NotificationSettingPublic>("/notification-settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function listNotificationDeliveries() {
  return request<{ items: NotificationDeliveryPublic[]; total: number }>("/notification-deliveries");
}
