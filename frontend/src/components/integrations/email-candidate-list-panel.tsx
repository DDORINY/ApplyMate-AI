"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { approveEmailCandidate, listEmailCandidates, rejectEmailCandidate } from "@/lib/api/gmail-integration";
import type { EmailCandidateType } from "@/types/gmail-integration";

const candidateTypes: Array<{ value: EmailCandidateType | ""; label: string }> = [
  { value: "", label: "전체" },
  { value: "APPLICATION_RECEIVED", label: "지원 접수" },
  { value: "CODING_TEST", label: "코딩 테스트" },
  { value: "ASSIGNMENT", label: "과제" },
  { value: "INTERVIEW", label: "면접" },
  { value: "OFFER", label: "합격/오퍼" },
  { value: "REJECTED", label: "불합격" },
  { value: "SCHEDULE_CHANGE", label: "일정 변경" },
];

export function EmailCandidateListPanel() {
  const queryClient = useQueryClient();
  const [candidateType, setCandidateType] = useState<EmailCandidateType | "">("");
  const query = useQuery({
    queryKey: ["email-candidates-page", candidateType],
    queryFn: () => listEmailCandidates({ candidate_type: candidateType }),
    retry: false,
  });
  const approveMutation = useMutation({
    mutationFn: (candidateId: number) => approveEmailCandidate(candidateId, { apply_status_change: false, create_schedule_event: false }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["email-candidates-page"] }),
  });
  const rejectMutation = useMutation({
    mutationFn: rejectEmailCandidate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["email-candidates-page"] }),
  });

  const items = query.data?.data.items ?? [];

  return (
    <section className="mx-auto max-w-6xl">
      <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold text-indigo-600">Inbox Candidates</p>
          <h1 className="text-3xl font-bold text-slate-950">Gmail 채용 메일 후보</h1>
          <p className="mt-2 text-sm text-slate-600">후보를 확인하기 전에는 지원 상태나 일정에 반영되지 않습니다.</p>
        </div>
        <select className="rounded-xl border border-slate-200 px-3 py-2 text-sm" value={candidateType} onChange={(event) => setCandidateType(event.target.value as EmailCandidateType | "")}>
          {candidateTypes.map((item) => (
            <option key={item.value || "all"} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        {items.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
            후보가 없습니다. 외부 연동 화면에서 Gmail 동기화를 실행해 주세요.
          </div>
        ) : (
          items.map((candidate) => (
            <article key={candidate.id} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <p className="text-xs font-semibold text-indigo-600">{candidate.candidate_type}</p>
                  <h2 className="mt-1 text-lg font-semibold text-slate-950">{candidate.email_message?.subject ?? "메일 후보"}</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    {candidate.company_name ?? "회사 미확인"} · {candidate.job_title ?? "직무 미확인"} · {candidate.status}
                  </p>
                  <p className="mt-3 rounded-2xl bg-slate-50 p-3 text-sm text-slate-600">
                    {String(candidate.evidence.source_text ?? "근거 텍스트 없음")}
                  </p>
                </div>
                <div className="flex shrink-0 flex-wrap gap-2">
                  <button
                    className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
                    disabled={candidate.status === "APPLIED" || approveMutation.isPending}
                    onClick={() => approveMutation.mutate(candidate.id)}
                  >
                    후보 확인
                  </button>
                  <button
                    className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 disabled:opacity-50"
                    disabled={candidate.status === "REJECTED" || rejectMutation.isPending}
                    onClick={() => rejectMutation.mutate(candidate.id)}
                  >
                    거절
                  </button>
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
