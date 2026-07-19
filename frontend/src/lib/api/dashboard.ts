import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type { DashboardData, DashboardPeriod } from "@/types/dashboard";

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as ApiErrorResponse;
    return new Error(body.error.message);
  } catch {
    return new Error("대시보드 정보를 불러오지 못했습니다.");
  }
}

function authHeaders() {
  const token = getAccessToken();
  if (!token) {
    throw new Error("로그인이 필요합니다.");
  }
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
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

export type DashboardParams = {
  period?: DashboardPeriod;
  start_date?: string;
  end_date?: string;
  timezone?: string;
  recent_limit?: number;
};

export async function getDashboard(params: DashboardParams = {}) {
  const suffix = toSearch(params);
  const response = await fetch(`${apiBaseUrl}/dashboard${suffix ? `?${suffix}` : ""}`, {
    credentials: "include",
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json() as Promise<ApiResponse<DashboardData>>;
}
