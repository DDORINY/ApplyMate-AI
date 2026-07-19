import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  JobMatchFeedbackListData,
  JobMatchFeedbackPublic,
  JobMatchFeedbackType,
  JobMatchPublic,
  JobMatchRunsData,
} from "@/types/job-match";

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

export async function analyzeJobMatch(
  jobId: number,
  options: { force?: boolean; generate_explanation?: boolean } = {},
) {
  return request<JobMatchPublic>(`/jobs/${jobId}/match`, {
    method: "POST",
    body: JSON.stringify({
      force: options.force ?? false,
      generate_explanation: options.generate_explanation ?? true,
    }),
  });
}

export async function getJobMatch(jobId: number) {
  return request<JobMatchPublic>(`/jobs/${jobId}/match`);
}

export async function deleteJobMatch(jobId: number) {
  return request<{ deleted: boolean }>(`/jobs/${jobId}/match`, { method: "DELETE" });
}

export async function listJobMatchRuns(jobId: number) {
  return request<JobMatchRunsData>(`/jobs/${jobId}/match/runs`);
}

export async function createJobMatchFeedback(
  jobId: number,
  payload: { feedback_type: JobMatchFeedbackType; rating?: number | null; comment?: string | null },
) {
  return request<JobMatchFeedbackPublic>(`/jobs/${jobId}/match/feedback`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listJobMatchFeedback(jobId: number) {
  return request<JobMatchFeedbackListData>(`/jobs/${jobId}/match/feedback`);
}
