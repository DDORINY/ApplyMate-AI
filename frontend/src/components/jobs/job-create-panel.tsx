"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm, type UseFormRegisterReturn } from "react-hook-form";
import { z } from "zod";

import { createJob, importJobUrl } from "@/lib/api/job";
import type { CompanySize, JobDeadlineType, JobEmploymentType, JobPostingStatus, JobWorkType } from "@/types/job";
import { companySizeLabels, deadlineTypeLabels, employmentTypeLabels, statusLabels, workTypeLabels } from "./job-labels";

const manualSchema = z
  .object({
    company_name: z.string().min(1, "기업명을 입력해 주세요."),
    company_website_url: z.string().url("URL 형식이 올바르지 않습니다.").optional().or(z.literal("")),
    company_size: z.string(),
    title: z.string().min(1, "공고 제목을 입력해 주세요."),
    position: z.string().optional(),
    employment_type: z.string(),
    career_requirement: z.string().optional(),
    education_requirement: z.string().optional(),
    location: z.string().optional(),
    work_type: z.string(),
    salary_min: z
      .string()
      .regex(/^\d*$/, "숫자만 입력할 수 있습니다.")
      .optional(),
    salary_max: z
      .string()
      .regex(/^\d*$/, "숫자만 입력할 수 있습니다.")
      .optional(),
    salary_text: z.string().optional(),
    description: z.string().optional(),
    requirements: z.string().optional(),
    preferred_qualifications: z.string().optional(),
    benefits: z.string().optional(),
    recruitment_process: z.string().optional(),
    deadline_at: z.string().optional(),
    deadline_type: z.string(),
    status: z.string(),
    is_favorite: z.boolean(),
    notes: z.string().optional(),
  })
  .refine(
    (value) =>
      value.salary_min === "" ||
      value.salary_max === "" ||
      value.salary_min === undefined ||
      value.salary_max === undefined ||
      Number(value.salary_min) <= Number(value.salary_max),
    { path: ["salary_max"], message: "최대 급여는 최소 급여보다 작을 수 없습니다." },
  );

const urlSchema = z.object({
  url: z.string().url("채용공고 URL을 입력해 주세요."),
  company_name: z.string().optional(),
  title: z.string().optional(),
  description: z.string().optional(),
});

type ManualValues = z.infer<typeof manualSchema>;
type UrlValues = z.infer<typeof urlSchema>;

export function JobCreatePanel() {
  const router = useRouter();
  const [mode, setMode] = useState<"manual" | "url">("manual");
  const manualForm = useForm<ManualValues>({
    resolver: zodResolver(manualSchema),
    defaultValues: {
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
    },
  });
  const urlForm = useForm<UrlValues>({
    resolver: zodResolver(urlSchema),
    defaultValues: { url: "", company_name: "", title: "", description: "" },
  });

  const createMutation = useMutation({
    mutationFn: (values: ManualValues) =>
      createJob({
        company_name: values.company_name,
        company_website_url: values.company_website_url || null,
        company_size: values.company_size as CompanySize,
        title: values.title,
        position: values.position || null,
        employment_type: values.employment_type as JobEmploymentType,
        career_requirement: values.career_requirement || null,
        education_requirement: values.education_requirement || null,
        location: values.location || null,
        work_type: values.work_type as JobWorkType,
        salary_min: values.salary_min === "" ? null : Number(values.salary_min),
        salary_max: values.salary_max === "" ? null : Number(values.salary_max),
        salary_text: values.salary_text || null,
        description: values.description || null,
        requirements: values.requirements || null,
        preferred_qualifications: values.preferred_qualifications || null,
        benefits: values.benefits || null,
        recruitment_process: values.recruitment_process || null,
        deadline_at: values.deadline_at || null,
        deadline_type: values.deadline_type as JobDeadlineType,
        status: values.status as JobPostingStatus,
        is_favorite: values.is_favorite,
        source_type: "MANUAL",
        source_url: null,
        notes: values.notes || null,
      }),
    onSuccess: (response) => router.push(`/jobs/${response.data.id}`),
  });

  const importMutation = useMutation({
    mutationFn: (values: UrlValues) =>
      importJobUrl({
        url: values.url,
        company_name: values.company_name || null,
        title: values.title || null,
        description: values.description || null,
      }),
    onSuccess: (response) => router.push(`/jobs/${response.data.job.id}`),
  });

  return (
    <div className="panel max-w-none">
      <div className="flex flex-wrap gap-2">
        <button className={mode === "manual" ? "button-primary" : "button-secondary"} type="button" onClick={() => setMode("manual")}>
          직접 입력
        </button>
        <button className={mode === "url" ? "button-primary" : "button-secondary"} type="button" onClick={() => setMode("url")}>
          URL 등록
        </button>
      </div>

      {mode === "manual" ? (
        <form className="mt-6 grid gap-4" onSubmit={manualForm.handleSubmit((values) => createMutation.mutate(values))}>
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="기업명" error={manualForm.formState.errors.company_name?.message}>
              <input className="input" {...manualForm.register("company_name")} />
            </Field>
            <Field label="기업 홈페이지" error={manualForm.formState.errors.company_website_url?.message}>
              <input className="input" placeholder="https://example.com" {...manualForm.register("company_website_url")} />
            </Field>
            <SelectField label="기업 규모" register={manualForm.register("company_size")}>
              {optionEntries(companySizeLabels)}
            </SelectField>
            <Field label="공고 제목" error={manualForm.formState.errors.title?.message}>
              <input className="input" {...manualForm.register("title")} />
            </Field>
            <Field label="직무">
              <input className="input" {...manualForm.register("position")} />
            </Field>
            <SelectField label="고용 형태" register={manualForm.register("employment_type")}>
              {optionEntries(employmentTypeLabels)}
            </SelectField>
            <Field label="경력 조건">
              <input className="input" placeholder="예: 신입, 3년 이상" {...manualForm.register("career_requirement")} />
            </Field>
            <Field label="학력 조건">
              <input className="input" placeholder="예: 학력 무관, 대졸 이상" {...manualForm.register("education_requirement")} />
            </Field>
            <Field label="근무 지역">
              <input className="input" {...manualForm.register("location")} />
            </Field>
            <SelectField label="근무 형태" register={manualForm.register("work_type")}>
              {optionEntries(workTypeLabels)}
            </SelectField>
            <Field label="최소 급여" error={manualForm.formState.errors.salary_min?.message}>
              <input className="input" type="number" {...manualForm.register("salary_min")} />
            </Field>
            <Field label="최대 급여" error={manualForm.formState.errors.salary_max?.message}>
              <input className="input" type="number" {...manualForm.register("salary_max")} />
            </Field>
            <Field label="급여 설명">
              <input className="input" {...manualForm.register("salary_text")} />
            </Field>
            <Field label="마감일">
              <input className="input" type="datetime-local" {...manualForm.register("deadline_at")} />
            </Field>
            <SelectField label="마감 유형" register={manualForm.register("deadline_type")}>
              {optionEntries(deadlineTypeLabels)}
            </SelectField>
            <SelectField label="상태" register={manualForm.register("status")}>
              {optionEntries(statusLabels)}
            </SelectField>
          </div>
          <Textarea label="주요 업무" register={manualForm.register("description")} />
          <Textarea label="필수 조건" register={manualForm.register("requirements")} />
          <Textarea label="우대 조건" register={manualForm.register("preferred_qualifications")} />
          <Textarea label="복지" register={manualForm.register("benefits")} />
          <Textarea label="채용 절차" register={manualForm.register("recruitment_process")} />
          <Textarea label="메모" register={manualForm.register("notes")} />
          <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
            <input type="checkbox" {...manualForm.register("is_favorite")} />
            관심 공고로 표시
          </label>
          <MutationMessage error={createMutation.error?.message} />
          <button className="button-primary w-fit" type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? "등록 중..." : "채용공고 등록"}
          </button>
        </form>
      ) : (
        <form className="mt-6 grid gap-4" onSubmit={urlForm.handleSubmit((values) => importMutation.mutate(values))}>
          <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
            URL 등록은 SSRF 방어와 HTML 크기/형식 제한을 적용합니다. 자동 추출보다 사용자가 입력한 기업명, 제목, 본문이 우선됩니다.
          </p>
          <Field label="채용공고 URL" error={urlForm.formState.errors.url?.message}>
            <input className="input" placeholder="https://example.com/jobs/123" {...urlForm.register("url")} />
          </Field>
          <Field label="기업명 선택 입력">
            <input className="input" {...urlForm.register("company_name")} />
          </Field>
          <Field label="공고 제목 선택 입력">
            <input className="input" {...urlForm.register("title")} />
          </Field>
          <Textarea label="공고 본문 선택 입력" register={urlForm.register("description")} />
          <MutationMessage error={importMutation.error?.message} />
          <button className="button-primary w-fit" type="submit" disabled={importMutation.isPending}>
            {importMutation.isPending ? "가져오는 중..." : "URL로 등록"}
          </button>
        </form>
      )}
    </div>
  );
}

function optionEntries(labels: Record<string, string>) {
  return Object.entries(labels).map(([value, label]) => (
    <option value={value} key={value}>
      {label}
    </option>
  ));
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      {children}
      {error ? <span className="text-sm font-normal text-rose-700">{error}</span> : null}
    </label>
  );
}

function SelectField({
  label,
  register,
  children,
}: {
  label: string;
  register: UseFormRegisterReturn;
  children: React.ReactNode;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <select className="input" {...register}>
        {children}
      </select>
    </label>
  );
}

function Textarea({ label, register }: { label: string; register: UseFormRegisterReturn }) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <textarea className="input min-h-28" {...register} />
    </label>
  );
}

function MutationMessage({ error }: { error?: string }) {
  return error ? <p className="text-sm text-rose-700">{error}</p> : null;
}
