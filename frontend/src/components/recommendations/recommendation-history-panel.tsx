"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { listJobRecommendationSnapshots } from "@/lib/api/job-recommendation";

const changeLabels: Record<string, string> = {
  NEW: "새 추천",
  UNCHANGED: "변화 없음",
  SCORE_UP: "점수 상승",
  SCORE_DOWN: "점수 하락",
  GRADE_UP: "등급 상승",
  GRADE_DOWN: "등급 하락",
  REMOVED: "제외됨",
  OUTDATED: "오래됨",
};

export function RecommendationHistoryPanel() {
  const snapshotsQuery = useQuery({
    queryKey: ["job-recommendation-snapshots"],
    queryFn: () => listJobRecommendationSnapshots({ size: 20 }),
    retry: false,
  });
  const snapshots = snapshotsQuery.data?.data.items ?? [];

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">Recommendation History</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">추천 실행 이력</h1>
            <p className="mt-2 text-sm text-slate-600">추천 실행마다 저장된 Snapshot과 신규·변경 추천을 확인합니다.</p>
          </div>
          <Link className="button-secondary" href="/recommendations">
            추천 목록
          </Link>
        </div>
      </section>

      {snapshotsQuery.isLoading ? <section className="panel max-w-none">추천 이력을 불러오는 중입니다.</section> : null}
      {snapshotsQuery.error ? <section className="panel max-w-none text-rose-700">{snapshotsQuery.error.message}</section> : null}

      {snapshots.map((snapshot) => (
        <section className="panel max-w-none" key={snapshot.id}>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-sm font-semibold text-violet-600">Snapshot #{snapshot.id}</p>
              <h2 className="mt-1 text-xl font-bold text-slate-950">{formatDateTime(snapshot.generated_at)}</h2>
              <p className="mt-1 text-xs text-slate-500">
                run #{snapshot.run_id} · 정책 {snapshot.policy_version}
              </p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-sm">
              <Metric label="추천" value={snapshot.recommended_count} />
              <Metric label="신규" value={snapshot.new_count} />
              <Metric label="변경" value={snapshot.changed_count} />
            </div>
          </div>
          <div className="mt-4 grid gap-2">
            {snapshot.items.slice(0, 5).map((item) => (
              <Link
                className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700 transition hover:bg-violet-50"
                href={item.recommendation_id ? `/recommendations/${item.recommendation_id}` : "/recommendations"}
                key={item.id}
              >
                #{item.rank} · {changeLabels[item.change_type]} · {item.score}점
                {item.score_delta ? ` (${item.score_delta > 0 ? "+" : ""}${item.score_delta})` : ""}
              </Link>
            ))}
          </div>
        </section>
      ))}

      {!snapshotsQuery.isLoading && snapshots.length === 0 ? (
        <section className="panel max-w-none text-center">
          <p className="text-lg font-bold text-slate-950">아직 추천 실행 이력이 없습니다.</p>
          <p className="mt-2 text-sm text-slate-600">추천 생성 또는 자동 실행 조건으로 실행하면 Snapshot이 저장됩니다.</p>
        </section>
      ) : null}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl bg-violet-50 px-4 py-3">
      <p className="text-xs font-semibold text-violet-500">{label}</p>
      <p className="mt-1 text-xl font-black text-violet-700">{value}</p>
    </div>
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Seoul",
  }).format(new Date(value));
}
