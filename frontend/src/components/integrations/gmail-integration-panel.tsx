"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  approveEmailCandidate,
  disconnectGmailIntegration,
  getGmailIntegrationStatus,
  listEmailCandidates,
  listGmailSyncRuns,
  startGmailConnection,
  syncGmail,
  updateGmailIntegrationSettings,
} from "@/lib/api/gmail-integration";
import type { EmailCandidateType } from "@/types/gmail-integration";

const candidateLabels: Record<EmailCandidateType, string> = {
  APPLICATION_RECEIVED: "지원 접수",
  DOCUMENT_REVIEW: "서류 전형",
  CODING_TEST: "코딩 테스트",
  ASSIGNMENT: "과제",
  INTERVIEW: "면접",
  FINAL_INTERVIEW: "최종 면접",
  OFFER: "합격/오퍼",
  REJECTED: "불합격",
  WITHDRAWN: "철회",
  SCHEDULE_CHANGE: "일정 변경",
  RECRUITER_CONTACT: "채용 담당자 연락",
  OTHER: "기타",
};

export function GmailIntegrationPanel() {
  const queryClient = useQueryClient();
  const [candidateType, setCandidateType] = useState<EmailCandidateType | "">("");
  const [lookbackDays, setLookbackDays] = useState(30);

  const statusQuery = useQuery({ queryKey: ["gmail-integration-status"], queryFn: getGmailIntegrationStatus, retry: false });
  const candidatesQuery = useQuery({
    queryKey: ["email-candidates", candidateType],
    queryFn: () => listEmailCandidates({ candidate_type: candidateType }),
    enabled: Boolean(statusQuery.data?.data.connected),
    retry: false,
  });
  const runsQuery = useQuery({
    queryKey: ["gmail-sync-runs"],
    queryFn: listGmailSyncRuns,
    enabled: Boolean(statusQuery.data?.data.connected),
    retry: false,
  });

  const connectMutation = useMutation({
    mutationFn: startGmailConnection,
    onSuccess: (response) => {
      window.location.href = response.data.authorization_url;
    },
  });
  const settingsMutation = useMutation({
    mutationFn: () => updateGmailIntegrationSettings({ sync_enabled: true, lookback_days: lookbackDays }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["gmail-integration-status"] }),
  });
  const syncMutation = useMutation({
    mutationFn: syncGmail,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gmail-integration-status"] });
      queryClient.invalidateQueries({ queryKey: ["email-candidates"] });
      queryClient.invalidateQueries({ queryKey: ["gmail-sync-runs"] });
    },
  });
  const approveMutation = useMutation({
    mutationFn: (candidateId: number) =>
      approveEmailCandidate(candidateId, { apply_status_change: false, create_schedule_event: false }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["email-candidates"] }),
  });
  const disconnectMutation = useMutation({
    mutationFn: disconnectGmailIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gmail-integration-status"] });
      queryClient.invalidateQueries({ queryKey: ["email-candidates"] });
      queryClient.invalidateQueries({ queryKey: ["gmail-sync-runs"] });
    },
  });

  const status = statusQuery.data?.data;
  const candidates = candidatesQuery.data?.data.items ?? [];

  return (
    <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-indigo-600">Gmail 채용 메일 분석</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">메일 후보를 만들고, 승인 전에는 반영하지 않습니다.</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            Gmail은 읽기 전용 scope만 사용합니다. 메일 수정·삭제·발송, 지원 상태 변경, 일정 생성은 사용자가 승인하기 전까지 수행하지 않습니다.
          </p>
        </div>
        <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm">
          <p className="font-semibold text-slate-900">{status?.connected ? "연결됨" : "연결 필요"}</p>
          <p className="text-slate-500">{status?.email ?? status?.provider ?? "provider 확인 중"}</p>
        </div>
      </div>

      {status?.needs_verification ? (
        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          실제 Gmail API 호출은 NEEDS_VERIFICATION 상태입니다. Mock provider에서는 전체 후보 플로우를 검증할 수 있습니다.
        </div>
      ) : null}

      <div className="mt-6 flex flex-wrap gap-3">
        {!status?.connected ? (
          <button
            className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            onClick={() => connectMutation.mutate()}
            disabled={connectMutation.isPending}
          >
            Gmail 연결
          </button>
        ) : (
          <>
            <label className="flex items-center gap-2 text-sm text-slate-700">
              조회 기간
              <input
                className="w-20 rounded-xl border border-slate-200 px-3 py-2"
                type="number"
                min={1}
                max={90}
                value={lookbackDays}
                onChange={(event) => setLookbackDays(Number(event.target.value))}
              />
              일
            </label>
            <button className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold" onClick={() => settingsMutation.mutate()}>
              설정 저장
            </button>
            <button
              className="rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
              onClick={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
            >
              Gmail 동기화
            </button>
            <button className="rounded-xl border border-red-200 px-4 py-2 text-sm font-semibold text-red-600" onClick={() => disconnectMutation.mutate()}>
              연결 해제
            </button>
          </>
        )}
      </div>

      {status?.connected ? (
        <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_320px]">
          <div>
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-950">분석 후보</h3>
              <select className="rounded-xl border border-slate-200 px-3 py-2 text-sm" value={candidateType} onChange={(event) => setCandidateType(event.target.value as EmailCandidateType | "")}>
                <option value="">전체</option>
                {Object.entries(candidateLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-3">
              {candidates.length === 0 ? (
                <p className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">아직 후보가 없습니다. Gmail 동기화를 실행해 주세요.</p>
              ) : (
                candidates.map((candidate) => (
                  <article key={candidate.id} className="rounded-2xl border border-slate-200 p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                      <div>
                        <p className="text-xs font-semibold text-indigo-600">{candidateLabels[candidate.candidate_type]}</p>
                        <h4 className="mt-1 font-semibold text-slate-950">{candidate.email_message?.subject ?? candidate.company_name ?? "메일 후보"}</h4>
                        <p className="mt-1 text-sm text-slate-500">
                          {candidate.company_name ?? "-"} · {candidate.job_title ?? "-"} · 신뢰도 {candidate.confidence}
                        </p>
                        <p className="mt-2 line-clamp-2 text-sm text-slate-600">{String(candidate.evidence.source_text ?? "")}</p>
                      </div>
                      <div className="flex shrink-0 gap-2">
                        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">{candidate.status}</span>
                        <button
                          className="rounded-xl bg-indigo-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50"
                          onClick={() => approveMutation.mutate(candidate.id)}
                          disabled={candidate.status === "APPLIED" || approveMutation.isPending}
                        >
                          후보 확인
                        </button>
                      </div>
                    </div>
                  </article>
                ))
              )}
            </div>
          </div>

          <aside className="rounded-2xl bg-slate-50 p-4">
            <h3 className="font-semibold text-slate-950">최근 동기화</h3>
            <div className="mt-3 space-y-2">
              {(runsQuery.data?.data ?? []).slice(0, 5).map((run) => (
                <div key={run.id} className="rounded-xl bg-white p-3 text-sm">
                  <p className="font-medium text-slate-900">{run.status}</p>
                  <p className="text-slate-500">
                    스캔 {run.scanned_count} · 후보 {run.candidate_count} · 중복 {run.ignored_count}
                  </p>
                </div>
              ))}
            </div>
          </aside>
        </div>
      ) : null}
    </section>
  );
}
