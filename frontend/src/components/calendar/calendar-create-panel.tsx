"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import { SourceSelector } from "@/components/applications/source-selector";
import { createCalendarEvent, getCalendarOptions } from "@/lib/api/calendar";
import type { ScheduleConfidence, ScheduleEventStatus, ScheduleEventType } from "@/types/calendar";
import {
  scheduleConfidenceLabels,
  scheduleConfidenceOptions,
  scheduleEventStatusLabels,
  scheduleEventStatusOptions,
  scheduleEventTypeLabels,
  scheduleEventTypeOptions,
} from "./calendar-labels";

type FormState = {
  application_id: string;
  job_id: string;
  title: string;
  description: string;
  event_type: ScheduleEventType;
  status: ScheduleEventStatus;
  confidence: ScheduleConfidence;
  start_at: string;
  end_at: string;
  all_day: boolean;
  timezone: string;
  location: string;
  online_url: string;
  reminder_minutes: string;
};

export function CalendarCreatePanel() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const defaultStart = useMemo(() => toDateTimeLocal(new Date(Date.now() + 24 * 60 * 60 * 1000)), []);
  const defaultEnd = useMemo(() => toDateTimeLocal(new Date(Date.now() + 25 * 60 * 60 * 1000)), []);
  const [form, setForm] = useState<FormState>({
    application_id: searchParams.get("applicationId") ?? "",
    job_id: searchParams.get("jobId") ?? "",
    title: "",
    description: "",
    event_type: "USER_EVENT",
    status: "SCHEDULED",
    confidence: "USER_INPUT",
    start_at: defaultStart,
    end_at: defaultEnd,
    all_day: false,
    timezone: "Asia/Seoul",
    location: "",
    online_url: "",
    reminder_minutes: "60",
  });

  const optionsQuery = useQuery({
    queryKey: ["calendar-options"],
    queryFn: getCalendarOptions,
    retry: false,
  });
  const mutation = useMutation({
    mutationFn: () =>
      createCalendarEvent({
        application_id: form.application_id ? Number(form.application_id) : null,
        job_id: form.job_id ? Number(form.job_id) : null,
        title: form.title,
        description: nullable(form.description),
        event_type: form.event_type,
        status: form.status,
        confidence: form.confidence,
        start_at: toIso(form.start_at),
        end_at: toIso(form.end_at),
        all_day: form.all_day,
        timezone: form.timezone,
        location: nullable(form.location),
        online_url: nullable(form.online_url),
        reminders: form.reminder_minutes ? [{ reminder_type: "IN_APP", minutes_before: Number(form.reminder_minutes) }] : [],
      }),
    onSuccess: (response) => router.push(`/calendar/events/${response.data.id}`),
  });

  return (
    <section className="panel max-w-none">
      <h1 className="text-2xl font-bold text-slate-950">일정 추가</h1>
      <p className="mt-2 text-sm text-slate-600">지원 항목이나 채용공고와 연결해 마감·면접·결과 발표 일정을 관리합니다.</p>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <SourceSelector
          label="연결 지원 항목"
          value={form.application_id}
          options={optionsQuery.data?.data.applications}
          onChange={(value) => setField("application_id", value)}
          placeholder="지원 항목 선택 안 함"
        />
        <SourceSelector
          label="연결 채용공고"
          value={form.job_id}
          options={optionsQuery.data?.data.jobs}
          onChange={(value) => setField("job_id", value)}
          placeholder="채용공고 선택 안 함"
        />
        <Field label="제목" value={form.title} onChange={(value) => setField("title", value)} />
        <Select label="일정 유형" value={form.event_type} options={scheduleEventTypeLabels} onChange={(value) => setField("event_type", value as ScheduleEventType)} />
        <Select label="상태" value={form.status} options={scheduleEventStatusLabels} onChange={(value) => setField("status", value as ScheduleEventStatus)} />
        <Select label="신뢰도" value={form.confidence} options={scheduleConfidenceLabels} onChange={(value) => setField("confidence", value as ScheduleConfidence)} />
        <Field label="시작" type="datetime-local" value={form.start_at} onChange={(value) => setField("start_at", value)} />
        <Field label="종료" type="datetime-local" value={form.end_at} onChange={(value) => setField("end_at", value)} />
        <Field label="타임존" value={form.timezone} onChange={(value) => setField("timezone", value)} />
        <Field label="장소" value={form.location} onChange={(value) => setField("location", value)} />
        <Field label="온라인 URL" value={form.online_url} placeholder="https://meet.example.com" onChange={(value) => setField("online_url", value)} />
        <label className="grid gap-2 text-sm font-medium text-slate-700">
          앱 내 알림
          <select className="input" value={form.reminder_minutes} onChange={(event) => setField("reminder_minutes", event.target.value)}>
            <option value="">알림 없음</option>
            <option value="10">10분 전</option>
            <option value="30">30분 전</option>
            <option value="60">1시간 전</option>
            <option value="180">3시간 전</option>
            <option value="1440">1일 전</option>
            <option value="4320">3일 전</option>
            <option value="10080">1주 전</option>
          </select>
        </label>
      </div>

      <label className="mt-4 flex items-center gap-2 text-sm font-medium text-slate-700">
        <input checked={form.all_day} type="checkbox" onChange={(event) => setField("all_day", event.target.checked)} />
        종일 일정
      </label>

      <label className="mt-4 grid gap-2 text-sm font-medium text-slate-700">
        설명
        <textarea className="input min-h-28" value={form.description} onChange={(event) => setField("description", event.target.value)} />
      </label>

      <div className="mt-6 flex flex-wrap gap-3">
        <button className="button-primary" type="button" disabled={mutation.isPending || !form.title.trim()} onClick={() => mutation.mutate()}>
          {mutation.isPending ? "저장 중..." : "일정 저장"}
        </button>
        <button className="button-secondary" type="button" onClick={() => router.push("/calendar")}>
          취소
        </button>
      </div>
      {mutation.error ? <p className="mt-3 text-sm text-rose-700">{mutation.error.message}</p> : null}
    </section>
  );

  function setField<TKey extends keyof FormState>(key: TKey, value: FormState[TKey]) {
    setForm((current) => ({ ...current, [key]: value }));
  }
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
      <input className="input" placeholder={placeholder} type={type} value={value} onChange={(event) => onChange(event.target.value)} />
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
  const optionValues =
    options === scheduleEventTypeLabels
      ? scheduleEventTypeOptions
      : options === scheduleEventStatusLabels
        ? scheduleEventStatusOptions
        : scheduleConfidenceOptions;
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <select className="input" value={value} onChange={(event) => onChange(event.target.value)}>
        {optionValues.map((optionValue) => (
          <option value={optionValue} key={optionValue}>
            {options[optionValue as TValue]}
          </option>
        ))}
      </select>
    </label>
  );
}

function nullable(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function toDateTimeLocal(value: Date) {
  const offset = value.getTimezoneOffset();
  const local = new Date(value.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 16);
}

function toIso(value: string) {
  return new Date(value).toISOString();
}
