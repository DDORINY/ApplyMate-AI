"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  disconnectCalendarIntegration,
  getCalendarIntegrationStatus,
  listCalendarSyncErrors,
  listCalendarSyncRuns,
  listExternalCalendars,
  startCalendarConnection,
  syncCalendar,
  updateCalendarIntegrationSettings,
} from "@/lib/api/calendar-integration";
import type { CalendarSyncDirection } from "@/types/calendar-integration";

const directionLabels: Record<CalendarSyncDirection, string> = {
  INTERNAL_TO_GOOGLE: "ApplyMate → Google",
  GOOGLE_TO_INTERNAL: "Google → ApplyMate",
  BIDIRECTIONAL: "양방향",
};

export function CalendarIntegrationPanel() {
  const queryClient = useQueryClient();
  const [selectedCalendarId, setSelectedCalendarId] = useState("");
  const [syncDirection, setSyncDirection] = useState<CalendarSyncDirection>("INTERNAL_TO_GOOGLE");

  const statusQuery = useQuery({
    queryKey: ["calendar-integration-status"],
    queryFn: getCalendarIntegrationStatus,
    retry: false,
  });
  const calendarsQuery = useQuery({
    queryKey: ["external-calendars"],
    queryFn: listExternalCalendars,
    enabled: Boolean(statusQuery.data?.data.connected),
    retry: false,
  });
  const runsQuery = useQuery({
    queryKey: ["calendar-sync-runs"],
    queryFn: listCalendarSyncRuns,
    enabled: Boolean(statusQuery.data?.data.connected),
    retry: false,
  });
  const errorsQuery = useQuery({
    queryKey: ["calendar-sync-errors"],
    queryFn: listCalendarSyncErrors,
    enabled: Boolean(statusQuery.data?.data.connected),
    retry: false,
  });

  const connectMutation = useMutation({
    mutationFn: startCalendarConnection,
    onSuccess: (response) => {
      window.location.href = response.data.authorization_url;
    },
  });
  const settingsMutation = useMutation({
    mutationFn: () =>
      updateCalendarIntegrationSettings({
        selected_calendar_id: selectedCalendarId || undefined,
        sync_direction: syncDirection,
        sync_enabled: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar-integration-status"] });
      queryClient.invalidateQueries({ queryKey: ["external-calendars"] });
    },
  });
  const syncMutation = useMutation({
    mutationFn: syncCalendar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar-integration-status"] });
      queryClient.invalidateQueries({ queryKey: ["calendar-sync-runs"] });
      queryClient.invalidateQueries({ queryKey: ["calendar-sync-errors"] });
    },
  });
  const disconnectMutation = useMutation({
    mutationFn: disconnectCalendarIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["calendar-integration-status"] });
      queryClient.invalidateQueries({ queryKey: ["external-calendars"] });
    },
  });

  const status = statusQuery.data?.data;
  const calendars = calendarsQuery.data?.data ?? [];
  const runs = runsQuery.data?.data ?? [];
  const errors = errorsQuery.data?.data ?? [];

  return (
    <section className="mx-auto grid w-full max-w-4xl gap-6">
      <div>
        <p className="text-sm font-medium text-sky-700">Integrations</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">Google Calendar 연동</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          로그인용 Google OAuth와 별도로, 사용자가 명시적으로 승인한 Calendar 권한만 일정 동기화에 사용합니다.
        </p>
      </div>

      <section className="panel max-w-none">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-950">연결 상태</h2>
            {statusQuery.isLoading ? <p className="mt-2 text-sm text-slate-500">상태를 확인하는 중입니다.</p> : null}
            {status ? (
              <div className="mt-3 grid gap-1 text-sm text-slate-600">
                <p>Provider: {status.provider}</p>
                <p>상태: {status.connected ? status.status : "DISCONNECTED"}</p>
                <p>계정: {status.email ?? "연결된 계정 없음"}</p>
                <p>선택 Calendar: {status.selected_calendar_name ?? "미선택"}</p>
                <p>동기화 방향: {status.sync_direction ? directionLabels[status.sync_direction] : "미설정"}</p>
                {status.needs_verification ? (
                  <p className="font-medium text-amber-700">실제 Google API 호출은 운영 credentials로 별도 검증이 필요합니다.</p>
                ) : null}
              </div>
            ) : null}
          </div>
          <div className="flex flex-wrap gap-2">
            {!status?.connected ? (
              <button className="button-primary" type="button" onClick={() => connectMutation.mutate()}>
                Google Calendar 연결
              </button>
            ) : (
              <>
                <button className="button-primary" type="button" onClick={() => syncMutation.mutate()}>
                  전체 동기화
                </button>
                <button className="button-secondary" type="button" onClick={() => disconnectMutation.mutate()}>
                  연결 해제
                </button>
              </>
            )}
          </div>
        </div>
        {connectMutation.error ? <p className="mt-3 text-sm text-rose-700">{connectMutation.error.message}</p> : null}
        {syncMutation.error ? <p className="mt-3 text-sm text-rose-700">{syncMutation.error.message}</p> : null}
        {disconnectMutation.error ? <p className="mt-3 text-sm text-rose-700">{disconnectMutation.error.message}</p> : null}
      </section>

      {status?.connected ? (
        <section className="panel max-w-none">
          <h2 className="text-lg font-semibold text-slate-950">Calendar 선택과 동기화 방향</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <label className="grid gap-2 text-sm font-medium text-slate-700 md:col-span-2">
              동기화 대상 Calendar
              <select className="input" value={selectedCalendarId} onChange={(event) => setSelectedCalendarId(event.target.value)}>
                <option value="">선택 안 함</option>
                {calendars.map((calendar) => (
                  <option disabled={!calendar.writable} key={calendar.id} value={calendar.id}>
                    {calendar.name} {calendar.primary ? "(primary)" : ""} {!calendar.writable ? "(읽기 전용)" : ""}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-medium text-slate-700">
              동기화 방향
              <select className="input" value={syncDirection} onChange={(event) => setSyncDirection(event.target.value as CalendarSyncDirection)}>
                {Object.entries(directionLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <button className="button-primary mt-4" type="button" onClick={() => settingsMutation.mutate()}>
            설정 저장
          </button>
          {settingsMutation.error ? <p className="mt-3 text-sm text-rose-700">{settingsMutation.error.message}</p> : null}
        </section>
      ) : null}

      {status?.connected ? (
        <div className="grid gap-5 lg:grid-cols-2">
          <section className="panel max-w-none">
            <h2 className="text-lg font-semibold text-slate-950">최근 동기화</h2>
            <div className="mt-4 grid gap-3">
              {runs.map((run) => (
                <div className="rounded-2xl border border-slate-200 p-4" key={run.id}>
                  <p className="font-semibold text-slate-950">#{run.id} · {run.status}</p>
                  <p className="mt-1 text-sm text-slate-600">
                    생성 {run.created_count} · 수정 {run.updated_count} · 오류 {run.error_count}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">{formatDateTime(run.started_at)}</p>
                </div>
              ))}
              {runs.length === 0 ? <p className="text-sm text-slate-500">아직 동기화 이력이 없습니다.</p> : null}
            </div>
          </section>

          <section className="panel max-w-none">
            <h2 className="text-lg font-semibold text-slate-950">최근 오류</h2>
            <div className="mt-4 grid gap-3">
              {errors.map((error) => (
                <div className="rounded-2xl border border-rose-100 bg-rose-50 p-4" key={error.id}>
                  <p className="font-semibold text-rose-800">{error.error_code}</p>
                  <p className="mt-1 text-sm text-rose-700">{error.safe_message}</p>
                  <p className="mt-1 text-xs text-rose-600">{formatDateTime(error.created_at)}</p>
                </div>
              ))}
              {errors.length === 0 ? <p className="text-sm text-slate-500">최근 동기화 오류가 없습니다.</p> : null}
            </div>
          </section>
        </div>
      ) : null}
    </section>
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
