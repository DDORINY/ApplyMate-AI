import { apiBaseUrl } from "@/lib/env/client";
import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/auth/token";
import type { ApiErrorResponse, ApiResponse, AuthTokenData, UserPublic } from "@/types/auth";

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as ApiErrorResponse;
    return new Error(body.error.message);
  } catch {
    return new Error("요청 처리 중 오류가 발생했습니다.");
  }
}

async function request<TData>(path: string, init: RequestInit = {}): Promise<ApiResponse<TData>> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  return response.json() as Promise<ApiResponse<TData>>;
}

export async function signup(payload: { name: string; email: string; password: string }) {
  return request<UserPublic>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function login(payload: { email: string; password: string }) {
  const response = await request<AuthTokenData>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setAccessToken(response.data.access_token);
  return response;
}

export async function refreshAccessToken() {
  const response = await request<AuthTokenData>("/auth/refresh", { method: "POST" });
  setAccessToken(response.data.access_token);
  return response;
}

export async function logout() {
  try {
    return await request<{ logged_out: boolean }>("/auth/logout", { method: "POST" });
  } finally {
    clearAccessToken();
  }
}

export async function me() {
  const token = getAccessToken();
  if (!token) {
    throw new Error("로그인이 필요합니다.");
  }

  try {
    return await request<UserPublic>("/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    await refreshAccessToken();
    const refreshedToken = getAccessToken();
    if (!refreshedToken) {
      throw error;
    }
    return request<UserPublic>("/auth/me", {
      headers: {
        Authorization: `Bearer ${refreshedToken}`,
      },
    });
  }
}
