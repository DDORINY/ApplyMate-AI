export type UserStatus = "ACTIVE" | "INACTIVE" | "WITHDRAWN";

export type UserPublic = {
  id: number;
  email: string;
  name: string;
  status: UserStatus;
  email_verified: boolean;
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
