export type ResumeSourceType = "USER_UPLOAD" | "MANUAL";

export type ResumeFilePublic = {
  id: number;
  resume_id: number;
  original_filename: string;
  content_type: string;
  file_extension: string;
  file_size: number;
  file_hash: string;
  uploaded_at: string;
  created_at: string;
};

export type ResumePublic = {
  id: number;
  title: string;
  description: string | null;
  source_type: ResumeSourceType;
  is_default: boolean;
  created_at: string;
  updated_at: string;
  files: ResumeFilePublic[];
};

export type ResumeListData = {
  items: ResumePublic[];
  page: number;
  size: number;
  total: number;
  total_pages: number;
};

export type ResumePayload = {
  title: string;
  description?: string | null;
  source_type?: ResumeSourceType;
  is_default?: boolean;
};
