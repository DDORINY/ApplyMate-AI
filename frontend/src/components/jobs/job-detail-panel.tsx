"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { deleteJob, getJob, updateJob } from "@/lib/api/job";
import type {
  CompanySize,
  JobDeadlineType,
  JobEmploymentType,
  JobPostingPayload,
  JobPostingStatus,
  JobWorkType,
} from "@/types/job";
import { JobAnalysisPanel } from "./job-analysis-panel";
import { JobMatchPanel } from "./job-match-panel";
import {
  companySizeLabels,
  deadlineTypeLabels,
  employmentTypeLabels,
  sourceTypeLabels,
  statusLabels,
  workTypeLabels,
} from "./job-labels";

type JobDetailPanelProps = {
  jobId: number;
};

type FormState = {
  company_name: string;
  company_website_url: string;
  company_size: CompanySize;
  title: string;
  position: string;
  employment_type: JobEmploymentType;
  career_requirement: string;
  education_requirement: string;
  location: string;
  work_type: JobWorkType;
  salary_min: string;
  salary_max: string;
  salary_text: string;
  description: string;
  requirements: string;
  preferred_qualifications: string;
  benefits: string;
  recruitment_process: string;
  deadline_at: string;
  deadline_type: JobDeadlineType;
  status: JobPostingStatus;
  is_favorite: boolean;
  notes: string;
};

const defaultForm: FormState = {
  company_name: "",
  company_website_url: "",
  company_size: "UNKNOWN",
  title: "",
  position: "",
  employment_type: "UNKNOWN",
  career_requirement: "",
  education_requirement: "",
  location: "",
  work_type: "UNKNOWN",
  salary_min: "",
  salary_max: "",
  salary_text: "",
  description: "",
  requirements: "",
  preferred_qualifications: "",
  benefits: "",
  recruitment_process: "",
  deadline_at: "",
  deadline_type: "UNKNOWN",
  status: "SAVED",
  is_favorite: false,
  notes: "",
};

export function JobDetailPanel({ jobId }: JobDetailPanelProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<FormState>(defaultForm);

  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => getJob(jobId),
    retry: false,
  });

  useEffect(() => {
    if (jobQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [jobQuery.error, router]);

  useEffect(() => {
    const job = jobQuery.data?.data;
    if (!job) {
      return;
    }
    setForm({
      company_name: job.company.name,
      company_website_url: job.company.website_url ?? "",
      company_size: job.company.company_size,
      title: job.title,
      position: job.position ?? "",
      employment_type: job.employment_type,
      career_requirement: job.career_requirement ?? "",
      education_requirement: job.education_requirement ?? "",
      location: job.location ?? "",
      work_type: job.work_type,
      salary_min: job.salary_min?.toString() ?? "",
      salary_max: job.salary_max?.toString() ?? "",
      salary_text: job.salary_text ?? "",
      description: job.description ?? "",
      requirements: job.requirements ?? "",
      preferred_qualifications: job.preferred_qualifications ?? "",
      benefits: job.benefits ?? "",
      recruitment_process: job.recruitment_process ?? "",
      deadline_at: toDateTimeLocal(job.deadline_at),
      deadline_type: job.deadline_type,
      status: job.status,
      is_favorite: job.is_favorite,
      notes: job.notes ?? "",
    });
  }, [jobQuery.data]);

  const updateMutation = useMutation({
    mutationFn: () => updateJob(jobId, buildPayload(form)),
    onSuccess: (response) => {
      queryClient.setQueryData(["job", jobId], response);
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      router.push("/jobs");
    },
  });

  const job = jobQuery.data?.data;

  if (jobQuery.isLoading) {
    return <div className="panel max-w-none">채용공고를 불러오는 중입니다.</div>;
  }

  if (jobQuery.error) {
    return <div className="panel max-w-none text-rose-700">{jobQuery.error.message}</div>;
  }

  if (!job) {
    return <div className="panel max-w-none">채용공고를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link className="button-secondary" href="/jobs">
          목록으로
        </Link>
        <Link className="button-primary" href="/jobs/new">
          새 공고 등록
        </Link>
      </div>

      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-sky-700">{sourceTypeLabels[job.source_type]}</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">{job.title}</h1>
            <p className="mt-2 text-slate-600">
              {job.company.name} · {statusLabels[job.status]} · {job.is_favorite ? "관심 공고" : "일반 공고"}
            </p>
            {job.source_url ? (
              <a
                className="mt-3 inline-flex text-sm font-medium text-sky-700 hover:underline"
                href={job.source_url}
                target="_blank"
                rel="noreferrer"
              >
                원문 공고 열기
              </a>
            ) : null}
          </div>
          <button
            className="button-secondary"
            type="button"
            onClick={() => setForm((value) => ({ ...value, is_favorite: !value.is_favorite }))}
          >
            {form.is_favorite ? "★ 관심" : "☆ 관심"}
          </button>
        </div>
      </section>

      <JobAnalysisPanel jobId={jobId} />
      <JobMatchPanel jobId={jobId} />

      <section className="panel max-w-none">
        <h2 className="text-xl font-semibold text-slate-950">채용공고 수정</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <Field label="기업명" value={form.company_name} onChange={(value) => setField("company_name", value)} />
          <Field
            label="기업 홈페이지"
            value={form.company_website_url}
            placeholder="https://example.com"
            onChange={(value) => setField("company_website_url", value)}
          />
          <Select
            label="기업 규모"
            value={form.company_size}
            onChange={(value) => setField("company_size", value as CompanySize)}
            options={companySizeLabels}
          />
          <Field label="공고 제목" value={form.title} onChange={(value) => setField("title", value)} />
          <Field label="직무" value={form.position} onChange={(value) => setField("position", value)} />
          <Select
            label="고용 형태"
            value={form.employment_type}
            onChange={(value) => setField("employment_type", value as JobEmploymentType)}
            options={employmentTypeLabels}
          />
          <Field label="경력 조건" value={form.career_requirement} onChange={(value) => setField("career_requirement", value)} />
          <Field label="학력 조건" value={form.education_requirement} onChange={(value) => setField("education_requirement", value)} />
          <Field label="근무 지역" value={form.location} onChange={(value) => setField("location", value)} />
          <Select
            label="근무 형태"
            value={form.work_type}
            onChange={(value) => setField("work_type", value as JobWorkType)}
            options={workTypeLabels}
          />
          <Field label="최소 급여" value={form.salary_min} type="number" onChange={(value) => setField("salary_min", value)} />
          <Field label="최대 급여" value={form.salary_max} type="number" onChange={(value) => setField("salary_max", value)} />
          <Field label="급여 설명" value={form.salary_text} onChange={(value) => setField("salary_text", value)} />
          <Field
            label="마감일"
            value={form.deadline_at}
            type="datetime-local"
            onChange={(value) => setField("deadline_at", value)}
          />
          <Select
            label="마감 유형"
            value={form.deadline_type}
            onChange={(value) => setField("deadline_type", value as JobDeadlineType)}
            options={deadlineTypeLabels}
          />
          <Select
            label="상태"
            value={form.status}
            onChange={(value) => setField("status", value as JobPostingStatus)}
            options={statusLabels}
          />
        </div>
        <Textarea label="주요 업무" value={form.description} onChange={(value) => setField("description", value)} />
        <Textarea label="필수 조건" value={form.requirements} onChange={(value) => setField("requirements", value)} />
        <Textarea
          label="우대 조건"
          value={form.preferred_qualifications}
          onChange={(value) => setField("preferred_qualifications", value)}
        />
        <Textarea label="복지" value={form.benefits} onChange={(value) => setField("benefits", value)} />
        <Textarea label="채용 절차" value={form.recruitment_process} onChange={(value) => setField("recruitment_process", value)} />
        <Textarea label="메모" value={form.notes} onChange={(value) => setField("notes", value)} />

        <div className="mt-5 flex flex-wrap gap-3">
          <button className="button-primary" type="button" disabled={updateMutation.isPending} onClick={() => updateMutation.mutate()}>
            {updateMutation.isPending ? "저장 중..." : "변경사항 저장"}
          </button>
          <button
            className="button-secondary border-rose-200 text-rose-700"
            type="button"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (window.confirm("이 채용공고를 삭제할까요?")) {
                deleteMutation.mutate();
              }
            }}
          >
            {deleteMutation.isPending ? "삭제 중..." : "삭제"}
          </button>
        </div>
        {updateMutation.error ? <p className="mt-3 text-sm text-rose-700">{updateMutation.error.message}</p> : null}
        {deleteMutation.error ? <p className="mt-3 text-sm text-rose-700">{deleteMutation.error.message}</p> : null}
        {updateMutation.isSuccess ? <p className="mt-3 text-sm text-emerald-700">저장되었습니다.</p> : null}
      </section>
    </div>
  );

  function setField<TKey extends keyof FormState>(key: TKey, value: FormState[TKey]) {
    setForm((current) => ({ ...current, [key]: value }));
  }
}

function buildPayload(form: FormState): Partial<JobPostingPayload> {
  return {
    company_name: form.company_name,
    company_website_url: nullable(form.company_website_url),
    company_size: form.company_size,
    title: form.title,
    position: nullable(form.position),
    employment_type: form.employment_type,
    career_requirement: nullable(form.career_requirement),
    education_requirement: nullable(form.education_requirement),
    location: nullable(form.location),
    work_type: form.work_type,
    salary_min: form.salary_min === "" ? null : Number(form.salary_min),
    salary_max: form.salary_max === "" ? null : Number(form.salary_max),
    salary_text: nullable(form.salary_text),
    description: nullable(form.description),
    requirements: nullable(form.requirements),
    preferred_qualifications: nullable(form.preferred_qualifications),
    benefits: nullable(form.benefits),
    recruitment_process: nullable(form.recruitment_process),
    deadline_at: nullable(form.deadline_at),
    deadline_type: form.deadline_type,
    status: form.status,
    is_favorite: form.is_favorite,
    notes: nullable(form.notes),
  };
}

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function toDateTimeLocal(value: string | null) {
  if (!value) {
    return "";
  }
  return value.slice(0, 16);
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <input
        className="input"
        placeholder={placeholder}
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function Select<TValue extends string>({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: TValue;
  onChange: (value: string) => void;
  options: Record<TValue, string>;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <select className="input" value={value} onChange={(event) => onChange(event.target.value)}>
        {Object.entries(options).map(([optionValue, labelText]) => (
          <option value={optionValue} key={optionValue}>
            {labelText as string}
          </option>
        ))}
      </select>
    </label>
  );
}

function Textarea({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="mt-4 grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <textarea className="input min-h-28" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
