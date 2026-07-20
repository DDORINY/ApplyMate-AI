"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import {
  createJobRecommendationFeedback,
  getJobRecommendation,
  refreshJobRecommendation,
} from "@/lib/api/job-recommendation";

export function RecommendationDetailPanel({ recommendationId }: { recommendationId: number }) {
  const queryClient = useQueryClient();
  const recommendationQuery = useQuery({
    queryKey: ["job-recommendation", recommendationId],
    queryFn: () => getJobRecommendation(recommendationId),
    retry: false,
  });
  const refreshMutation = useMutation({
    mutationFn: () => refreshJobRecommendation(recommendationId),
    onSuccess: (response) => {
      queryClient.setQueryData(["job-recommendation", recommendationId], response);
      queryClient.invalidateQueries({ queryKey: ["job-recommendations"] });
    },
  });
  const feedbackMutation = useMutation({
    mutationFn: (feedback_type: "INTERESTED" | "NOT_INTERESTED" | "HIDDEN" | "SAVED_FOR_LATER") =>
      createJobRecommendationFeedback(recommendationId, { feedback_type }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["job-recommendation", recommendationId] }),
  });

  if (recommendationQuery.isLoading) {
    return <section className="panel max-w-none">추천 상세를 불러오는 중입니다.</section>;
  }
  if (recommendationQuery.error) {
    return <section className="panel max-w-none text-rose-700">{recommendationQuery.error.message}</section>;
  }
  const item = recommendationQuery.data?.data;
  if (!item) {
    return <section className="panel max-w-none">추천 결과를 찾을 수 없습니다.</section>;
  }
  const matched = item.reasons.filter((reason) => reason.match_status === "MATCHED");
  const missing = item.reasons.filter((reason) => reason.match_status === "MISSING");
  const unknown = item.reasons.filter((reason) => reason.match_status === "UNKNOWN");

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">추천 방식: {item.recommendation_type}</p>
            <h1 className="mt-2 text-3xl font-black text-slate-950">{item.job.title}</h1>
            <p className="mt-2 text-slate-600">
              {item.job.company_name} · {item.job.location ?? "지역 미상"} · 정책 {item.policy_version}
            </p>
          </div>
          <div className="rounded-[2rem] bg-violet-600 px-8 py-6 text-center text-white shadow-xl shadow-violet-200">
            <p className="text-sm font-semibold opacity-80">추천 점수</p>
            <p className="text-5xl font-black">{item.score}</p>
            <p className="text-sm font-bold">{item.grade}</p>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          <Link className="button-secondary" href="/recommendations">
            목록으로
          </Link>
          <Link className="button-primary" href={`/jobs/${item.job_id}`}>
            공고 상세 보기
          </Link>
          <button className="button-secondary" type="button" onClick={() => refreshMutation.mutate()} disabled={refreshMutation.isPending}>
            {refreshMutation.isPending ? "재계산 중..." : "추천 새로 계산"}
          </button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        {Object.entries(item.score_breakdown).map(([key, value]) => (
          <div className="panel max-w-none" key={key}>
            <p className="text-xs font-semibold uppercase text-violet-500">{key}</p>
            <p className="mt-2 text-2xl font-black text-slate-950">{value}점</p>
          </div>
        ))}
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        <ReasonColumn title="추천 이유" items={matched} tone="emerald" />
        <ReasonColumn title="부족 조건" items={missing} tone="amber" />
        <ReasonColumn title="확인 필요" items={unknown} tone="slate" />
      </section>

      {item.missing_profile_fields.length > 0 ? (
        <section className="panel max-w-none">
          <h2 className="text-lg font-bold text-slate-950">프로필 보완 안내</h2>
          <p className="mt-2 text-sm text-slate-600">아래 정보가 부족해 추천 신뢰도가 낮아질 수 있습니다.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {item.missing_profile_fields.map((field) => (
              <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-800" key={field}>
                {field}
              </span>
            ))}
          </div>
        </section>
      ) : null}

      <section className="panel max-w-none">
        <h2 className="text-lg font-bold text-slate-950">피드백</h2>
        <p className="mt-2 text-sm text-slate-600">피드백은 저장되지만 v0.6.0에서는 자동 가중치 학습에 사용하지 않습니다.</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {(["INTERESTED", "SAVED_FOR_LATER", "NOT_INTERESTED", "HIDDEN"] as const).map((type) => (
            <button className="button-secondary" type="button" key={type} onClick={() => feedbackMutation.mutate(type)}>
              {type}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

function ReasonColumn({
  title,
  items,
  tone,
}: {
  title: string;
  items: { id: number; label: string; evidence: string | null; severity: string }[];
  tone: "emerald" | "amber" | "slate";
}) {
  const toneClass = {
    emerald: "bg-emerald-50 text-emerald-800",
    amber: "bg-amber-50 text-amber-800",
    slate: "bg-slate-50 text-slate-700",
  }[tone];
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-bold text-slate-950">{title}</h2>
      <div className="mt-4 grid gap-3">
        {items.map((item) => (
          <div className={`rounded-2xl p-4 ${toneClass}`} key={item.id}>
            <p className="font-bold">{item.label}</p>
            <p className="mt-1 text-sm opacity-80">{item.evidence}</p>
          </div>
        ))}
        {items.length === 0 ? <p className="text-sm text-slate-500">표시할 항목이 없습니다.</p> : null}
      </div>
    </section>
  );
}
