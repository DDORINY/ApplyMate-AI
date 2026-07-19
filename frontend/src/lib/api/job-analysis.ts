import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  AIProviderStatusData,
  JobAnalysisPublic,
  JobAnalysisRunsData,
} from "@/types/job-analysis";

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

export async function getAIProviderStatus() {
  return request<AIProviderStatusData>("/ai/providers");
}

export async function analyzeJob(jobId: number, force = false) {
  return request<JobAnalysisPublic>(`/jobs/${jobId}/analysis`, {
    method: "POST",
    body: JSON.stringify({ force }),
  });
}

export async function getJobAnalysis(jobId: number) {
  return request<JobAnalysisPublic>(`/jobs/${jobId}/analysis`);
}

export async function updateJobAnalysis(
  jobId: number,
  payload: Partial<Pick<JobAnalysisPublic, "summary" | "keywords">>,
) {
  return request<JobAnalysisPublic>(`/jobs/${jobId}/analysis`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteJobAnalysis(jobId: number) {
  return request<{ deleted: boolean }>(`/jobs/${jobId}/analysis`, { method: "DELETE" });
}

export async function listJobAnalysisRuns(jobId: number) {
  return request<JobAnalysisRunsData>(`/jobs/${jobId}/analysis/runs`);
}
