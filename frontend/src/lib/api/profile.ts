import { refreshAccessToken } from "@/lib/api/auth";
import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  CareerProfile,
  ExcludedCondition,
  Experience,
  JobPreference,
  PortfolioLink,
  Project,
  UserSkill,
} from "@/types/profile";

async function parseError(response: Response) {
  try {
    const body = (await response.json()) as ApiErrorResponse;
    return new Error(body.error.message);
  } catch {
    return new Error("요청 처리 중 오류가 발생했습니다.");
  }
}

async function request<TData>(path: string, init: RequestInit = {}, retry = true) {
  const token = getAccessToken();
  if (!token) {
    throw new Error("로그인이 필요합니다.");
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init.headers ?? {}),
    },
  });

  if (response.status === 401 && retry) {
    await refreshAccessToken();
    return request<TData>(path, init, false);
  }

  if (!response.ok) {
    throw await parseError(response);
  }

  return response.json() as Promise<ApiResponse<TData>>;
}

const jsonBody = (payload: unknown) => ({ body: JSON.stringify(payload) });

export const profileApi = {
  getProfile: () => request<CareerProfile>("/profiles/me"),
  saveProfile: async (payload: Partial<CareerProfile>) => {
    try {
      return await request<CareerProfile>("/profiles/me", {
        method: "PATCH",
        ...jsonBody(payload),
      });
    } catch {
      return request<CareerProfile>("/profiles", { method: "POST", ...jsonBody(payload) });
    }
  },
  listSkills: () => request<UserSkill[]>("/profiles/me/skills"),
  addSkill: (payload: unknown) =>
    request<UserSkill>("/profiles/me/skills", { method: "POST", ...jsonBody(payload) }),
  updateSkill: (id: number, payload: unknown) =>
    request<UserSkill>(`/profiles/me/skills/${id}`, { method: "PATCH", ...jsonBody(payload) }),
  deleteSkill: (id: number) =>
    request<{ deleted: boolean }>(`/profiles/me/skills/${id}`, { method: "DELETE" }),
  listExperiences: () => request<Experience[]>("/profiles/me/experiences"),
  addExperience: (payload: unknown) =>
    request<Experience>("/profiles/me/experiences", { method: "POST", ...jsonBody(payload) }),
  updateExperience: (id: number, payload: unknown) =>
    request<Experience>(`/profiles/me/experiences/${id}`, {
      method: "PATCH",
      ...jsonBody(payload),
    }),
  deleteExperience: (id: number) =>
    request<{ deleted: boolean }>(`/profiles/me/experiences/${id}`, { method: "DELETE" }),
  listProjects: () => request<Project[]>("/profiles/me/projects"),
  addProject: (payload: unknown) =>
    request<Project>("/profiles/me/projects", { method: "POST", ...jsonBody(payload) }),
  updateProject: (id: number, payload: unknown) =>
    request<Project>(`/profiles/me/projects/${id}`, { method: "PATCH", ...jsonBody(payload) }),
  deleteProject: (id: number) =>
    request<{ deleted: boolean }>(`/profiles/me/projects/${id}`, { method: "DELETE" }),
  getPreferences: () => request<JobPreference>("/profiles/me/preferences"),
  savePreferences: (payload: unknown) =>
    request<JobPreference>("/profiles/me/preferences", { method: "PUT", ...jsonBody(payload) }),
  patchPreferences: (payload: unknown) =>
    request<JobPreference>("/profiles/me/preferences", { method: "PATCH", ...jsonBody(payload) }),
  listExclusions: () => request<ExcludedCondition[]>("/profiles/me/exclusions"),
  addExclusion: (payload: unknown) =>
    request<ExcludedCondition>("/profiles/me/exclusions", { method: "POST", ...jsonBody(payload) }),
  updateExclusion: (id: number, payload: unknown) =>
    request<ExcludedCondition>(`/profiles/me/exclusions/${id}`, {
      method: "PATCH",
      ...jsonBody(payload),
    }),
  deleteExclusion: (id: number) =>
    request<{ deleted: boolean }>(`/profiles/me/exclusions/${id}`, { method: "DELETE" }),
  listPortfolioLinks: () => request<PortfolioLink[]>("/profiles/me/portfolio-links"),
  addPortfolioLink: (payload: unknown) =>
    request<PortfolioLink>("/profiles/me/portfolio-links", {
      method: "POST",
      ...jsonBody(payload),
    }),
  updatePortfolioLink: (id: number, payload: unknown) =>
    request<PortfolioLink>(`/profiles/me/portfolio-links/${id}`, {
      method: "PATCH",
      ...jsonBody(payload),
    }),
  deletePortfolioLink: (id: number) =>
    request<{ deleted: boolean }>(`/profiles/me/portfolio-links/${id}`, { method: "DELETE" }),
};
