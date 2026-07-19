"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import { archiveApplication, listApplications } from "@/lib/api/application";
import type { ApplicationStatus } from "@/types/application";
import { applicationPriorityLabels, applicationStatusLabels, applicationStatusOptions } from "./application-labels";

export function ApplicationListPanel() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState("");
  const [status, setStatus] = useState<ApplicationStatus | "">("");
  const applicationsQuery = useQuery({
    queryKey: ["applications", { page, keyword, status }],
    queryFn: () => listApplications({ page, size: 10, keyword, status }),
    retry: false,
  });
  const archiveMutation = useMutation({
    mutationFn: archiveApplication,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applications"] }),
  });
  const data = applicationsQuery.data?.data;

  return (
    <div className="grid gap-5">
      <div className="panel max-w-none">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
          <label className="grid flex-1 gap-2 text-sm font-medium text-slate-700">
            검색
            <input className="input" value={keyword} placeholder="회사, 공고, 담당자" onChange={(event) => {
              setPage(1);
              setKeyword(event.target.value);
            }} />
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            상태
            <select className="input min-w-40" value={status} onChange={(event) => {
              setPage(1);
              setStatus(event.target.value as ApplicationStatus | "");
            }}>
              <option value="">전체</option>
              {applicationStatusOptions.map((value) => (
                <option key={value} value={value}>{applicationStatusLabels[value]}</option>
              ))}
            </select>
          </label>
          <Link className="button-primary" href="/applications/new">지원 항목 추가</Link>
        </div>
      </div>

      {applicationsQuery.isLoading ? <div className="panel max-w-none">지원 현황을 불러오는 중입니다.</div> : null}
      {applicationsQuery.error ? <div className="panel max-w-none text-rose-700">{applicationsQuery.error.message}</div> : null}
      {!applicationsQuery.isLoading && data?.items.length === 0 ? (
        <div className="panel max-w-none">
          <p className="text-slate-700">아직 관리 중인 지원 항목이 없습니다.</p>
          <Link className="button-primary mt-4 inline-flex" href="/applications/new">첫 지원 항목 만들기</Link>
        </div>
      ) : null}

      <div className="grid gap-3">
        {data?.items.map((application) => (
          <article className="panel max-w-none" key={application.id}>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-500">
                  {applicationStatusLabels[application.status]} · {applicationPriorityLabels[application.priority]}
                </p>
                <Link className="mt-1 block text-xl font-semibold text-slate-950 hover:underline" href={`/applications/${application.id}`}>
                  {application.company_name_snapshot ?? "회사 미지정"} · {application.job_title_snapshot ?? "공고 미지정"}
                </Link>
                <p className="mt-2 text-sm text-slate-600">
                  지원일 {formatDate(application.applied_at) ?? "-"} · 예정일 {formatDate(application.planned_apply_at) ?? "-"} · 메모 {application.notes_count}
                </p>
              </div>
              <button className="button-secondary" type="button" disabled={archiveMutation.isPending} onClick={() => archiveMutation.mutate(application.id)}>
                보관
              </button>
            </div>
          </article>
        ))}
      </div>

      {data && data.total > data.size ? (
        <div className="flex items-center justify-center gap-3">
          <button className="button-secondary" type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>이전</button>
          <span className="text-sm text-slate-600">{page} / {data.total_pages}</span>
          <button className="button-secondary" type="button" disabled={page >= data.total_pages} onClick={() => setPage((value) => value + 1)}>다음</button>
        </div>
      ) : null}
    </div>
  );
}

function formatDate(value: string | null) {
  if (!value) return null;
  return new Intl.DateTimeFormat("ko-KR", { dateStyle: "medium" }).format(new Date(value));
}
