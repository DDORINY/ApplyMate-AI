"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  createApplicationDocument,
  generateApplicationDocument,
  getDocumentProviderStatus,
} from "@/lib/api/application-document";
import type { ApplicationDocumentTone, ApplicationDocumentType } from "@/types/application-document";
import { documentToneLabels, documentTypeLabels } from "./document-labels";

const numericFields = ["job_id", "resume_id", "resume_file_id", "resume_analysis_id", "job_analysis_id", "job_match_id"] as const;

export function DocumentCreatePanel() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [documentType, setDocumentType] = useState<ApplicationDocumentType>("MOTIVATION");
  const [tone, setTone] = useState<ApplicationDocumentTone>("PROFESSIONAL");
  const [question, setQuestion] = useState("");
  const [instructions, setInstructions] = useState("");
  const [characterLimit, setCharacterLimit] = useState("800");
  const [focusPoints, setFocusPoints] = useState("");
  const [sourceIds, setSourceIds] = useState<Record<(typeof numericFields)[number], string>>({
    job_id: "",
    resume_id: "",
    resume_file_id: "",
    resume_analysis_id: "",
    job_analysis_id: "",
    job_match_id: "",
  });

  const providerQuery = useQuery({
    queryKey: ["document-provider-status"],
    queryFn: getDocumentProviderStatus,
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const createResponse = await createApplicationDocument({
        title,
        document_type: documentType,
        question: question || null,
        instructions: instructions || null,
        tone,
        character_limit: characterLimit ? Number(characterLimit) : null,
        focus_points: focusPoints
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),
        ...Object.fromEntries(
          numericFields.map((field) => [field, sourceIds[field] ? Number(sourceIds[field]) : null]),
        ),
      });
      return generateApplicationDocument(createResponse.data.id);
    },
    onSuccess: (response) => router.push(`/documents/${response.data.id}`),
  });

  return (
    <div className="panel">
      <div className="mb-6">
        <p className="text-sm font-semibold text-slate-500">AI Provider</p>
        <p className="text-sm text-slate-700">
          {providerQuery.isLoading
            ? "상태 확인 중"
            : providerQuery.data
              ? `${providerQuery.data.data.active_provider} · ${providerQuery.data.data.model ?? "모델 미설정"}`
              : "상태를 확인하지 못했습니다."}
        </p>
      </div>

      <form className="grid gap-4" onSubmit={(event) => {
        event.preventDefault();
        createMutation.mutate();
      }}>
        <label className="grid gap-2 text-sm font-medium text-slate-700">
          제목
          <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} required placeholder="예: 토스 프론트엔드 지원동기" />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            문서 유형
            <select className="input" value={documentType} onChange={(event) => setDocumentType(event.target.value as ApplicationDocumentType)}>
              {Object.entries(documentTypeLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            말투
            <select className="input" value={tone} onChange={(event) => setTone(event.target.value as ApplicationDocumentTone)}>
              {Object.entries(documentToneLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {numericFields.map((field) => (
            <label className="grid gap-2 text-sm font-medium text-slate-700" key={field}>
              {field}
              <input
                className="input"
                inputMode="numeric"
                value={sourceIds[field]}
                placeholder="선택 사항"
                onChange={(event) => setSourceIds((value) => ({ ...value, [field]: event.target.value }))}
              />
            </label>
          ))}
        </div>

        <label className="grid gap-2 text-sm font-medium text-slate-700">
          문항
          <textarea className="input min-h-24" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="지원동기 또는 자기소개서 문항을 입력하세요." />
        </label>

        <label className="grid gap-2 text-sm font-medium text-slate-700">
          추가 지시사항
          <textarea className="input min-h-24" value={instructions} onChange={(event) => setInstructions(event.target.value)} placeholder="강조할 경험, 피해야 할 표현, 분량 등을 적어주세요." />
        </label>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            글자 수 제한
            <input className="input" inputMode="numeric" value={characterLimit} onChange={(event) => setCharacterLimit(event.target.value)} />
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            중점 포인트
            <input className="input" value={focusPoints} onChange={(event) => setFocusPoints(event.target.value)} placeholder="쉼표로 구분" />
          </label>
        </div>

        {createMutation.error ? <p className="text-sm text-rose-700">{createMutation.error.message}</p> : null}
        <button className="button-primary" type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? "생성 중..." : "문서 생성"}
        </button>
      </form>
    </div>
  );
}
