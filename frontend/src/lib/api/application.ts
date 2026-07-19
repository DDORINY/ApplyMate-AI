import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  ApplicationChannel,
  ApplicationListData,
  ApplicationNotePayload,
  ApplicationNotePublic,
  ApplicationOptionsData,
  ApplicationPayload,
  ApplicationPriority,
  ApplicationPublic,
  ApplicationStatus,
  ApplicationStatusHistoryPublic,
} from "@/types/application";

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

export type ApplicationListParams = {
  page?: number;
  size?: number;
  keyword?: string;
  status?: ApplicationStatus | "";
  company?: string;
  job_id?: number | "";
  priority?: ApplicationPriority | "";
  application_channel?: ApplicationChannel | "";
  archived?: boolean;
  sort?: string;
  order?: "asc" | "desc";
};

function toSearch(params: Record<string, unknown>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      search.set(key, String(value));
    }
  });
  return search.toString();
}

export async function listApplications(params: ApplicationListParams = {}) {
  const suffix = toSearch(params);
  return request<ApplicationListData>(`/applications${suffix ? `?${suffix}` : ""}`);
}

export async function getApplication(applicationId: number) {
  return request<ApplicationPublic>(`/applications/${applicationId}`);
}

export async function createApplication(payload: ApplicationPayload) {
  return request<ApplicationPublic>("/applications", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateApplication(applicationId: number, payload: Partial<ApplicationPayload>) {
  return request<ApplicationPublic>(`/applications/${applicationId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function archiveApplication(applicationId: number) {
  return request<{ archived: boolean }>(`/applications/${applicationId}`, { method: "DELETE" });
}

export async function changeApplicationStatus(applicationId: number, status: ApplicationStatus, note?: string) {
  return request<ApplicationPublic>(`/applications/${applicationId}/status`, {
    method: "POST",
    body: JSON.stringify({ status, note }),
  });
}

export async function listApplicationStatusHistory(applicationId: number) {
  return request<ApplicationStatusHistoryPublic[]>(`/applications/${applicationId}/status-history`);
}

export async function listApplicationNotes(applicationId: number) {
  return request<ApplicationNotePublic[]>(`/applications/${applicationId}/notes`);
}

export async function createApplicationNote(applicationId: number, payload: Required<ApplicationNotePayload>) {
  return request<ApplicationNotePublic>(`/applications/${applicationId}/notes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateApplicationNote(
  applicationId: number,
  noteId: number,
  payload: ApplicationNotePayload,
) {
  return request<ApplicationNotePublic>(`/applications/${applicationId}/notes/${noteId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteApplicationNote(applicationId: number, noteId: number) {
  return request<{ deleted: boolean }>(`/applications/${applicationId}/notes/${noteId}`, {
    method: "DELETE",
  });
}

export async function getApplicationOptions() {
  return request<ApplicationOptionsData>("/applications/options");
}
