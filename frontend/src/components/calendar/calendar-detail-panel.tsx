"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import {
  archiveCalendarEvent,
  changeCalendarEventStatus,
  createCalendarEventReminder,
  getCalendarEvent,
  listCalendarEventHistory,
  listCalendarEventReminders,
} from "@/lib/api/calendar";
import type { ScheduleEventStatus } from "@/types/calendar";
import {
  formatRemaining,
  formatScheduleDateTime,
  scheduleConfidenceLabels,
  scheduleEventStatusLabels,
  scheduleEventStatusOptions,
  scheduleEventTypeLabels,
  scheduleReminderTypeLabels,
} from "./calendar-labels";

export function CalendarDetailPanel({ eventId }: { eventId: number }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [nextStatus, setNextStatus] = useState<ScheduleEventStatus>("COMPLETED");
  const [reminderMinutes, setReminderMinutes] = useState("60");

  const eventQuery = useQuery({
    queryKey: ["calendar-event", eventId],
    queryFn: () => getCalendarEvent(eventId),
    retry: false,
  });
  const remindersQuery = useQuery({
    queryKey: ["calendar-event-reminders", eventId],
    queryFn: () => listCalendarEventReminders(eventId),
    retry: false,
  });
  const historyQuery = useQuery({
    queryKey: ["calendar-event-history", eventId],
    queryFn: () => listCalendarEventHistory(eventId),
    retry: false,
  });
  const statusMutation = useMutation({
    mutationFn: () => changeCalendarEventStatus(eventId, nextStatus),
    onSuccess: (response) => {
      queryClient.setQueryData(["calendar-event", eventId], response);
      queryClient.invalidateQueries({ queryKey: ["calendar-event-reminders", eventId] });
      queryClient.invalidateQueries({ queryKey: ["calendar-event-history", eventId] });
      queryClient.invalidateQueries({ queryKey: ["calendar-events"] });
    },
  });
  const reminderMutation = useMutation({
    mutationFn: () => createCalendarEventReminder(eventId, { reminder_type: "IN_APP", minutes_before: Number(reminderMinutes) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar-event", eventId] });
      queryClient.invalidateQueries({ queryKey: ["calendar-event-reminders", eventId] });
      queryClient.invalidateQueries({ queryKey: ["calendar-event-history", eventId] });
    },
  });
  const archiveMutation = useMutation({
    mutationFn: () => archiveCalendarEvent(eventId),
    onSuccess: () => router.push("/calendar"),
  });

  const event = eventQuery.data?.data;

  if (eventQuery.isLoading) {
    return <div className="panel max-w-none">일정을 불러오는 중입니다.</div>;
  }
  if (eventQuery.error) {
    return <div className="panel max-w-none text-rose-700">{eventQuery.error.message}</div>;
  }
  if (!event) {
    return <div className="panel max-w-none">일정을 찾을 수 없습니다.</div>;
  }

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link className="button-secondary" href="/calendar">
          일정 목록
        </Link>
        <button
          className="button-secondary border-rose-200 text-rose-700"
          type="button"
          disabled={archiveMutation.isPending}
          onClick={() => archiveMutation.mutate()}
        >
          일정 보관
        </button>
      </div>

      <section className="panel max-w-none">
        <p className="text-sm font-semibold text-sky-700">{scheduleEventTypeLabels[event.event_type]}</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">{event.title}</h1>
        <div className="mt-4 grid gap-3 text-sm text-slate-700 sm:grid-cols-2 lg:grid-cols-3">
          <Info label="상태" value={scheduleEventStatusLabels[event.effective_status]} />
          <Info label="신뢰도" value={scheduleConfidenceLabels[event.confidence]} />
          <Info label="시작" value={formatScheduleDateTime(event.start_at)} />
          <Info label="종료" value={formatScheduleDateTime(event.end_at)} />
          <Info label="남은 시간" value={formatRemaining(event.hours_remaining)} />
          <Info label="타임존" value={event.timezone} />
          <Info label="장소" value={event.location ?? "-"} />
          <Info label="알림" value={`${event.reminders_count}개`} />
          <Info label="종일" value={event.all_day ? "예" : "아니오"} />
        </div>
        {event.description ? <p className="mt-4 whitespace-pre-wrap text-sm text-slate-700">{event.description}</p> : null}
        <div className="mt-5 flex flex-wrap gap-2">
          {event.application_id ? (
            <Link className="button-secondary" href={`/applications/${event.application_id}`}>
              연결 지원 항목
            </Link>
          ) : null}
          {event.job_id ? (
            <Link className="button-secondary" href={`/jobs/${event.job_id}`}>
              연결 채용공고
            </Link>
          ) : null}
          {event.online_url ? (
            <a className="button-secondary" href={event.online_url} rel="noreferrer" target="_blank">
              온라인 링크 열기
            </a>
          ) : null}
        </div>
        {event.has_conflict ? (
          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            <p className="font-semibold">겹치는 일정이 있습니다.</p>
            <ul className="mt-2 list-disc pl-5">
              {event.conflicting_events.map((item) => (
                <li key={item.id}>
                  {item.title} · {formatScheduleDateTime(item.start_at)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">상태 변경</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-[220px_auto]">
          <select className="input" value={nextStatus} onChange={(input) => setNextStatus(input.target.value as ScheduleEventStatus)}>
            {scheduleEventStatusOptions.map((value) => (
              <option key={value} value={value}>
                {scheduleEventStatusLabels[value]}
              </option>
            ))}
          </select>
          <button className="button-primary" type="button" disabled={statusMutation.isPending} onClick={() => statusMutation.mutate()}>
            상태 변경
          </button>
        </div>
        {statusMutation.error ? <p className="mt-3 text-sm text-rose-700">{statusMutation.error.message}</p> : null}
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">알림</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-[220px_auto]">
          <select className="input" value={reminderMinutes} onChange={(input) => setReminderMinutes(input.target.value)}>
            <option value="10">10분 전</option>
            <option value="30">30분 전</option>
            <option value="60">1시간 전</option>
            <option value="180">3시간 전</option>
            <option value="1440">1일 전</option>
            <option value="4320">3일 전</option>
            <option value="10080">1주 전</option>
          </select>
          <button className="button-primary" type="button" disabled={reminderMutation.isPending} onClick={() => reminderMutation.mutate()}>
            알림 추가
          </button>
        </div>
        <div className="mt-4 grid gap-2">
          {remindersQuery.data?.data.map((reminder) => (
            <div className="rounded-2xl border border-slate-200 p-3 text-sm text-slate-700" key={reminder.id}>
              {scheduleReminderTypeLabels[reminder.reminder_type]} · {reminder.minutes_before}분 전 · {reminder.status}
              <p className="mt-1 text-xs text-slate-500">{formatScheduleDateTime(reminder.scheduled_at)}</p>
            </div>
          ))}
        </div>
        {reminderMutation.error ? <p className="mt-3 text-sm text-rose-700">{reminderMutation.error.message}</p> : null}
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">변경 이력</h2>
        <ol className="mt-4 grid gap-3">
          {historyQuery.data?.data.map((item) => (
            <li className="rounded-2xl border border-slate-200 p-3" key={item.id}>
              <p className="text-sm font-semibold text-slate-700">{item.action}</p>
              <p className="mt-1 text-xs text-slate-500">
                {formatScheduleDateTime(item.created_at)} · {item.source}
              </p>
              {item.changed_fields?.length ? <p className="mt-2 text-sm text-slate-600">변경 필드: {item.changed_fields.join(", ")}</p> : null}
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-semibold text-slate-500">{label}</p>
      <p className="mt-1">{value}</p>
    </div>
  );
}
