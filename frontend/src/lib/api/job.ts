import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  JobEmploymentType,
  JobPostingImportData,
  JobPostingListData,
  JobPostingPayload,
  JobPostingPublic,
  JobPostingStatus,
  JobSourceType,
  JobWorkType,
} from "@/types/job";

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

export type JobListParams = {
  page?: number;
  size?: number;
  query?: string;
  status?: JobPostingStatus | "";
  employment_type?: JobEmploymentType | "";
  work_type?: JobWorkType | "";
  is_favorite?: boolean | "";
  source_type?: JobSourceType | "";
  sort?: "created_at" | "updated_at" | "deadline_at" | "title";
  order?: "asc" | "desc";
};

export async function listJobs(params: JobListParams = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      search.set(key, String(value));
    }
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<JobPostingListData>(`/jobs${suffix}`);
}

export async function createJob(payload: JobPostingPayload) {
  return request<JobPostingPublic>("/jobs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function importJobUrl(payload: {
  url: string;
  company_name?: string | null;
  title?: string | null;
  description?: string | null;
}) {
  return request<JobPostingImportData>("/jobs/import-url", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getJob(jobId: number) {
  return request<JobPostingPublic>(`/jobs/${jobId}`);
}

export async function updateJob(jobId: number, payload: Partial<JobPostingPayload>) {
  return request<JobPostingPublic>(`/jobs/${jobId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteJob(jobId: number) {
  return request<{ deleted: boolean }>(`/jobs/${jobId}`, { method: "DELETE" });
}
