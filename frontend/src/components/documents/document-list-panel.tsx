"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  archiveApplicationDocument,
  duplicateApplicationDocument,
  listApplicationDocuments,
} from "@/lib/api/application-document";
import type { ApplicationDocumentStatus, ApplicationDocumentType } from "@/types/application-document";
import { documentStatusLabels, documentTypeLabels } from "./document-labels";

export function DocumentListPanel() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState("");
  const [documentType, setDocumentType] = useState<ApplicationDocumentType | "">("");
  const [status, setStatus] = useState<ApplicationDocumentStatus | "">("");

  const documentsQuery = useQuery({
    queryKey: ["application-documents", { page, keyword, documentType, status }],
    queryFn: () =>
      listApplicationDocuments({
        page,
        size: 10,
        keyword,
        document_type: documentType,
        status,
      }),
    retry: false,
  });

  const duplicateMutation = useMutation({
    mutationFn: (documentId: number) => duplicateApplicationDocument(documentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["application-documents"] }),
  });

  const archiveMutation = useMutation({
    mutationFn: (documentId: number) => archiveApplicationDocument(documentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["application-documents"] }),
  });

  useEffect(() => {
    if (documentsQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [documentsQuery.error, router]);

  const data = documentsQuery.data?.data;

  return (
    <div className="grid gap-5">
      <div className="panel max-w-none">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
          <label className="grid flex-1 gap-2 text-sm font-medium text-slate-700">
            검색
            <input
              className="input"
              value={keyword}
              placeholder="문서 제목, 문항, 지시사항"
              onChange={(event) => {
                setPage(1);
                setKeyword(event.target.value);
              }}
            />
          </label>
          <Select label="문서 유형" value={documentType} onChange={(value) => setDocumentType(value as ApplicationDocumentType | "")}>
            <option value="">전체</option>
            {Object.entries(documentTypeLabels).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </Select>
          <Select label="상태" value={status} onChange={(value) => setStatus(value as ApplicationDocumentStatus | "")}>
            <option value="">전체</option>
            {Object.entries(documentStatusLabels).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </Select>
          <Link className="button-primary" href="/documents/new">
            지원 문서 생성
          </Link>
        </div>
      </div>

      {documentsQuery.isLoading ? <div className="panel max-w-none">지원 문서를 불러오는 중입니다.</div> : null}
      {documentsQuery.error ? <div className="panel max-w-none text-rose-700">{documentsQuery.error.message}</div> : null}
      {!documentsQuery.isLoading && data?.items.length === 0 ? (
        <div className="panel max-w-none">
          <p className="text-slate-700">아직 생성한 지원 문서가 없습니다.</p>
          <Link className="button-primary mt-4 inline-flex" href="/documents/new">
            첫 지원 문서 만들기
          </Link>
        </div>
      ) : null}

      <div className="grid gap-3">
        {data?.items.map((document) => (
          <article className="panel max-w-none" key={document.id}>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-500">
                  {documentTypeLabels[document.document_type]} · {documentStatusLabels[document.status]}
                </p>
                <Link className="mt-1 block text-xl font-semibold text-slate-950 hover:underline" href={`/documents/${document.id}`}>
                  {document.title}
                </Link>
                <p className="mt-2 text-sm text-slate-600">
                  현재 버전: {document.current_version_number ?? "-"} · 글자 수: {document.current_version?.character_count ?? 0}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button className="button-secondary" type="button" disabled={duplicateMutation.isPending} onClick={() => duplicateMutation.mutate(document.id)}>
                  복제
                </button>
                <button className="button-secondary" type="button" disabled={archiveMutation.isPending} onClick={() => archiveMutation.mutate(document.id)}>
                  보관
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>

      {data && data.total > data.size ? (
        <div className="flex items-center justify-center gap-3">
          <button className="button-secondary" type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
            이전
          </button>
          <span className="text-sm text-slate-600">{page}</span>
          <button className="button-secondary" type="button" disabled={page * data.size >= data.total} onClick={() => setPage((value) => value + 1)}>
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
