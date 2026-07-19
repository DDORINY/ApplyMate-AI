"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { listJobs, updateJob } from "@/lib/api/job";
import type { JobEmploymentType, JobPostingStatus, JobWorkType } from "@/types/job";
import { employmentTypeLabels, statusLabels, workTypeLabels } from "./job-labels";

export function JobListPanel() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<JobPostingStatus | "">("");
  const [employmentType, setEmploymentType] = useState<JobEmploymentType | "">("");
  const [workType, setWorkType] = useState<JobWorkType | "">("");
  const [favoriteOnly, setFavoriteOnly] = useState(false);

  const jobsQuery = useQuery({
    queryKey: ["jobs", { page, query, status, employmentType, workType, favoriteOnly }],
    queryFn: () =>
      listJobs({
        page,
        size: 10,
        query,
        status,
        employment_type: employmentType,
        work_type: workType,
        is_favorite: favoriteOnly ? true : "",
      }),
    retry: false,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, is_favorite }: { id: number; is_favorite: boolean }) =>
      updateJob(id, { is_favorite }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
  });

  useEffect(() => {
    if (jobsQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [jobsQuery.error, router]);

  const data = jobsQuery.data?.data;

  return (
    <div className="grid gap-5">
      <div className="panel max-w-none">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
          <label className="grid flex-1 gap-2 text-sm font-medium text-slate-700">
            검색
            <input
              className="input"
              value={query}
              placeholder="공고 제목, 기업, 직무, 지역, 메모"
              onChange={(event) => {
                setPage(1);
                setQuery(event.target.value);
              }}
            />
          </label>
          <Select label="상태" value={status} onChange={(value) => setStatus(value as JobPostingStatus | "")}>
            <option value="">전체</option>
            {Object.entries(statusLabels).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </Select>
          <Select
            label="고용 형태"
            value={employmentType}
            onChange={(value) => setEmploymentType(value as JobEmploymentType | "")}
          >
            <option value="">전체</option>
            {Object.entries(employmentTypeLabels).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </Select>
          <Select label="근무 형태" value={workType} onChange={(value) => setWorkType(value as JobWorkType | "")}>
            <option value="">전체</option>
            {Object.entries(workTypeLabels).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </Select>
          <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
            <input
              type="checkbox"
              checked={favoriteOnly}
              onChange={(event) => {
                setPage(1);
                setFavoriteOnly(event.target.checked);
              }}
            />
            관심만
          </label>
        </div>
      </div>

      {jobsQuery.isLoading ? <div className="panel max-w-none">채용공고를 불러오는 중입니다.</div> : null}
      {jobsQuery.error ? <div className="panel max-w-none text-rose-700">{jobsQuery.error.message}</div> : null}
      {!jobsQuery.isLoading && data?.items.length === 0 ? (
        <div className="panel max-w-none">
          <p className="text-slate-700">등록된 채용공고가 없습니다.</p>
          <Link className="button-primary mt-4 inline-flex" href="/jobs/new">
            첫 채용공고 등록하기
          </Link>
        </div>
      ) : null}

      <div className="grid gap-3">
        {data?.items.map((job) => (
          <article className="panel max-w-none" key={job.id}>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-500">{job.company.name}</p>
                <Link className="mt-1 block text-xl font-semibold text-slate-950 hover:underline" href={`/jobs/${job.id}`}>
                  {job.title}
                </Link>
                <p className="mt-2 text-sm text-slate-600">
                  {[job.position, employmentTypeLabels[job.employment_type], workTypeLabels[job.work_type], job.location]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  마감: {job.deadline_at ?? "미정"} · 상태: {statusLabels[job.status]}
                </p>
              </div>
              <button
                className="button-secondary"
                type="button"
                disabled={updateMutation.isPending}
                onClick={() => updateMutation.mutate({ id: job.id, is_favorite: !job.is_favorite })}
              >
                {job.is_favorite ? "★ 관심" : "☆ 관심"}
              </button>
            </div>
          </article>
        ))}
      </div>

      {data && data.total_pages > 1 ? (
        <div className="flex items-center justify-center gap-3">
          <button className="button-secondary" type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
            이전
          </button>
          <span className="text-sm text-slate-600">
            {data.page} / {data.total_pages}
          </span>
          <button
            className="button-secondary"
            type="button"
            disabled={page >= data.total_pages}
            onClick={() => setPage((value) => value + 1)}
          >
            다음
          </button>
        </div>
      ) : null}
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  children,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  children: React.ReactNode;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <select className="input min-w-36" value={value} onChange={(event) => onChange(event.target.value)}>
        {children}
      </select>
    </label>
  );
}
