import { getAccessToken } from "@/lib/auth/token";
import { apiBaseUrl } from "@/lib/env/client";
import type { ApiErrorResponse, ApiResponse } from "@/types/auth";
import type {
  ApplicationDocumentListData,
  ApplicationDocumentPayload,
  ApplicationDocumentPublic,
  ApplicationDocumentSourcePublic,
  ApplicationDocumentStatus,
  ApplicationDocumentType,
  ApplicationDocumentVersionPublic,
  DocumentProviderStatus,
  GenerationRunPublic,
} from "@/types/application-document";

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

export type DocumentListParams = {
  page?: number;
  size?: number;
  document_type?: ApplicationDocumentType | "";
  status?: ApplicationDocumentStatus | "";
  keyword?: string;
  include_archived?: boolean;
};

export async function listApplicationDocuments(params: DocumentListParams = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      search.set(key, String(value));
    }
  });
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return request<ApplicationDocumentListData>(`/documents${suffix}`);
}

export async function createApplicationDocument(payload: ApplicationDocumentPayload) {
  return request<ApplicationDocumentPublic>("/documents", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getApplicationDocument(documentId: number) {
  return request<ApplicationDocumentPublic>(`/documents/${documentId}`);
}

export async function updateApplicationDocument(
  documentId: number,
  payload: Partial<ApplicationDocumentPayload>,
) {
  return request<ApplicationDocumentPublic>(`/documents/${documentId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function archiveApplicationDocument(documentId: number) {
  return request<{ archived: boolean }>(`/documents/${documentId}`, { method: "DELETE" });
}

export async function generateApplicationDocument(
  documentId: number,
  payload: Partial<ApplicationDocumentPayload> = {},
) {
  return request<ApplicationDocumentPublic>(`/documents/${documentId}/generate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function regenerateApplicationDocument(
  documentId: number,
  payload: Partial<ApplicationDocumentPayload> = {},
) {
  return request<ApplicationDocumentPublic>(`/documents/${documentId}/regenerate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listApplicationDocumentVersions(documentId: number) {
  return request<ApplicationDocumentVersionPublic[]>(`/documents/${documentId}/versions`);
}

export async function createApplicationDocumentVersion(
  documentId: number,
  payload: { content: string; change_summary?: string | null },
) {
  return request<ApplicationDocumentVersionPublic>(`/documents/${documentId}/versions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function restoreApplicationDocumentVersion(documentId: number, versionId: number) {
  return request<ApplicationDocumentVersionPublic>(
    `/documents/${documentId}/versions/${versionId}/restore`,
    { method: "POST" },
  );
}

export async function listApplicationDocumentSources(documentId: number) {
  return request<ApplicationDocumentSourcePublic[]>(`/documents/${documentId}/sources`);
}

export async function listApplicationDocumentGenerationRuns(documentId: number) {
  return request<GenerationRunPublic[]>(`/documents/${documentId}/generation-runs`);
}

export async function duplicateApplicationDocument(documentId: number, title?: string) {
  return request<ApplicationDocumentPublic>(`/documents/${documentId}/duplicate`, {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export async function getDocumentProviderStatus() {
  return request<DocumentProviderStatus>("/ai/document-providers");
}
