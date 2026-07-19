"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { createApplication, getApplicationOptions } from "@/lib/api/application";
import type { ApplicationChannel, ApplicationPriority, ApplicationStatus } from "@/types/application";
import { SourceSelector } from "./source-selector";
import {
  applicationChannelLabels,
  applicationChannelOptions,
  applicationPriorityLabels,
  applicationPriorityOptions,
  applicationStatusLabels,
  applicationStatusOptions,
} from "./application-labels";

function optionalNumber(value: string) {
  return value ? Number(value) : null;
}

function queryDefault(searchParams: URLSearchParams, key: string) {
  const value = searchParams.get(key);
  return value && Number.isFinite(Number(value)) ? value : "";
}

export function ApplicationCreatePanel() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [jobId, setJobId] = useState(() => queryDefault(searchParams, "jobId"));
  const [resumeId, setResumeId] = useState(() => queryDefault(searchParams, "resumeId"));
  const [resumeFileId, setResumeFileId] = useState("");
  const [documentId, setDocumentId] = useState(() => queryDefault(searchParams, "documentId"));
  const [versionId, setVersionId] = useState("");
  const [status, setStatus] = useState<ApplicationStatus>("PREPARING");
  const [priority, setPriority] = useState<ApplicationPriority>("NORMAL");
  const [channel, setChannel] = useState<ApplicationChannel>("COMPANY_SITE");
  const [plannedApplyAt, setPlannedApplyAt] = useState("");
  const [appliedAt, setAppliedAt] = useState("");
  const [applicationUrl, setApplicationUrl] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [contactPhone, setContactPhone] = useState("");

  const optionsQuery = useQuery({
    queryKey: ["application-options"],
    queryFn: getApplicationOptions,
    retry: false,
  });
  const options = optionsQuery.data?.data;
  const filteredVersions = options?.application_document_versions.filter((version) => {
    if (!documentId) return true;
    return String(version.metadata.document_id) === documentId;
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createApplication({
        job_id: optionalNumber(jobId),
        resume_id: optionalNumber(resumeId),
        resume_file_id: optionalNumber(resumeFileId),
        application_document_id: optionalNumber(documentId),
        application_document_version_id: optionalNumber(versionId),
        status,
        priority,
        application_channel: channel,
        planned_apply_at: plannedApplyAt ? new Date(plannedApplyAt).toISOString() : null,
        applied_at: appliedAt ? new Date(appliedAt).toISOString() : null,
        application_url: applicationUrl || null,
        contact_name: contactName || null,
        contact_email: contactEmail || null,
        contact_phone: contactPhone || null,
      }),
    onSuccess: (response) => router.push(`/applications/${response.data.id}`),
  });

  return (
    <div className="panel max-w-none">
      <form
        className="grid gap-5"
        onSubmit={(event) => {
          event.preventDefault();
          createMutation.mutate();
        }}
      >
        <div>
          <p className="text-sm font-semibold text-slate-500">Application Tracking</p>
          <h1 className="mt-1 text-2xl font-bold text-slate-950">지원 항목 만들기</h1>
          <p className="mt-2 text-sm text-slate-600">채용공고, 이력서, 제출 문서 버전을 선택해 지원 현황을 관리합니다.</p>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <SourceSelector label="채용공고" value={jobId} options={options?.jobs} onChange={setJobId} />
          <SourceSelector label="이력서" value={resumeId} options={options?.resumes} onChange={setResumeId} />
          <SourceSelector label="이력서 파일" value={resumeFileId} options={options?.resume_files} onChange={setResumeFileId} />
          <SourceSelector label="지원 문서" value={documentId} options={options?.application_documents} onChange={setDocumentId} />
          <SourceSelector label="제출 문서 버전" value={versionId} options={filteredVersions} onChange={setVersionId} />
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <Select label="상태" value={status} onChange={(value) => setStatus(value as ApplicationStatus)}>
            {applicationStatusOptions.map((value) => (
              <option key={value} value={value}>{applicationStatusLabels[value]}</option>
            ))}
          </Select>
          <Select label="우선순위" value={priority} onChange={(value) => setPriority(value as ApplicationPriority)}>
            {applicationPriorityOptions.map((value) => (
              <option key={value} value={value}>{applicationPriorityLabels[value]}</option>
            ))}
          </Select>
          <Select label="지원 경로" value={channel} onChange={(value) => setChannel(value as ApplicationChannel)}>
            {applicationChannelOptions.map((value) => (
              <option key={value} value={value}>{applicationChannelLabels[value]}</option>
            ))}
          </Select>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <Input label="지원 예정일" type="datetime-local" value={plannedApplyAt} onChange={setPlannedApplyAt} />
          <Input label="지원 완료일" type="datetime-local" value={appliedAt} onChange={setAppliedAt} />
          <Input label="지원 URL" value={applicationUrl} onChange={setApplicationUrl} placeholder="https://..." />
          <Input label="담당자 이름" value={contactName} onChange={setContactName} />
          <Input label="담당자 이메일" value={contactEmail} onChange={setContactEmail} />
          <Input label="담당자 전화번호" value={contactPhone} onChange={setContactPhone} />
        </div>

        {optionsQuery.error ? <p className="text-sm text-rose-700">{optionsQuery.error.message}</p> : null}
        {createMutation.error ? <p className="text-sm text-rose-700">{createMutation.error.message}</p> : null}
        <button className="button-primary" type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? "저장 중..." : "지원 현황에 추가"}
        </button>
      </form>
    </div>
  );
}

function Select({ label, value, onChange, children }: { label: string; value: string; onChange: (value: string) => void; children: React.ReactNode }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <select className="input" value={value} onChange={(event) => onChange(event.target.value)}>
        {children}
      </select>
    </label>
  );
}

function Input({ label, value, onChange, type = "text", placeholder }: { label: string; value: string; onChange: (value: string) => void; type?: string; placeholder?: string }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <input className="input" type={type} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
