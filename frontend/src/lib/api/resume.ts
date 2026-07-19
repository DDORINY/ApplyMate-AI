import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  ResumeExtractionRunListData,
  ResumeExtractionRunPublic,
  ResumeFileExtractionPublic,
  ResumeFilePublic,
  ResumeListData,
  ResumePayload,
  ResumePublic,
} from "@/types/resume";

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as ApiErrorResponse;
    return new Error(body.error.message);
  } catch {
    return new Error("요청 처리 중 오류가 발생했습니다.");
  }
}

function authHeaders(json = true): Record<string, string> {
  const token = getAccessToken();
  if (!token) {
    throw new Error("로그인이 필요합니다.");
  }
  const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
  if (json) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
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

export async function listResumes(params: { page?: number; size?: number } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      search.set(key, String(value));
    }
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<ResumeListData>(`/resumes${suffix}`);
}

export async function createResume(payload: ResumePayload) {
  return request<ResumePublic>("/resumes", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getResume(resumeId: number) {
  return request<ResumePublic>(`/resumes/${resumeId}`);
}

export async function updateResume(resumeId: number, payload: Partial<ResumePayload>) {
  return request<ResumePublic>(`/resumes/${resumeId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function setDefaultResume(resumeId: number) {
  return request<ResumePublic>(`/resumes/${resumeId}/default`, { method: "POST" });
}

export async function deleteResume(resumeId: number) {
  return request<{ deleted: boolean }>(`/resumes/${resumeId}`, { method: "DELETE" });
}

export async function uploadResumeFile(resumeId: number, file: File) {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${apiBaseUrl}/resumes/${resumeId}/files`, {
    method: "POST",
    credentials: "include",
    headers: authHeaders(false),
    body,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json() as Promise<ApiResponse<ResumeFilePublic>>;
}

export async function deleteResumeFile(resumeId: number, fileId: number) {
  return request<{ deleted: boolean }>(`/resumes/${resumeId}/files/${fileId}`, { method: "DELETE" });
}

export async function downloadResumeFile(resumeId: number, fileId: number, filename: string) {
  const response = await fetch(`${apiBaseUrl}/resumes/${resumeId}/files/${fileId}/download`, {
    credentials: "include",
    headers: authHeaders(false),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}

export async function extractResumeFile(resumeId: number, fileId: number) {
  return request<ResumeFileExtractionPublic>(`/resumes/${resumeId}/files/${fileId}/extraction`, {
    method: "POST",
  });
}

export async function getResumeFileExtraction(resumeId: number, fileId: number) {
  return request<ResumeFileExtractionPublic>(`/resumes/${resumeId}/files/${fileId}/extraction`);
}

export async function updateResumeFileExtraction(resumeId: number, fileId: number, editedText: string) {
  return request<ResumeFileExtractionPublic>(`/resumes/${resumeId}/files/${fileId}/extraction`, {
    method: "PATCH",
    body: JSON.stringify({ edited_text: editedText }),
  });
}

export async function retryResumeFileExtraction(resumeId: number, fileId: number) {
  return request<ResumeFileExtractionPublic>(`/resumes/${resumeId}/files/${fileId}/extraction/retry`, {
    method: "POST",
  });
}

export async function listResumeFileExtractionRuns(resumeId: number, fileId: number) {
  return request<ResumeExtractionRunListData>(`/resumes/${resumeId}/files/${fileId}/extraction/runs`);
}

export async function getResumeFileExtractionRun(resumeId: number, fileId: number, runId: number) {
  return request<ResumeExtractionRunPublic>(`/resumes/${resumeId}/files/${fileId}/extraction/runs/${runId}`);
}
