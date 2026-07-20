"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { createDocumentImprovement, getApplicationDocument } from "@/lib/api/application-document";
import type { DocumentImprovementType } from "@/types/document-improvement";
import { documentImprovementTypeLabels } from "./document-improvement-labels";

const improvementTypes = Object.keys(documentImprovementTypeLabels) as DocumentImprovementType[];

export function DocumentImprovementCreatePanel({ documentId }: { documentId: number }) {
  const router = useRouter();
  const [improvementType, setImprovementType] = useState<DocumentImprovementType>("JOB_ALIGNMENT");
  const [customInstruction, setCustomInstruction] = useState("");
  const [targetTone, setTargetTone] = useState("전문적이고 진정성 있는 한국어");
  const [targetMinLength, setTargetMinLength] = useState("");
  const [targetMaxLength, setTargetMaxLength] = useState("");

  const documentQuery = useQuery({
    queryKey: ["application-document", documentId],
    queryFn: () => getApplicationDocument(documentId),
    retry: false,
  });

  const improvementMutation = useMutation({
    mutationFn: () =>
      createDocumentImprovement(documentId, {
        improvement_type: improvementType,
        custom_instruction: customInstruction.trim() || null,
        target_tone: targetTone.trim() || null,
        target_min_length: targetMinLength ? Number(targetMinLength) : null,
        target_max_length: targetMaxLength ? Number(targetMaxLength) : null,
      }),
    onSuccess: (response) => router.push(`/documents/${documentId}/improvements/${response.data.id}`),
  });

  useEffect(() => {
    if (documentQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [documentQuery.error, router]);

  const document = documentQuery.data?.data;
  const canSubmit = Boolean(document?.current_version?.content) && (improvementType !== "CUSTOM" || customInstruction.trim().length > 0);

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none overflow-hidden">
        <div className="rounded-3xl bg-gradient-to-br from-violet-600 to-indigo-500 p-6 text-white shadow-xl shadow-violet-500/20">
          <p className="text-sm font-semibold text-violet-100">AI 지원 문서 개선</p>
          <h1 className="mt-2 text-2xl font-bold">{document?.title ?? "지원 문서"}를 더 설득력 있게 다듬어요</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-violet-100">
            기존 버전은 그대로 보존되고, AI 제안을 확인한 뒤 승인할 때만 새 버전이 만들어집니다.
          </p>
          <div className="mt-4 flex flex-wrap gap-2 text-sm">
            <Link className="rounded-full bg-white/16 px-4 py-2 font-semibold hover:bg-white/24" href={`/documents/${documentId}`}>
              문서 상세로 돌아가기
            </Link>
            <span className="rounded-full bg-white/16 px-4 py-2">현재 버전 {document?.current_version_number ?? "-"}</span>
          </div>
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
        <form
          className="panel max-w-none"
          onSubmit={(event) => {
            event.preventDefault();
            if (canSubmit) {
              improvementMutation.mutate();
            }
          }}
        >
          <h2 className="text-lg font-semibold text-slate-950">개선 요청 설정</h2>
          <div className="mt-5 grid gap-4">
            <label className="grid gap-2 text-sm font-medium text-slate-700">
              개선 유형
              <select className="input" value={improvementType} onChange={(event) => setImprovementType(event.target.value as DocumentImprovementType)}>
                {improvementTypes.map((type) => (
                  <option value={type} key={type}>
                    {documentImprovementTypeLabels[type]}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-medium text-slate-700">
              추가 요청
              <textarea
                className="input min-h-32"
                value={customInstruction}
                placeholder="예: FastAPI 프로젝트 경험을 근거로 직무 적합성을 더 분명하게 보여주세요."
                onChange={(event) => setCustomInstruction(event.target.value)}
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-slate-700">
              목표 톤
              <input className="input" value={targetTone} onChange={(event) => setTargetTone(event.target.value)} />
            </label>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="grid gap-2 text-sm font-medium text-slate-700">
                최소 글자 수
                <input className="input" value={targetMinLength} inputMode="numeric" onChange={(event) => setTargetMinLength(event.target.value)} />
              </label>
              <label className="grid gap-2 text-sm font-medium text-slate-700">
                최대 글자 수
                <input className="input" value={targetMaxLength} inputMode="numeric" onChange={(event) => setTargetMaxLength(event.target.value)} />
              </label>
            </div>
          </div>
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button className="button-primary" type="submit" disabled={!canSubmit || improvementMutation.isPending}>
              {improvementMutation.isPending ? "개선안 생성 중..." : "개선안 생성"}
            </button>
            {improvementMutation.error ? <span className="text-sm text-rose-700">{improvementMutation.error.message}</span> : null}
          </div>
        </form>

        <aside className="panel max-w-none">
          <h2 className="text-lg font-semibold text-slate-950">현재 문서 미리보기</h2>
          {documentQuery.isLoading ? <p className="mt-3 text-sm text-slate-600">문서를 불러오는 중입니다.</p> : null}
          {documentQuery.error ? <p className="mt-3 text-sm text-rose-700">{documentQuery.error.message}</p> : null}
          <div className="mt-4 rounded-3xl border border-violet-100 bg-violet-50/70 p-4 text-sm leading-7 text-slate-700">
            {document?.current_version?.content ? (
              <p className="whitespace-pre-wrap">{document.current_version.content.slice(0, 1400)}</p>
            ) : (
              <p>먼저 문서 초안을 생성하거나 편집 버전을 저장해 주세요.</p>
            )}
          </div>
        </aside>
      </section>
    </div>
  );
}
