"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  deleteResume,
  deleteResumeFile,
  downloadResumeFile,
  getResume,
  setDefaultResume,
  updateResume,
  uploadResumeFile,
} from "@/lib/api/resume";

export function ResumeDetailPanel({ resumeId }: { resumeId: number }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const resumeQuery = useQuery({
    queryKey: ["resume", resumeId],
    queryFn: () => getResume(resumeId),
    retry: false,
  });

  useEffect(() => {
    if (resumeQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [resumeQuery.error, router]);

  useEffect(() => {
    const resume = resumeQuery.data?.data;
    if (resume) {
      setTitle(resume.title);
      setDescription(resume.description ?? "");
    }
  }, [resumeQuery.data]);

  const updateMutation = useMutation({
    mutationFn: () => updateResume(resumeId, { title, description: description || null }),
    onSuccess: (response) => queryClient.setQueryData(["resume", resumeId], response),
  });
  const defaultMutation = useMutation({
    mutationFn: () => setDefaultResume(resumeId),
    onSuccess: (response) => {
      queryClient.setQueryData(["resume", resumeId], response);
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file) {
        throw new Error("업로드할 파일을 선택해 주세요.");
      }
      return uploadResumeFile(resumeId, file);
    },
    onSuccess: () => {
      setFile(null);
      queryClient.invalidateQueries({ queryKey: ["resume", resumeId] });
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
  const deleteFileMutation = useMutation({
    mutationFn: (fileId: number) => deleteResumeFile(resumeId, fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume", resumeId] });
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });
  const deleteMutation = useMutation({
    mutationFn: () => deleteResume(resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      router.push("/resumes");
    },
  });

  const resume = resumeQuery.data?.data;
  if (resumeQuery.isLoading) {
    return <div className="panel max-w-none">이력서를 불러오는 중입니다.</div>;
  }
  if (resumeQuery.error) {
    return <div className="panel max-w-none text-rose-700">{resumeQuery.error.message}</div>;
  }
  if (!resume) {
    return <div className="panel max-w-none">이력서를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link className="button-secondary" href="/resumes">
          목록으로
        </Link>
        <button
          className="button-primary"
          type="button"
          disabled={defaultMutation.isPending || resume.is_default}
          onClick={() => defaultMutation.mutate()}
        >
          {resume.is_default ? "기본 이력서" : "기본으로 설정"}
        </button>
      </div>

      <section className="panel max-w-none">
        <p className="text-sm font-semibold text-sky-700">ApplyMate AI v0.3.0</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">{resume.title}</h1>
        <p className="mt-2 text-slate-600">{resume.description ?? "설명 없음"}</p>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-xl font-semibold text-slate-950">이력서 정보</h2>
        <div className="mt-5 grid gap-4">
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            제목
            <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} />
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            설명
            <textarea className="input min-h-28" value={description} onChange={(event) => setDescription(event.target.value)} />
          </label>
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button className="button-primary" type="button" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
            저장
          </button>
          <button
            className="button-secondary border-rose-200 text-rose-700"
            type="button"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (window.confirm("이력서를 삭제할까요? 연결된 파일도 함께 삭제됩니다.")) {
                deleteMutation.mutate();
              }
            }}
          >
            삭제
          </button>
        </div>
        {updateMutation.error ? <p className="mt-3 text-sm text-rose-700">{updateMutation.error.message}</p> : null}
        {deleteMutation.error ? <p className="mt-3 text-sm text-rose-700">{deleteMutation.error.message}</p> : null}
      </section>

      <section className="panel max-w-none">
        <h2 className="text-xl font-semibold text-slate-950">파일</h2>
        <div className="mt-5 grid gap-3">
          {resume.files.length === 0 ? <p className="text-sm text-slate-600">업로드된 파일이 없습니다.</p> : null}
          {resume.files.map((resumeFile) => (
            <div className="rounded-2xl border border-slate-200 p-4" key={resumeFile.id}>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-slate-950">{resumeFile.original_filename}</p>
                  <p className="mt-1 text-sm text-slate-500">
                    {formatBytes(resumeFile.file_size)} · {resumeFile.content_type}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    className="button-secondary"
                    type="button"
                    onClick={() => downloadResumeFile(resumeId, resumeFile.id, resumeFile.original_filename)}
                  >
                    다운로드
                  </button>
                  <button
                    className="button-secondary border-rose-200 text-rose-700"
                    type="button"
                    disabled={deleteFileMutation.isPending}
                    onClick={() => deleteFileMutation.mutate(resumeFile.id)}
                  >
                    파일 삭제
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-3 rounded-2xl bg-slate-50 p-4">
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            새 파일 업로드
            <input
              className="input"
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <button
            className="button-primary w-fit"
            type="button"
            disabled={uploadMutation.isPending || !file}
            onClick={() => uploadMutation.mutate()}
          >
            파일 추가
          </button>
          {uploadMutation.error ? <p className="text-sm text-rose-700">{uploadMutation.error.message}</p> : null}
          {deleteFileMutation.error ? <p className="text-sm text-rose-700">{deleteFileMutation.error.message}</p> : null}
        </div>
      </section>
    </div>
  );
}

function formatBytes(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
