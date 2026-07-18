export type UserStatus = "ACTIVE" | "INACTIVE" | "WITHDRAWN";

export type UserPublic = {
  id: number;
  email: string;
  name: string;
  status: UserStatus;
  email_verified: boolean;
  has_password: boolean;
  last_login_at: string | null;
  created_at: string;
};

export type AuthTokenData = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  user: UserPublic;
};

export type ApiResponse<TData> = {
  success: true;
  data: TData;
  message: string;
};

export type ApiErrorResponse = {
  success: false;
  error: {
    code: string;
    message: string;
  };
};

export type OAuthProvider = "GOOGLE" | "GITHUB";

export type OAuthProviderPublic = {
  provider: OAuthProvider;
  enabled: boolean;
};

export type OAuthProvidersData = {
  providers: OAuthProviderPublic[];
};

export type OAuthAuthorizationData = {
  authorization_url: string;
};

export type OAuthExchangeData = AuthTokenData & {
  redirect_path: string;
  provider: OAuthProvider;
};

export type OAuthAccountPublic = {
  provider: OAuthProvider;
  provider_email: string | null;
  provider_username: string | null;
  provider_display_name: string | null;
  email_verified: boolean;
  created_at: string;
  last_login_at: string | null;
  can_unlink: boolean;
};

export type OAuthAccountsData = {
  accounts: OAuthAccountPublic[];
};

export type SessionPublic = {
  session_id: string;
  device_name: string | null;
  device_info: string | null;
  user_agent: string | null;
  current: boolean;
  created_at: string;
  last_used_at: string | null;
  expires_at: string;
};

export type SessionsData = {
  sessions: SessionPublic[];
};

export type SecurityEventType =
  | "LOGIN_SUCCESS"
  | "LOGIN_FAILED"
  | "LOGOUT"
  | "LOGOUT_ALL"
  | "EMAIL_VERIFICATION_SENT"
  | "EMAIL_VERIFIED"
  | "PASSWORD_RESET_REQUESTED"
  | "PASSWORD_RESET_COMPLETED"
  | "PASSWORD_CHANGED"
  | "PASSWORD_CONFIGURED"
  | "SESSION_REVOKED"
  | "SOCIAL_ACCOUNT_LINKED"
  | "SOCIAL_ACCOUNT_UNLINKED";

export type SecurityEventPublic = {
  id: number;
  event_type: SecurityEventType;
  session_id: string | null;
  event_metadata: Record<string, unknown>;
  created_at: string;
};

export type SecurityEventsData = {
  events: SecurityEventPublic[];
};

export type SessionRevokedData = {
  revoked: boolean;
  revoked_count: number;
};

export type PasswordUpdatedData = {
  updated: boolean;
};
