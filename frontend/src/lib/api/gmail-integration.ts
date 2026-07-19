import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  EmailCandidateApplicationOptionsData,
  EmailCandidateListData,
  EmailCandidatePublic,
  EmailCandidateType,
  EmailSyncRunPublic,
  GmailConnectData,
  GmailIntegrationStatusData,
  GmailSyncResult,
} from "@/types/gmail-integration";

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

export async function getGmailIntegrationStatus() {
  return request<GmailIntegrationStatusData>("/integrations/gmail/status");
}

export async function startGmailConnection() {
  return request<GmailConnectData>("/integrations/gmail/connect", {
    method: "POST",
    body: JSON.stringify({ redirect_path: "/settings/integrations" }),
  });
}

export async function updateGmailIntegrationSettings(payload: {
  sync_enabled?: boolean;
  search_query?: string;
  lookback_days?: number;
}) {
  return request<GmailIntegrationStatusData>("/integrations/gmail/settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function disconnectGmailIntegration() {
  return request<{ disconnected: boolean }>("/integrations/gmail/connection", { method: "DELETE" });
}

export async function syncGmail() {
  return request<GmailSyncResult>("/integrations/gmail/sync", { method: "POST" });
}

export async function listGmailSyncRuns() {
  return request<EmailSyncRunPublic[]>("/integrations/gmail/sync-runs");
}

export async function listEmailCandidates(params: { candidate_type?: EmailCandidateType | ""; status?: string } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) search.set(key, value);
  });
  return request<EmailCandidateListData>(`/email-candidates${search.toString() ? `?${search}` : ""}`);
}

export async function getEmailCandidate(candidateId: number) {
  return request<EmailCandidatePublic>(`/email-candidates/${candidateId}`);
}

export async function approveEmailCandidate(candidateId: number, payload: {
  apply_status_change: boolean;
  create_schedule_event: boolean;
  application_id?: number;
}) {
  return request(`/email-candidates/${candidateId}/approve`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function rejectEmailCandidate(candidateId: number) {
  return request<EmailCandidatePublic>(`/email-candidates/${candidateId}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason: "Rejected by user" }),
  });
}

export async function getEmailCandidateApplicationOptions(candidateId: number) {
  return request<EmailCandidateApplicationOptionsData>(`/email-candidates/${candidateId}/application-options`);
}
