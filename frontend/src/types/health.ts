export type ApiResponse<TData> = {
  success: true;
  data: TData;
  message: string;
};

export type HealthData = {
  status: string;
  database: string;
  redis: string;
};
