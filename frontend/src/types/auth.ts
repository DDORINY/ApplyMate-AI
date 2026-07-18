export type UserStatus = "ACTIVE" | "INACTIVE" | "WITHDRAWN";

export type UserPublic = {
  id: number;
  email: string;
  name: string;
  status: UserStatus;
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
