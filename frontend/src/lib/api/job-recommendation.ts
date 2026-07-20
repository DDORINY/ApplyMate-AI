import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  JobRecommendation,
  JobRecommendationFeedback,
  JobRecommendationFeedbackReason,
  JobRecommendationFeedbackType,
  JobRecommendationGenerateData,
  JobRecommendationGrade,
  JobRecommendationListData,
  JobRecommendationPolicyData,
  JobRecommendationRunIfDueData,
  JobRecommendationSettings,
  JobRecommendationSnapshotListData,
  RecommendationChangeType,
  RecommendationNotificationListData,
  RecommendationNotificationStatus,
} from "@/types/job-recommendation";

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

export type JobRecommendationListParams = {
  page?: number;
  size?: number;
  min_score?: number;
  grade?: JobRecommendationGrade | "";
  change_type?: RecommendationChangeType | "";
  has_blocking_mismatch?: boolean | "";
  keyword?: string;
  include_hidden?: boolean;
  include_outdated?: boolean;
  sort?: "score" | "generated_at" | "job_deadline" | "company_name";
  order?: "asc" | "desc";
};

export async function generateJobRecommendations(payload = {}) {
  return request<JobRecommendationGenerateData>("/recommendations/jobs/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listJobRecommendations(params: JobRecommendationListParams = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      search.set(key, String(value));
    }
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<JobRecommendationListData>(`/recommendations/jobs${suffix}`);
}

export async function getJobRecommendation(recommendationId: number) {
  return request<JobRecommendation>(`/recommendations/jobs/${recommendationId}`);
}

export async function refreshJobRecommendation(recommendationId: number) {
  return request<JobRecommendation>(`/recommendations/jobs/${recommendationId}/refresh`, {
    method: "POST",
  });
}

export async function createJobRecommendationFeedback(
  recommendationId: number,
  payload: {
    feedback_type: JobRecommendationFeedbackType;
    reason_code?: JobRecommendationFeedbackReason | null;
    comment?: string | null;
  },
) {
  return request<JobRecommendationFeedback>(`/recommendations/jobs/${recommendationId}/feedback`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getJobRecommendationPolicy() {
  return request<JobRecommendationPolicyData>("/recommendations/jobs/policy");
}

export async function getJobRecommendationSettings() {
  return request<JobRecommendationSettings>("/recommendations/settings");
}

export async function updateJobRecommendationSettings(payload: Partial<JobRecommendationSettings>) {
  return request<JobRecommendationSettings>("/recommendations/settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function runJobRecommendationsIfDue(payload: { force?: boolean } = {}) {
  return request<JobRecommendationRunIfDueData>("/recommendations/jobs/run-if-due", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listJobRecommendationSnapshots(params: { page?: number; size?: number } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      search.set(key, String(value));
    }
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<JobRecommendationSnapshotListData>(`/recommendations/jobs/snapshots${suffix}`);
}

export async function listRecommendationNotifications(params: { status?: RecommendationNotificationStatus | ""; page?: number; size?: number } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      search.set(key, String(value));
    }
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<RecommendationNotificationListData>(`/recommendation-notifications${suffix}`);
}

export async function updateRecommendationNotification(notificationId: number, status: RecommendationNotificationStatus) {
  return request(`/recommendation-notifications/${notificationId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}
