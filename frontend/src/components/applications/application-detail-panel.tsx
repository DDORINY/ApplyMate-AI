"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import {
  changeApplicationStatus,
  createApplicationNote,
  deleteApplicationNote,
  getApplication,
  listApplicationNotes,
  listApplicationStatusHistory,
} from "@/lib/api/application";
import type { ApplicationNoteType, ApplicationStatus } from "@/types/application";
import {
  applicationChannelLabels,
  applicationNoteTypeLabels,
  applicationNoteTypeOptions,
  applicationPriorityLabels,
  applicationStatusLabels,
  applicationStatusOptions,
} from "./application-labels";

export function ApplicationDetailPanel({ applicationId }: { applicationId: number }) {
  const queryClient = useQueryClient();
  const [nextStatus, setNextStatus] = useState<ApplicationStatus>("APPLIED");
  const [statusNote, setStatusNote] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [noteType, setNoteType] = useState<ApplicationNoteType>("GENERAL");
  const applicationQuery = useQuery({
    queryKey: ["application", applicationId],
    queryFn: () => getApplication(applicationId),
    retry: false,
  });
  const historyQuery = useQuery({
    queryKey: ["application-status-history", applicationId],
    queryFn: () => listApplicationStatusHistory(applicationId),
    retry: false,
  });
  const notesQuery = useQuery({
    queryKey: ["application-notes", applicationId],
    queryFn: () => listApplicationNotes(applicationId),
    retry: false,
  });
  const statusMutation = useMutation({
    mutationFn: () => changeApplicationStatus(applicationId, nextStatus, statusNote || undefined),
    onSuccess: () => {
      setStatusNote("");
      queryClient.invalidateQueries({ queryKey: ["application", applicationId] });
      queryClient.invalidateQueries({ queryKey: ["application-status-history", applicationId] });
    },
  });
  const noteMutation = useMutation({
    mutationFn: () => createApplicationNote(applicationId, { content: noteContent, note_type: noteType, is_pinned: false }),
    onSuccess: () => {
      setNoteContent("");
      queryClient.invalidateQueries({ queryKey: ["application-notes", applicationId] });
      queryClient.invalidateQueries({ queryKey: ["application", applicationId] });
    },
  });
  const deleteNoteMutation = useMutation({
    mutationFn: (noteId: number) => deleteApplicationNote(applicationId, noteId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["application-notes", applicationId] }),
  });

  const application = applicationQuery.data?.data;

  if (applicationQuery.isLoading) {
    return <div className="panel max-w-none">지원 항목을 불러오는 중입니다.</div>;
  }
  if (!application) {
    return <div className="panel max-w-none text-rose-700">{applicationQuery.error?.message ?? "지원 항목을 찾을 수 없습니다."}</div>;
  }

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <p className="text-sm font-semibold text-slate-500">{applicationStatusLabels[application.status]}</p>
        <h1 className="mt-1 text-2xl font-bold text-slate-950">
          {application.company_name_snapshot ?? "회사 미지정"} · {application.job_title_snapshot ?? "공고 미지정"}
        </h1>
        <div className="mt-4 grid gap-3 text-sm text-slate-700 sm:grid-cols-2 lg:grid-cols-3">
          <Info label="우선순위" value={applicationPriorityLabels[application.priority]} />
          <Info label="지원 경로" value={applicationChannelLabels[application.application_channel]} />
          <Info label="지원 예정일" value={formatDateTime(application.planned_apply_at)} />
          <Info label="지원 완료일" value={formatDateTime(application.applied_at)} />
          <Info label="담당자" value={application.contact_name ?? "-"} />
          <Info label="담당자 이메일" value={application.contact_email ?? "-"} />
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          {application.job_id ? <Link className="button-secondary" href={`/jobs/${application.job_id}`}>채용공고 보기</Link> : null}
          {application.resume_id ? <Link className="button-secondary" href={`/resumes/${application.resume_id}`}>이력서 보기</Link> : null}
          {application.application_document_id ? <Link className="button-secondary" href={`/documents/${application.application_document_id}`}>지원 문서 보기</Link> : null}
          {application.application_url ? <a className="button-secondary" href={application.application_url} rel="noreferrer" target="_blank">지원 링크 열기</a> : null}
        </div>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">상태 변경</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-[220px_1fr_auto]">
          <select className="input" value={nextStatus} onChange={(event) => setNextStatus(event.target.value as ApplicationStatus)}>
            {applicationStatusOptions.map((value) => (
              <option key={value} value={value}>{applicationStatusLabels[value]}</option>
            ))}
          </select>
          <input className="input" value={statusNote} onChange={(event) => setStatusNote(event.target.value)} placeholder="변경 메모" />
          <button className="button-primary" type="button" disabled={statusMutation.isPending} onClick={() => statusMutation.mutate()}>변경</button>
        </div>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">메모</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-[180px_1fr_auto]">
          <select className="input" value={noteType} onChange={(event) => setNoteType(event.target.value as ApplicationNoteType)}>
            {applicationNoteTypeOptions.map((value) => (
              <option key={value} value={value}>{applicationNoteTypeLabels[value]}</option>
            ))}
          </select>
          <input className="input" value={noteContent} onChange={(event) => setNoteContent(event.target.value)} placeholder="메모를 입력하세요." />
          <button className="button-primary" type="button" disabled={noteMutation.isPending || !noteContent.trim()} onClick={() => noteMutation.mutate()}>추가</button>
        </div>
        <div className="mt-4 grid gap-2">
          {notesQuery.data?.data.map((note) => (
            <div className="rounded-2xl border border-slate-200 p-3" key={note.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold text-slate-500">{applicationNoteTypeLabels[note.note_type]}</p>
                  <p className="mt-1 text-sm text-slate-700">{note.content}</p>
                </div>
                <button className="text-sm text-rose-700" type="button" onClick={() => deleteNoteMutation.mutate(note.id)}>삭제</button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">상태 이력</h2>
        <ol className="mt-4 grid gap-3">
          {historyQuery.data?.data.map((item) => (
            <li className="rounded-2xl border border-slate-200 p-3" key={item.id}>
              <p className="text-sm font-semibold text-slate-700">
                {item.previous_status ? applicationStatusLabels[item.previous_status] : "시작"} → {applicationStatusLabels[item.new_status]}
              </p>
              <p className="mt-1 text-xs text-slate-500">{formatDateTime(item.changed_at)} · {item.source}</p>
              {item.note ? <p className="mt-2 text-sm text-slate-600">{item.note}</p> : null}
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <p className="text-xs font-semibold text-slate-500">{label}</p>
      <p className="mt-1">{value ?? "-"}</p>
    </div>
  );
}

function formatDateTime(value: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ko-KR", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}
