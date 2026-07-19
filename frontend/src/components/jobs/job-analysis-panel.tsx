"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import {
  analyzeJob,
  deleteJobAnalysis,
  getAIProviderStatus,
  getJobAnalysis,
  listJobAnalysisRuns,
  updateJobAnalysis,
} from "@/lib/api/job-analysis";

type JobAnalysisPanelProps = {
  jobId: number;
};

export function JobAnalysisPanel({ jobId }: JobAnalysisPanelProps) {
  const queryClient = useQueryClient();
  const [summary, setSummary] = useState("");
  const [keywords, setKeywords] = useState("");

  const providerQuery = useQuery({
    queryKey: ["ai-provider"],
    queryFn: getAIProviderStatus,
    retry: false,
  });
  const analysisQuery = useQuery({
    queryKey: ["job-analysis", jobId],
    queryFn: () => getJobAnalysis(jobId),
    retry: false,
  });
  const runsQuery = useQuery({
    queryKey: ["job-analysis-runs", jobId],
    queryFn: () => listJobAnalysisRuns(jobId),
    retry: false,
  });

  const analysis = analysisQuery.data?.data;
  const provider = providerQuery.data?.data;

  useEffect(() => {
    if (!analysis) {
      return;
    }
    setSummary(analysis.summary ?? "");
    setKeywords((analysis.keywords ?? []).join(", "));
  }, [analysis]);

  const runMutation = useMutation({
    mutationFn: (force: boolean) => analyzeJob(jobId, force),
    onSuccess: (response) => {
      queryClient.setQueryData(["job-analysis", jobId], response);
      queryClient.invalidateQueries({ queryKey: ["job-analysis-runs", jobId] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: () =>
      updateJobAnalysis(jobId, {
        summary,
        keywords: keywords
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
      }),
    onSuccess: (response) => queryClient.setQueryData(["job-analysis", jobId], response),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteJobAnalysis(jobId),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ["job-analysis", jobId] });
      queryClient.invalidateQueries({ queryKey: ["job-analysis-runs", jobId] });
    },
  });

  const actionDisabled =
    runMutation.isPending || providerQuery.isLoading || provider?.analysis_available === false;

  return (
    <section className="panel max-w-none">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-sky-700">AI 채용공고 분석</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            공고 원문을 구조화해서 볼 수 있어요
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            Provider: {provider?.active_provider ?? "확인 중"}
            {provider?.model ? ` · ${provider.model}` : ""}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="button-primary"
            type="button"
            disabled={actionDisabled}
            onClick={() => runMutation.mutate(false)}
          >
            {runMutation.isPending ? "분석 중..." : analysis ? "최신 분석 확인" : "분석 실행"}
          </button>
          <button
            className="button-secondary"
            type="button"
            disabled={actionDisabled}
            onClick={() => runMutation.mutate(true)}
          >
            재분석
          </button>
        </div>
      </div>

      {provider && !provider.analysis_available ? (
        <p className="mt-4 rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
          AI Provider가 비활성화되어 있습니다. `.env`에서 AI_PROVIDER를 mock 또는 openai로 설정해
          주세요.
        </p>
      ) : null}
      {analysis?.is_outdated ? (
        <p className="mt-4 rounded-2xl bg-orange-50 px-4 py-3 text-sm text-orange-800">
          공고 내용이 변경되어 기존 분석이 오래되었습니다. 재분석을 권장합니다.
        </p>
      ) : null}
      {runMutation.error ? <ErrorMessage message={runMutation.error.message} /> : null}
      {analysisQuery.error && !analysis ? (
        <p className="mt-4 text-sm text-slate-500">아직 저장된 분석 결과가 없습니다.</p>
      ) : null}

      {analysis ? (
        <div className="mt-5 grid gap-5">
          <div className="rounded-2xl border border-slate-200 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge>{analysis.status}</Badge>
              {analysis.is_user_edited ? <Badge>사용자 수정됨</Badge> : null}
              <span className="text-xs text-slate-500">
                {analysis.analyzed_at ? new Date(analysis.analyzed_at).toLocaleString() : ""}
              </span>
            </div>
            <label className="mt-4 grid gap-2 text-sm font-medium text-slate-700">
              요약
              <textarea
                className="input min-h-28"
                value={summary}
                onChange={(event) => setSummary(event.target.value)}
              />
            </label>
            <label className="mt-4 grid gap-2 text-sm font-medium text-slate-700">
              키워드
              <input
                className="input"
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
                placeholder="Python, FastAPI, PostgreSQL"
              />
            </label>
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                className="button-primary"
                type="button"
                disabled={updateMutation.isPending}
                onClick={() => updateMutation.mutate()}
              >
                {updateMutation.isPending ? "저장 중..." : "분석 결과 저장"}
              </button>
              <button
                className="button-secondary border-rose-200 text-rose-700"
                type="button"
                disabled={deleteMutation.isPending}
                onClick={() => {
                  if (window.confirm("분석 결과를 삭제할까요? 실행 이력은 보존됩니다.")) {
                    deleteMutation.mutate();
                  }
                }}
              >
                삭제
              </button>
            </div>
            {updateMutation.error ? <ErrorMessage message={updateMutation.error.message} /> : null}
            {deleteMutation.error ? <ErrorMessage message={deleteMutation.error.message} /> : null}
          </div>

          <AnalysisList title="주요 업무" items={analysis.responsibilities ?? []} />
          <AnalysisList title="필수 조건" items={analysis.required_qualifications ?? []} />
          <AnalysisList title="우대 조건" items={analysis.preferred_qualifications ?? []} />
          <AnalysisList title="기술 스택" items={analysis.technical_skills ?? []} />
          <div className="rounded-2xl border border-slate-200 p-4">
            <h3 className="font-semibold text-slate-950">실행 이력</h3>
            <div className="mt-3 grid gap-2 text-sm text-slate-600">
              {(runsQuery.data?.data.items ?? []).map((run) => (
                <div className="rounded-xl bg-slate-50 px-3 py-2" key={run.id}>
                  #{run.id} · {run.status} · {run.provider}
                  {run.total_tokens ? ` · ${run.total_tokens} tokens` : ""}
                  {run.error_code ? ` · ${run.error_code}` : ""}
                </div>
              ))}
              {runsQuery.data?.data.items.length === 0 ? "실행 이력이 없습니다." : null}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function AnalysisList({ title, items }: { title: string; items: Record<string, unknown>[] }) {
  return (
    <div className="rounded-2xl border border-slate-200 p-4">
      <h3 className="font-semibold text-slate-950">{title}</h3>
      <div className="mt-3 grid gap-3">
        {items.length === 0 ? <p className="text-sm text-slate-500">추출된 항목이 없습니다.</p> : null}
        {items.map((item, index) => (
          <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700" key={`${title}-${index}`}>
            <p className="font-medium text-slate-950">{String(item.text ?? item.name ?? "")}</p>
            {item.evidence ? <p className="mt-1 text-slate-500">근거: {String(item.evidence)}</p> : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function Badge({ children }: { children: string }) {
  return <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">{children}</span>;
}

function ErrorMessage({ message }: { message: string }) {
  return <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{message}</p>;
}
