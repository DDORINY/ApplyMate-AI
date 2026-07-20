"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import {
  applyDocumentImprovement,
  getApplicationDocument,
  getDocumentImprovement,
  rejectDocumentImprovement,
  retryDocumentImprovement,
  updateDocumentImprovementSuggestion,
} from "@/lib/api/application-document";
import { documentImprovementRiskLabels, documentImprovementStatusLabels, documentImprovementTypeLabels } from "./document-improvement-labels";

export function DocumentImprovementDetailPanel({ documentId, runId }: { documentId: number; runId: number }) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const documentQuery = useQuery({
    queryKey: ["application-document", documentId],
    queryFn: () => getApplicationDocument(documentId),
    retry: false,
  });
  const runQuery = useQuery({
    queryKey: ["document-improvement", documentId, runId],
    queryFn: () => getDocumentImprovement(documentId, runId),
    retry: false,
  });

  useEffect(() => {
    if (documentQuery.error?.message === "로그인이 필요합니다." || runQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [documentQuery.error, runQuery.error, router]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["document-improvement", documentId, runId] });
    queryClient.invalidateQueries({ queryKey: ["application-document", documentId] });
    queryClient.invalidateQueries({ queryKey: ["application-document-versions", documentId] });
    queryClient.invalidateQueries({ queryKey: ["document-improvements", documentId] });
  };

  const updateMutation = useMutation({
    mutationFn: ({ suggestionId, selected }: { suggestionId: number; selected: boolean }) =>
      updateDocumentImprovementSuggestion(documentId, runId, suggestionId, {
        status: selected ? "APPROVED" : "REJECTED",
        selected,
      }),
    onSuccess: invalidate,
  });
  const applyMutation = useMutation({
    mutationFn: () =>
      applyDocumentImprovement(documentId, runId, {
        apply_all: false,
        suggestion_ids: runQuery.data?.data.suggestions.filter((item) => item.selected && item.status !== "REJECTED").map((item) => item.id) ?? [],
        version_title: "AI 개선 승인본",
      }),
    onSuccess: () => {
      invalidate();
      router.push(`/documents/${documentId}`);
    },
  });
  const rejectMutation = useMutation({
    mutationFn: () => rejectDocumentImprovement(documentId, runId),
    onSuccess: invalidate,
  });
  const retryMutation = useMutation({
    mutationFn: () => retryDocumentImprovement(documentId, runId),
    onSuccess: (response) => router.push(`/documents/${documentId}/improvements/${response.data.id}`),
  });

  const document = documentQuery.data?.data;
  const run = runQuery.data?.data;
  const currentContent = document?.current_version?.content ?? "";
  const suggestedContent = run?.suggested_content ?? "";

  if (documentQuery.isLoading || runQuery.isLoading) {
    return <div className="panel max-w-none">개선 실행을 불러오는 중입니다.</div>;
  }
  if (documentQuery.error || runQuery.error) {
    return <div className="panel max-w-none text-rose-700">{documentQuery.error?.message ?? runQuery.error?.message}</div>;
  }
  if (!document || !run) {
    return <div className="panel max-w-none">개선 실행을 찾을 수 없습니다.</div>;
  }

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">
              {documentImprovementTypeLabels[run.improvement_type]} · {documentImprovementStatusLabels[run.status]}
            </p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950">{run.suggested_title ?? document.title}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">{run.overall_feedback ?? "AI 개선 결과를 검토해 주세요."}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link className="button-secondary" href={`/documents/${documentId}/improve`}>
              다른 개선 요청
            </Link>
            <Link className="button-secondary" href={`/documents/${documentId}`}>
              문서 상세
            </Link>
          </div>
        </div>
      </section>

      {(run.warnings.length || run.missing_information.length || run.outdated) ? (
        <section className="panel max-w-none border-amber-200 bg-amber-50/80">
          <h2 className="text-lg font-semibold text-amber-900">승인 전 확인 필요</h2>
          <ul className="mt-3 grid gap-2 text-sm text-amber-800">
            {run.outdated ? <li>기준 문서보다 최신 버전이 있어 바로 적용할 수 없습니다. 새 개선안을 다시 생성해 주세요.</li> : null}
            {run.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
            {run.missing_information.map((item) => (
              <li key={item}>부족한 정보: {item}</li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="grid gap-5 lg:grid-cols-2">
        <article className="panel max-w-none">
          <h2 className="text-lg font-semibold text-slate-950">Before</h2>
          <div className="mt-4 min-h-96 rounded-3xl border border-slate-200 bg-white/70 p-4 text-sm leading-7 text-slate-700">
            <p className="whitespace-pre-wrap">{currentContent}</p>
          </div>
        </article>
        <article className="panel max-w-none">
          <h2 className="text-lg font-semibold text-slate-950">After 제안</h2>
          <div className="mt-4 min-h-96 rounded-3xl border border-violet-100 bg-violet-50/80 p-4 text-sm leading-7 text-slate-800">
            <p className="whitespace-pre-wrap">{suggestedContent}</p>
          </div>
        </article>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">문장별 제안</h2>
        <div className="mt-4 grid gap-3">
          {run.suggestions.map((suggestion) => (
            <article className="rounded-3xl border border-slate-200 bg-white/75 p-4" key={suggestion.id}>
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div className="grid gap-3 text-sm leading-6">
                  <p className="text-slate-500 line-through decoration-rose-300">{suggestion.original_text}</p>
                  <p className="font-medium text-slate-950">{suggestion.suggested_text}</p>
                  <p className="text-slate-600">{suggestion.reason}</p>
                  <p className="text-xs font-semibold text-violet-600">
                    위험도 {documentImprovementRiskLabels[suggestion.risk_level]} · 상태 {suggestion.status}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2">
                  <button
                    className={suggestion.selected ? "button-primary" : "button-secondary"}
                    type="button"
                    disabled={updateMutation.isPending || suggestion.status === "APPLIED"}
                    onClick={() => updateMutation.mutate({ suggestionId: suggestion.id, selected: true })}
                  >
                    승인
                  </button>
                  <button
                    className="button-secondary"
                    type="button"
                    disabled={updateMutation.isPending || suggestion.status === "APPLIED"}
                    onClick={() => updateMutation.mutate({ suggestionId: suggestion.id, selected: false })}
                  >
                    제외
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="panel max-w-none">
        <div className="flex flex-wrap items-center gap-3">
          <button className="button-primary" type="button" disabled={applyMutation.isPending || run.outdated || run.status === "APPLIED"} onClick={() => applyMutation.mutate()}>
            {applyMutation.isPending ? "새 버전 저장 중..." : "승인한 제안 새 버전으로 적용"}
          </button>
          <button className="button-secondary" type="button" disabled={rejectMutation.isPending || run.status === "APPLIED"} onClick={() => rejectMutation.mutate()}>
            전체 거절
          </button>
          <button className="button-secondary" type="button" disabled={retryMutation.isPending || run.status === "APPLIED"} onClick={() => retryMutation.mutate()}>
            재시도
          </button>
          {applyMutation.error ? <span className="text-sm text-rose-700">{applyMutation.error.message}</span> : null}
        </div>
      </section>
    </div>
  );
}
