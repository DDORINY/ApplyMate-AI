"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import {
  createJobRecommendationFeedback,
  generateJobRecommendations,
  getJobRecommendationPolicy,
  listRecommendationNotifications,
  listJobRecommendations,
  runJobRecommendationsIfDue,
} from "@/lib/api/job-recommendation";
import type { JobRecommendationFeedbackType, JobRecommendationGrade, RecommendationChangeType } from "@/types/job-recommendation";

const gradeLabels: Record<string, string> = {
  EXCELLENT: "매우 적합",
  GOOD: "적합",
  POSSIBLE: "검토 가능",
  LOW: "낮음",
  BLOCKED: "필수 조건 확인",
};

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

const feedbackLabels: Record<string, string> = {
  INTERESTED: "관심 있음",
  NOT_INTERESTED: "관심 없음",
  HIDDEN: "숨김",
  APPLIED: "지원 완료",
  SAVED_FOR_LATER: "나중에 보기",
};

export function RecommendationListPanel() {
  const queryClient = useQueryClient();
  const [grade, setGrade] = useState<JobRecommendationGrade | "">("");
  const [changeType, setChangeType] = useState<RecommendationChangeType | "">("");
  const [feedbackType, setFeedbackType] = useState<JobRecommendationFeedbackType | "">("");
  const [minimumScore, setMinimumScore] = useState("");
  const [keyword, setKeyword] = useState("");

  const params = {
    grade,
    change_type: changeType,
    feedback: feedbackType,
    min_score: minimumScore ? Number(minimumScore) : undefined,
    keyword,
    include_outdated: true,
  };
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
  const notificationsQuery = useQuery({
    queryKey: ["recommendation-notifications", "pending"],
    queryFn: () => listRecommendationNotifications({ status: "PENDING", size: 5 }),
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
  const runIfDueMutation = useMutation({
    mutationFn: () => runJobRecommendationsIfDue({ force: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["recommendation-notifications"] });
    },
  });
  const feedbackMutation = useMutation({
    mutationFn: ({ id, feedback_type }: { id: number; feedback_type: JobRecommendationFeedbackType }) =>
      createJobRecommendationFeedback(id, { feedback_type }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["job-recommendations"] }),
  });

  const items = recommendationsQuery.data?.data.items ?? [];

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none overflow-hidden">
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
          <div className="flex flex-wrap gap-2">
            <button className="button-secondary" type="button" onClick={() => runIfDueMutation.mutate()} disabled={runIfDueMutation.isPending}>
              {runIfDueMutation.isPending ? "실행 중..." : "자동 실행 조건으로 실행"}
            </button>
            <button className="button-primary" type="button" onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
              {generateMutation.isPending ? "계산 중..." : "추천 생성"}
            </button>
            <Link className="button-secondary" href="/recommendations/history">
              이력 보기
            </Link>
            <Link className="button-secondary" href="/settings/recommendations">
              추천 설정
            </Link>
          </div>
        </div>
        {runIfDueMutation.data ? (
          <p className="mt-3 rounded-2xl bg-violet-50 px-4 py-3 text-sm text-violet-700">{runIfDueMutation.data.data.message}</p>
        ) : null}
      </section>

      <section className="panel max-w-none">
        <div className="grid gap-3 lg:grid-cols-[1fr_150px_150px_150px]">
          <input className="input" placeholder="회사명, 직무명 검색" value={keyword} onChange={(event) => setKeyword(event.target.value)} />
          <select className="input" value={grade} onChange={(event) => setGrade(event.target.value as JobRecommendationGrade | "")}>
            <option value="">전체 등급</option>
            {Object.entries(gradeLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select className="input" value={changeType} onChange={(event) => setChangeType(event.target.value as RecommendationChangeType | "")}>
            <option value="">전체 변화</option>
            {Object.entries(changeLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select className="input" value={feedbackType} onChange={(event) => setFeedbackType(event.target.value as JobRecommendationFeedbackType | "")}>
            <option value="">전체 피드백</option>
            {Object.entries(feedbackLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <input className="input" min={0} max={100} placeholder="최소 점수" type="number" value={minimumScore} onChange={(event) => setMinimumScore(event.target.value)} />
        </div>
      </section>

      {(notificationsQuery.data?.data.items.length ?? 0) > 0 ? (
        <section className="panel max-w-none">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-violet-600">알림 후보</p>
              <h2 className="mt-1 text-lg font-bold text-slate-950">실제 발송 전 검토할 추천 변화</h2>
            </div>
            <span className="rounded-full bg-violet-100 px-3 py-1 text-xs font-bold text-violet-700">
              {notificationsQuery.data?.data.total ?? 0}건
            </span>
          </div>
          <div className="mt-4 grid gap-2">
            {notificationsQuery.data?.data.items.map((item) => (
              <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700" key={item.id}>
                <span className="font-semibold text-slate-950">{item.title}</span> · {item.message}
              </p>
            ))}
          </div>
        </section>
      ) : null}

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
                {item.latest_change_type ? (
                  <span className="rounded-full bg-sky-100 px-3 py-1 text-sky-700">{changeLabels[item.latest_change_type]}</span>
                ) : null}
                {item.feedback ? (
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-700">{feedbackLabels[item.feedback.feedback_type]}</span>
                ) : null}
              </div>
              <div className="mt-4 grid gap-2 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600 sm:grid-cols-3">
                <p>순위: {item.rank ? `${item.rank}위` : "미집계"}</p>
                <p>점수 변화: {item.score_delta ? `${item.score_delta > 0 ? "+" : ""}${item.score_delta}` : "0"}</p>
                <p>데이터 완성도: {item.data_completeness_score ?? "-"}%</p>
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
                <button className="button-secondary" type="button" onClick={() => feedbackMutation.mutate({ id: item.id, feedback_type: "SAVED_FOR_LATER" })}>
                  나중에 보기
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
