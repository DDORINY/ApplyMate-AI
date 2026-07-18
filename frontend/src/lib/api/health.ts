import { apiBaseUrl } from "@/lib/env/client";
import type { ApiResponse, HealthData } from "@/types/health";

export async function fetchHealth(): Promise<ApiResponse<HealthData>> {
  const response = await fetch(`${apiBaseUrl}/health`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch health status");
  }

  return response.json() as Promise<ApiResponse<HealthData>>;
}
