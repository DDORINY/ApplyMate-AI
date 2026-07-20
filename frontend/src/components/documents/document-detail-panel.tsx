"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import {
  createApplicationDocumentVersion,
  getApplicationDocument,
  listApplicationDocumentGenerationRuns,
  listApplicationDocumentSources,
  listApplicationDocumentVersions,
  listDocumentImprovements,
  regenerateApplicationDocument,
  restoreApplicationDocumentVersion,
} from "@/lib/api/application-document";
import { documentImprovementStatusLabels, documentImprovementTypeLabels } from "./document-improvement-labels";
import { documentStatusLabels, documentTypeLabels } from "./document-labels";

export function DocumentDetailPanel({ documentId }: { documentId: number }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [content, setContent] = useState("");

  const documentQuery = useQuery({
    queryKey: ["application-document", documentId],
    queryFn: () => getApplicationDocument(documentId),
    retry: false,
  });
  const versionsQuery = useQuery({
    queryKey: ["application-document-versions", documentId],
    queryFn: () => listApplicationDocumentVersions(documentId),
    retry: false,
  });
  const sourcesQuery = useQuery({
    queryKey: ["application-document-sources", documentId],
    queryFn: () => listApplicationDocumentSources(documentId),
    retry: false,
  });
  const runsQuery = useQuery({
    queryKey: ["application-document-runs", documentId],
    queryFn: () => listApplicationDocumentGenerationRuns(documentId),
    retry: false,
  });
  const improvementsQuery = useQuery({
    queryKey: ["document-improvements", documentId],
    queryFn: () => listDocumentImprovements(documentId),
    retry: false,
  });

  const document = documentQuery.data?.data;
  const currentVersion = document?.current_version;

  useEffect(() => {
    if (documentQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [documentQuery.error, router]);

  useEffect(() => {
    if (currentVersion?.content) {
      setContent(currentVersion.content);
    }
  }, [currentVersion?.content]);

  const counts = useMemo(() => {
    const paragraphs = content.split("\n\n").filter((item) => item.trim()).length;
    return {
      character_count: content.length,
      character_count_without_spaces: content.replace(/\s/g, "").length,
      word_count: content.split(/\s+/).filter(Boolean).length,
      paragraph_count: paragraphs || (content.trim() ? 1 : 0),
    };
  }, [content]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["application-document", documentId] });
    queryClient.invalidateQueries({ queryKey: ["application-document-versions", documentId] });
    queryClient.invalidateQueries({ queryKey: ["application-document-sources", documentId] });
    queryClient.invalidateQueries({ queryKey: ["application-document-runs", documentId] });
    queryClient.invalidateQueries({ queryKey: ["document-improvements", documentId] });
  };

  const saveMutation = useMutation({
    mutationFn: () =>
      createApplicationDocumentVersion(documentId, {
        content,
        change_summary: "사용자 편집 저장",
      }),
    onSuccess: invalidate,
  });
  const regenerateMutation = useMutation({
    mutationFn: () => regenerateApplicationDocument(documentId),
    onSuccess: invalidate,
  });
  const restoreMutation = useMutation({
    mutationFn: (versionId: number) => restoreApplicationDocumentVersion(documentId, versionId),
    onSuccess: invalidate,
  });

  if (documentQuery.isLoading) {
    return <div className="panel">지원 문서를 불러오는 중입니다.</div>;
  }
  if (documentQuery.error) {
    return <div className="panel text-rose-700">{documentQuery.error.message}</div>;
  }
  if (!document) {
    return <div className="panel">지원 문서를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-500">
              {documentTypeLabels[document.document_type]} · {documentStatusLabels[document.status]}
            </p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950">{document.title}</h1>
            <div className="mt-3 flex flex-wrap gap-2">
              <Link className="button-primary inline-flex" href={`/documents/${document.id}/improve`}>
                AI 문서 개선
              </Link>
              <Link className="button-secondary inline-flex" href={`/applications/new?documentId=${document.id}`}>
                이 문서로 지원 항목 생성
              </Link>
            </div>
            <p className="mt-2 text-sm text-slate-600">
              현재 버전 {document.current_version_number ?? "-"} · 제한 {document.character_limit ?? "없음"}자
            </p>
          </div>
          <button className="button-secondary" type="button" disabled={regenerateMutation.isPending} onClick={() => regenerateMutation.mutate()}>
            {regenerateMutation.isPending ? "재생성 중..." : "AI 재생성"}
          </button>
        </div>
      </section>

      <section className="panel max-w-none">
        <div className="mb-3 flex flex-wrap gap-3 text-sm text-slate-600">
          <span>공백 포함 {counts.character_count}</span>
          <span>공백 제외 {counts.character_count_without_spaces}</span>
          <span>단어 {counts.word_count}</span>
          <span>문단 {counts.paragraph_count}</span>
          {document.character_limit && counts.character_count > document.character_limit ? (
            <span className="font-semibold text-rose-700">제한 초과</span>
          ) : null}
        </div>
        <textarea className="input min-h-96 font-mono text-sm leading-7" value={content} onChange={(event) => setContent(event.target.value)} />
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <button className="button-primary" type="button" disabled={saveMutation.isPending || !content.trim()} onClick={() => saveMutation.mutate()}>
            {saveMutation.isPending ? "저장 중..." : "편집 버전 저장"}
          </button>
          {saveMutation.error ? <span className="text-sm text-rose-700">{saveMutation.error.message}</span> : null}
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-4">
        <div className="panel max-w-none lg:col-span-1">
          <h2 className="text-lg font-semibold text-slate-950">버전</h2>
          <div className="mt-3 grid gap-2">
            {versionsQuery.data?.data.map((version) => (
              <button
                className="rounded-xl border border-slate-200 px-3 py-2 text-left text-sm hover:bg-slate-50"
                type="button"
                key={version.id}
                disabled={restoreMutation.isPending || version.version_number === document.current_version_number}
                onClick={() => restoreMutation.mutate(version.id)}
              >
                v{version.version_number} · {version.is_ai_generated ? "AI" : "사용자"} · {version.character_count}자
              </button>
            ))}
          </div>
        </div>

        <div className="panel max-w-none lg:col-span-1">
          <h2 className="text-lg font-semibold text-slate-950">근거</h2>
          <div className="mt-3 grid gap-2">
            {sourcesQuery.data?.data.map((source) => (
              <div className="rounded-xl border border-slate-200 p-3 text-sm" key={source.id}>
                <p className="font-semibold text-slate-700">
                  {source.source_type} #{source.source_id}
                </p>
                <p className="mt-1 text-slate-600">{String(source.evidence.evidence_text ?? "").slice(0, 180)}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="panel max-w-none lg:col-span-1">
          <h2 className="text-lg font-semibold text-slate-950">생성 이력</h2>
          <div className="mt-3 grid gap-2">
            {runsQuery.data?.data.map((run) => (
              <div className="rounded-xl border border-slate-200 p-3 text-sm" key={run.id}>
                <p className="font-semibold text-slate-700">
                  {run.status} · {run.provider}
                </p>
                {run.error_code ? <p className="mt-1 text-rose-700">{run.error_code}</p> : null}
              </div>
            ))}
          </div>
        </div>

        <div className="panel max-w-none lg:col-span-1">
          <h2 className="text-lg font-semibold text-slate-950">개선 이력</h2>
          <div className="mt-3 grid gap-2">
            {improvementsQuery.data?.data.items.map((run) => (
              <Link
                className="rounded-xl border border-slate-200 p-3 text-sm hover:bg-violet-50"
                href={`/documents/${documentId}/improvements/${run.id}`}
                key={run.id}
              >
                <p className="font-semibold text-slate-700">
                  {documentImprovementTypeLabels[run.improvement_type]} · {documentImprovementStatusLabels[run.status]}
                </p>
                <p className="mt-1 text-slate-500">{run.created_at.slice(0, 10)}</p>
              </Link>
            ))}
            {improvementsQuery.data?.data.items.length === 0 ? <p className="text-sm text-slate-600">아직 개선 이력이 없습니다.</p> : null}
          </div>
        </div>
      </section>
    </div>
  );
}
