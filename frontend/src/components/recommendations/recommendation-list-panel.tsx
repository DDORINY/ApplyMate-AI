"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import {
  createJobRecommendationFeedback,
  generateJobRecommendations,
  getJobRecommendationPolicy,
  listJobRecommendations,
} from "@/lib/api/job-recommendation";
import type { JobRecommendationGrade } from "@/types/job-recommendation";

const gradeLabels: Record<string, string> = {
  EXCELLENT: "매우 적합",
  GOOD: "적합",
  POSSIBLE: "검토 가능",
  LOW: "낮음",
  BLOCKED: "필수 조건 확인",
};

export function RecommendationListPanel() {
  const queryClient = useQueryClient();
  const [grade, setGrade] = useState<JobRecommendationGrade | "">("");
  const [keyword, setKeyword] = useState("");

  const params = { grade, keyword, include_outdated: true };
  const recommendationsQuery = useQuery({
    queryKey: ["job-recommendations", params],
    queryFn: () => listJobRecommendations(params),
    retry: false,
  });
  const policyQuery = useQuery({
    queryKey: ["job-recommendation-policy"],
    queryFn: getJobRecommendationPolicy,
    retry: false,
  });
  const generateMutation = useMutation({
    mutationFn: () =>
      generateJobRecommendations({
        force_refresh: false,
        include_jobs_without_analysis: true,
        exclude_applied_jobs: true,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["job-recommendations"] }),
  });
  const feedbackMutation = useMutation({
    mutationFn: ({ id, feedback_type }: { id: number; feedback_type: "INTERESTED" | "NOT_INTERESTED" | "HIDDEN" }) =>
      createJobRecommendationFeedback(id, { feedback_type }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["job-recommendations"] }),
  });

  const items = recommendationsQuery.data?.data.items ?? [];

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">RULE_BASED</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">채용공고 추천</h1>
            <p className="mt-2 text-sm text-slate-600">
              저장된 공고와 커리어 프로필을 비교해 규칙 기반 점수와 추천 이유를 계산합니다.
            </p>
            {policyQuery.data ? (
              <p className="mt-2 text-xs font-semibold text-violet-500">
                추천 방식: {policyQuery.data.data.recommendation_type} · 정책: {policyQuery.data.data.policy_version}
              </p>
            ) : null}
          </div>
          <button className="button-primary" type="button" onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
            {generateMutation.isPending ? "계산 중..." : "추천 생성"}
          </button>
        </div>
      </section>

      <section className="panel max-w-none">
        <div className="grid gap-3 md:grid-cols-[1fr_180px]">
          <input className="input" placeholder="회사명, 직무명 검색" value={keyword} onChange={(event) => setKeyword(event.target.value)} />
          <select className="input" value={grade} onChange={(event) => setGrade(event.target.value as JobRecommendationGrade | "")}>
            <option value="">전체 등급</option>
            {Object.entries(gradeLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </section>

      {recommendationsQuery.isLoading ? <section className="panel max-w-none">추천 목록을 불러오는 중입니다.</section> : null}
      {recommendationsQuery.error ? <section className="panel max-w-none text-rose-700">{recommendationsQuery.error.message}</section> : null}

      <section className="grid gap-4 xl:grid-cols-2">
        {items.map((item) => {
          const matchedReasons = item.reasons.filter((reason) => reason.match_status === "MATCHED").slice(0, 2);
          const missingReasons = item.reasons.filter((reason) => reason.match_status === "MISSING").slice(0, 2);
          return (
            <article className="panel max-w-none" key={item.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-violet-600">{item.job.company_name}</p>
                  <h2 className="mt-1 text-xl font-bold text-slate-950">{item.job.title}</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    {item.job.location ?? "지역 미상"} · {item.job.employment_type}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-black text-violet-600">{item.score}</p>
                  <p className="text-xs font-bold text-slate-500">{gradeLabels[item.grade]}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold">
                <span className="rounded-full bg-violet-100 px-3 py-1 text-violet-700">추천 방식: {item.recommendation_type}</span>
                {item.has_blocking_mismatch ? <span className="rounded-full bg-rose-100 px-3 py-1 text-rose-700">필수 조건 확인</span> : null}
                {item.outdated ? <span className="rounded-full bg-amber-100 px-3 py-1 text-amber-700">오래된 추천</span> : null}
              </div>
              <div className="mt-4 grid gap-2">
                {matchedReasons.map((reason) => (
                  <p className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800" key={reason.id}>
                    강점 · {reason.label}
                  </p>
                ))}
                {missingReasons.map((reason) => (
                  <p className="rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-800" key={reason.id}>
                    부족 · {reason.label}
                  </p>
                ))}
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <Link className="button-primary" href={`/recommendations/${item.id}`}>
                  상세 보기
                </Link>
                <Link className="button-secondary" href={`/jobs/${item.job_id}`}>
                  공고 보기
                </Link>
                <button className="button-secondary" type="button" onClick={() => feedbackMutation.mutate({ id: item.id, feedback_type: "INTERESTED" })}>
                  관심 있음
                </button>
                <button className="button-secondary" type="button" onClick={() => feedbackMutation.mutate({ id: item.id, feedback_type: "HIDDEN" })}>
                  숨기기
                </button>
              </div>
            </article>
          );
        })}
      </section>

      {!recommendationsQuery.isLoading && items.length === 0 ? (
        <section className="panel max-w-none text-center">
          <p className="text-lg font-bold text-slate-950">아직 추천 결과가 없습니다.</p>
          <p className="mt-2 text-sm text-slate-600">저장된 채용공고와 프로필을 기준으로 추천을 생성해 보세요.</p>
        </section>
      ) : null}
    </div>
  );
}
