"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { getJobRecommendationSettings, updateJobRecommendationSettings } from "@/lib/api/job-recommendation";
import type { RecommendationRunFrequency } from "@/types/job-recommendation";

export function RecommendationSettingsPanel() {
  const queryClient = useQueryClient();
  const settingsQuery = useQuery({
    queryKey: ["job-recommendation-settings"],
    queryFn: getJobRecommendationSettings,
    retry: false,
  });
  const [form, setForm] = useState({
    enabled: false,
    frequency: "MANUAL" as RecommendationRunFrequency,
    preferred_run_hour: 9,
    timezone: "Asia/Seoul",
    minimum_score: 50,
    include_jobs_without_analysis: true,
    exclude_applied_jobs: true,
    exclude_hidden_jobs: true,
    notify_new_recommendations: true,
    notify_score_changes: true,
  });
  useEffect(() => {
    const settings = settingsQuery.data?.data;
    if (settings) {
      setForm({
        enabled: settings.enabled,
        frequency: settings.frequency,
        preferred_run_hour: settings.preferred_run_hour,
        timezone: settings.timezone,
        minimum_score: settings.minimum_score,
        include_jobs_without_analysis: settings.include_jobs_without_analysis,
        exclude_applied_jobs: settings.exclude_applied_jobs,
        exclude_hidden_jobs: settings.exclude_hidden_jobs,
        notify_new_recommendations: settings.notify_new_recommendations,
        notify_score_changes: settings.notify_score_changes,
      });
    }
  }, [settingsQuery.data]);

  const saveMutation = useMutation({
    mutationFn: () => updateJobRecommendationSettings(form),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["job-recommendation-settings"] }),
  });

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <p className="text-sm font-semibold text-violet-600">Recommendation Settings</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">추천 실행 설정</h1>
        <p className="mt-2 text-sm text-slate-600">
          v0.6.1은 실제 백그라운드 워커가 아니라 스케줄러가 호출 가능한 설정과 실행 조건 기반을 제공합니다.
        </p>
      </section>

      <section className="panel max-w-none">
        {settingsQuery.isLoading ? <p className="text-sm text-slate-500">설정을 불러오는 중입니다.</p> : null}
        {settingsQuery.error ? <p className="text-sm text-rose-700">{settingsQuery.error.message}</p> : null}
        <div className="grid gap-4 md:grid-cols-2">
          <label className="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700">
            <input
              checked={form.enabled}
              type="checkbox"
              onChange={(event) => setForm((prev) => ({ ...prev, enabled: event.target.checked }))}
            />
            추천 자동 실행 후보 활성화
          </label>
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            실행 빈도
            <select className="input" value={form.frequency} onChange={(event) => setForm((prev) => ({ ...prev, frequency: event.target.value as RecommendationRunFrequency }))}>
              <option value="MANUAL">수동</option>
              <option value="DAILY">매일</option>
              <option value="WEEKLY">매주</option>
            </select>
          </label>
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            실행 시간
            <input className="input" max={23} min={0} type="number" value={form.preferred_run_hour} onChange={(event) => setForm((prev) => ({ ...prev, preferred_run_hour: Number(event.target.value) }))} />
          </label>
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            시간대
            <input className="input" value={form.timezone} onChange={(event) => setForm((prev) => ({ ...prev, timezone: event.target.value }))} />
          </label>
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            최소 추천 점수
            <input className="input" max={100} min={0} type="number" value={form.minimum_score} onChange={(event) => setForm((prev) => ({ ...prev, minimum_score: Number(event.target.value) }))} />
          </label>
          <Toggle label="분석 없는 공고 포함" value={form.include_jobs_without_analysis} onChange={(value) => setForm((prev) => ({ ...prev, include_jobs_without_analysis: value }))} />
          <Toggle label="지원 완료 공고 제외" value={form.exclude_applied_jobs} onChange={(value) => setForm((prev) => ({ ...prev, exclude_applied_jobs: value }))} />
          <Toggle label="숨김 공고 제외" value={form.exclude_hidden_jobs} onChange={(value) => setForm((prev) => ({ ...prev, exclude_hidden_jobs: value }))} />
          <Toggle label="새 추천 알림 후보 생성" value={form.notify_new_recommendations} onChange={(value) => setForm((prev) => ({ ...prev, notify_new_recommendations: value }))} />
          <Toggle label="점수 변화 알림 후보 생성" value={form.notify_score_changes} onChange={(value) => setForm((prev) => ({ ...prev, notify_score_changes: value }))} />
        </div>
        <div className="mt-5 flex items-center gap-3">
          <button className="button-primary" disabled={saveMutation.isPending} type="button" onClick={() => saveMutation.mutate()}>
            {saveMutation.isPending ? "저장 중..." : "설정 저장"}
          </button>
          {saveMutation.isSuccess ? <p className="text-sm font-semibold text-emerald-600">저장되었습니다.</p> : null}
        </div>
      </section>
    </div>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700">
      <input checked={value} type="checkbox" onChange={(event) => onChange(event.target.checked)} />
      {label}
    </label>
  );
}
