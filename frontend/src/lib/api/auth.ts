import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type {
  ApiErrorResponse,
  ApiResponse,
  AuthTokenData,
  OAuthAccountsData,
  OAuthAuthorizationData,
  OAuthExchangeData,
  OAuthProvider,
  OAuthProvidersData,
  PasswordUpdatedData,
  SecurityEventsData,
  SessionRevokedData,
  SessionsData,
  UserPublic,
} from "@/types/auth";

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

function withAccessToken(init: RequestInit = {}) {
  const token = getAccessToken();
  if (!token) {
    throw new Error("로그인이 필요합니다.");
  }

  return {
    ...init,
    headers: {
      ...(init.headers ?? {}),
      Authorization: `Bearer ${token}`,
    },
  };
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
  try {
    return await request<UserPublic>("/auth/me", withAccessToken());
  } catch {
    await refreshAccessToken();
    return request<UserPublic>("/auth/me", withAccessToken());
  }
}

export async function getOAuthProviders() {
  return request<OAuthProvidersData>("/auth/oauth/providers");
}

export async function startOAuth(provider: OAuthProvider, redirectPath = "/me") {
  const params = new URLSearchParams({ redirect_path: redirectPath });
  return request<OAuthAuthorizationData>(
    `/auth/oauth/${provider.toLowerCase()}/authorize?${params.toString()}`,
  );
}

export async function exchangeOAuthTicket(ticket: string) {
  const response = await request<OAuthExchangeData>("/auth/oauth/exchange", {
    method: "POST",
    body: JSON.stringify({ ticket }),
  });
  setAccessToken(response.data.access_token);
  return response;
}

export async function getOAuthAccounts() {
  return request<OAuthAccountsData>("/auth/oauth/accounts", withAccessToken());
}

export async function startOAuthLink(provider: OAuthProvider, redirectPath = "/settings/accounts") {
  const params = new URLSearchParams({ redirect_path: redirectPath });
  return request<OAuthAuthorizationData>(
    `/auth/oauth/${provider.toLowerCase()}/link/authorize?${params.toString()}`,
    withAccessToken(),
  );
}

export async function unlinkOAuthAccount(provider: OAuthProvider) {
  return request<{ unlinked: boolean }>(
    `/auth/oauth/accounts/${provider.toLowerCase()}`,
    withAccessToken({ method: "DELETE" }),
  );
}

export async function sendEmailVerification() {
  return request<{ sent: boolean; email: string }>(
    "/auth/email-verification/send",
    withAccessToken({ method: "POST" }),
  );
}

export async function verifyEmail(token: string) {
  return request<UserPublic>("/auth/email-verification/verify", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export async function forgotPassword(email: string) {
  return request<{ accepted: boolean }>("/auth/password/forgot", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(payload: {
  token: string;
  new_password: string;
  new_password_confirm: string;
}) {
  const response = await request<PasswordUpdatedData>("/auth/password/reset", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  clearAccessToken();
  return response;
}

export async function changePassword(payload: {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}) {
  return request<PasswordUpdatedData>(
    "/auth/password/change",
    withAccessToken({
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function setPassword(payload: {
  new_password: string;
  new_password_confirm: string;
}) {
  return request<PasswordUpdatedData>(
    "/auth/password/set",
    withAccessToken({
      method: "POST",
      body: JSON.stringify(payload),
    }),
  );
}

export async function getSessions() {
  return request<SessionsData>("/auth/sessions", withAccessToken());
}

export async function revokeSession(sessionId: string) {
  return request<SessionRevokedData>(
    `/auth/sessions/${sessionId}`,
    withAccessToken({ method: "DELETE" }),
  );
}

export async function revokeOtherSessions() {
  return request<SessionRevokedData>(
    "/auth/sessions/others",
    withAccessToken({ method: "DELETE" }),
  );
}

export async function revokeAllSessions() {
  try {
    return await request<SessionRevokedData>(
      "/auth/sessions",
      withAccessToken({ method: "DELETE" }),
    );
  } finally {
    clearAccessToken();
  }
}

export async function getSecurityEvents() {
  return request<SecurityEventsData>("/auth/security-events", withAccessToken());
}
