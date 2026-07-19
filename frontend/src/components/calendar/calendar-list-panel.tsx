"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import { listCalendarEvents, listUpcomingCalendarEvents } from "@/lib/api/calendar";
import type { ScheduleEventStatus, ScheduleEventType } from "@/types/calendar";
import {
  formatRemaining,
  formatScheduleDateTime,
  scheduleEventStatusLabels,
  scheduleEventStatusOptions,
  scheduleEventTypeLabels,
  scheduleEventTypeOptions,
} from "./calendar-labels";

type ViewMode = "month" | "week" | "list";

export function CalendarListPanel() {
  const searchParams = useSearchParams();
  const applicationId = searchParams.get("applicationId") ?? "";
  const jobId = searchParams.get("jobId") ?? "";
  const [viewMode, setViewMode] = useState<ViewMode>("month");
  const [eventType, setEventType] = useState<ScheduleEventType | "">("");
  const [status, setStatus] = useState<ScheduleEventStatus | "">("");
  const range = useMemo(() => buildRange(viewMode), [viewMode]);

  const eventsQuery = useQuery({
    queryKey: ["calendar-events", viewMode, eventType, status, applicationId, jobId],
    queryFn: () =>
      listCalendarEvents({
        page: 1,
        size: 50,
        start_from: range.start,
        start_to: range.end,
        event_type: eventType,
        status,
        application_id: applicationId ? Number(applicationId) : "",
        job_id: jobId ? Number(jobId) : "",
        sort: "start_at",
        order: "asc",
      }),
    retry: false,
  });
  const upcomingQuery = useQuery({
    queryKey: ["calendar-upcoming"],
    queryFn: () => listUpcomingCalendarEvents(168, 8),
    retry: false,
  });

  const events = eventsQuery.data?.data.items ?? [];
  const upcoming = upcomingQuery.data?.data.items ?? [];

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">캘린더</h2>
            <p className="mt-1 text-sm text-slate-600">월간·주간·목록 기준으로 지원 일정을 확인합니다.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {(["month", "week", "list"] as const).map((mode) => (
              <button
                className={viewMode === mode ? "button-primary" : "button-secondary"}
                key={mode}
                type="button"
                onClick={() => setViewMode(mode)}
              >
                {mode === "month" ? "월간" : mode === "week" ? "주간" : "목록"}
              </button>
            ))}
            <Link className="button-primary" href="/calendar/new">
              일정 추가
            </Link>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            일정 유형
            <select className="input" value={eventType} onChange={(event) => setEventType(event.target.value as ScheduleEventType | "")}>
              <option value="">전체</option>
              {scheduleEventTypeOptions.map((value) => (
                <option key={value} value={value}>
                  {scheduleEventTypeLabels[value]}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            상태
            <select className="input" value={status} onChange={(event) => setStatus(event.target.value as ScheduleEventStatus | "")}>
              <option value="">전체</option>
              {scheduleEventStatusOptions.map((value) => (
                <option key={value} value={value}>
                  {scheduleEventStatusLabels[value]}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">임박 일정</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {upcoming.map((event) => (
            <EventCard event={event} key={event.id} compact />
          ))}
          {upcomingQuery.isLoading ? <p className="text-sm text-slate-500">임박 일정을 불러오는 중입니다.</p> : null}
          {!upcomingQuery.isLoading && upcoming.length === 0 ? <p className="text-sm text-slate-500">7일 내 일정이 없습니다.</p> : null}
        </div>
      </section>

      <section className="panel max-w-none">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-950">
            {viewMode === "month" ? "이번 달 일정" : viewMode === "week" ? "이번 주 일정" : "전체 일정"}
          </h2>
          <p className="text-sm text-slate-500">{eventsQuery.data?.data.total ?? 0}개</p>
        </div>
        <div className="mt-4 grid gap-3">
          {events.map((event) => (
            <EventCard event={event} key={event.id} />
          ))}
          {eventsQuery.isLoading ? <p className="text-sm text-slate-500">일정을 불러오는 중입니다.</p> : null}
          {eventsQuery.error ? <p className="text-sm text-rose-700">{eventsQuery.error.message}</p> : null}
          {!eventsQuery.isLoading && events.length === 0 ? <p className="text-sm text-slate-500">표시할 일정이 없습니다.</p> : null}
        </div>
      </section>
    </div>
  );
}

function EventCard({ event, compact = false }: { event: import("@/types/calendar").ScheduleEventPublic; compact?: boolean }) {
  return (
    <Link className="rounded-2xl border border-slate-200 bg-white p-4 transition hover:border-sky-300 hover:shadow-sm" href={`/calendar/events/${event.id}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold text-sky-700">{scheduleEventTypeLabels[event.event_type]}</p>
          <h3 className="mt-1 font-semibold text-slate-950">{event.title}</h3>
          <p className="mt-1 text-sm text-slate-600">{formatScheduleDateTime(event.start_at)}</p>
        </div>
        <div className="text-right text-xs text-slate-500">
          <p>{scheduleEventStatusLabels[event.effective_status]}</p>
          <p>{formatRemaining(event.hours_remaining)}</p>
        </div>
      </div>
      {!compact && event.has_conflict ? <p className="mt-3 text-sm font-medium text-amber-700">겹치는 일정이 있습니다.</p> : null}
      {!compact && event.reminders_count > 0 ? <p className="mt-2 text-xs text-slate-500">알림 {event.reminders_count}개</p> : null}
    </Link>
  );
}

function buildRange(viewMode: ViewMode) {
  const now = new Date();
  if (viewMode === "list") {
    const start = new Date(now);
    start.setDate(start.getDate() - 30);
    const end = new Date(now);
    end.setDate(end.getDate() + 90);
    return { start: start.toISOString(), end: end.toISOString() };
  }
  if (viewMode === "week") {
    const start = new Date(now);
    start.setDate(now.getDate() - now.getDay());
    start.setHours(0, 0, 0, 0);
    const end = new Date(start);
    end.setDate(start.getDate() + 7);
    return { start: start.toISOString(), end: end.toISOString() };
  }
  const start = new Date(now.getFullYear(), now.getMonth(), 1);
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return { start: start.toISOString(), end: end.toISOString() };
}
