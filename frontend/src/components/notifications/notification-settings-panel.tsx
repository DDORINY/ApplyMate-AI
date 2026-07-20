"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { getNotificationSettings, updateNotificationSettings } from "@/lib/api/notification";
import type { NotificationSettingPublic } from "@/types/notification";

const toggles: Array<[keyof NotificationSettingPublic, string]> = [
  ["in_app_enabled", "In-app 알림"],
  ["email_enabled", "Email 알림"],
  ["push_enabled", "Push 알림"],
  ["quiet_hours_enabled", "조용한 시간"],
  ["schedule_reminder_enabled", "일정 리마인더"],
  ["application_deadline_enabled", "지원 마감"],
  ["recommendation_enabled", "추천 알림"],
  ["gmail_candidate_enabled", "Gmail 후보"],
  ["document_improvement_enabled", "문서 개선"],
  ["sync_error_enabled", "동기화 오류"],
  ["daily_digest_enabled", "일일 요약"],
];

export function NotificationSettingsPanel() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const settingsQuery = useQuery({
    queryKey: ["notification-settings"],
    queryFn: getNotificationSettings,
    retry: false,
  });
  const mutation = useMutation({
    mutationFn: updateNotificationSettings,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notification-settings"] }),
  });

  useEffect(() => {
    if (settingsQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [settingsQuery.error, router]);

  const settings = settingsQuery.data?.data;

  if (settingsQuery.isLoading) {
    return <div className="panel max-w-none">알림 설정을 불러오는 중입니다.</div>;
  }
  if (settingsQuery.error) {
    return <div className="panel max-w-none text-rose-700">{settingsQuery.error.message}</div>;
  }
  if (!settings) {
    return <div className="panel max-w-none">알림 설정을 찾을 수 없습니다.</div>;
  }

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <p className="text-sm font-semibold text-violet-600">Notification Settings</p>
        <h1 className="mt-1 text-2xl font-bold text-slate-950">알림 설정</h1>
        <p className="mt-2 text-sm text-slate-600">외부 채널은 사용자 동의가 있어야 활성화됩니다. Push는 v0.8.0에서 설정 구조만 제공합니다.</p>
      </section>

      <section className="panel max-w-none">
        <div className="grid gap-3 sm:grid-cols-2">
          {toggles.map(([key, label]) => (
            <label className="flex items-center justify-between rounded-2xl border border-violet-100 bg-white/70 px-4 py-3 text-sm font-semibold text-slate-700" key={key}>
              {label}
              <input
                type="checkbox"
                checked={Boolean(settings[key])}
                onChange={(event) => mutation.mutate({ [key]: event.target.checked })}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            Timezone
            <input className="input" defaultValue={settings.timezone} onBlur={(event) => mutation.mutate({ timezone: event.target.value })} />
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            기본 리마인더 분
            <input
              className="input"
              defaultValue={settings.default_reminder_minutes}
              inputMode="numeric"
              onBlur={(event) => mutation.mutate({ default_reminder_minutes: Number(event.target.value) })}
            />
          </label>
          <label className="grid gap-2 text-sm font-medium text-slate-700">
            일일 요약 시간
            <input className="input" defaultValue={settings.daily_digest_hour} inputMode="numeric" onBlur={(event) => mutation.mutate({ daily_digest_hour: Number(event.target.value) })} />
          </label>
        </div>
        {mutation.error ? <p className="mt-4 text-sm text-rose-700">{mutation.error.message}</p> : null}
      </section>
    </div>
  );
}
