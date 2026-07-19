"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  analyzeJobMatch,
  createJobMatchFeedback,
  deleteJobMatch,
  getJobMatch,
  listJobMatchFeedback,
  listJobMatchRuns,
} from "@/lib/api/job-match";
import type { JobMatchFeedbackType, JobMatchPublic } from "@/types/job-match";

type JobMatchPanelProps = {
  jobId: number;
};

const gradeLabels: Record<string, string> = {
  EXCELLENT: "매우 높음",
  GOOD: "높음",
  MODERATE: "보통",
  LOW: "낮음",
  VERY_LOW: "매우 낮음",
};

const recommendationLabels: Record<string, string> = {
  STRONGLY_RECOMMENDED: "강력 추천",
  RECOMMENDED: "추천",
  CONSIDER: "검토",
  NOT_RECOMMENDED: "비추천",
  INSUFFICIENT_DATA: "정보 부족",
};

const feedbackLabels: Record<JobMatchFeedbackType, string> = {
  ACCURATE: "정확해요",
  TOO_HIGH: "점수가 높아요",
  TOO_LOW: "점수가 낮아요",
  MISSING_STRENGTH: "강점이 빠졌어요",
  MISSING_RISK: "위험요소가 빠졌어요",
  OTHER: "기타",
};

export function JobMatchPanel({ jobId }: JobMatchPanelProps) {
  const queryClient = useQueryClient();
  const [feedbackType, setFeedbackType] = useState<JobMatchFeedbackType>("ACCURATE");
  const [rating, setRating] = useState("5");
  const [comment, setComment] = useState("");

  const matchQuery = useQuery({
    queryKey: ["job-match", jobId],
    queryFn: () => getJobMatch(jobId),
    retry: false,
  });
  const runsQuery = useQuery({
    queryKey: ["job-match-runs", jobId],
    queryFn: () => listJobMatchRuns(jobId),
    retry: false,
  });
  const feedbackQuery = useQuery({
    queryKey: ["job-match-feedback", jobId],
    queryFn: () => listJobMatchFeedback(jobId),
    retry: false,
  });

  const match = matchQuery.data?.data;

  const runMutation = useMutation({
    mutationFn: (force: boolean) => analyzeJobMatch(jobId, { force }),
    onSuccess: (response) => {
      queryClient.setQueryData(["job-match", jobId], response);
      queryClient.invalidateQueries({ queryKey: ["job-match-runs", jobId] });
      queryClient.invalidateQueries({ queryKey: ["job-match-feedback", jobId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteJobMatch(jobId),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ["job-match", jobId] });
      queryClient.invalidateQueries({ queryKey: ["job-match-runs", jobId] });
      queryClient.invalidateQueries({ queryKey: ["job-match-feedback", jobId] });
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: () =>
      createJobMatchFeedback(jobId, {
        feedback_type: feedbackType,
        rating: rating ? Number(rating) : null,
        comment: comment.trim() || null,
      }),
    onSuccess: () => {
      setComment("");
      queryClient.invalidateQueries({ queryKey: ["job-match-feedback", jobId] });
    },
  });

  return (
    <section className="panel max-w-none">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-sky-700">AI 공고 적합도 분석</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            내 커리어 프로필과 이 공고의 맞춤도를 계산합니다
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            점수는 규칙 기반으로 산정되며, AI는 설명 보조 용도로만 사용합니다.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="button-primary"
            type="button"
            disabled={runMutation.isPending}
            onClick={() => runMutation.mutate(false)}
          >
            {runMutation.isPending ? "분석 중..." : match ? "최신 결과 확인" : "적합도 분석"}
          </button>
          <button
            className="button-secondary"
            type="button"
            disabled={runMutation.isPending}
            onClick={() => runMutation.mutate(true)}
          >
            재계산
          </button>
        </div>
      </div>

      {match?.is_outdated ? (
        <p className="mt-4 rounded-2xl bg-orange-50 px-4 py-3 text-sm text-orange-800">
          프로필 또는 공고 분석이 변경되어 기존 적합도 결과가 오래되었습니다. 재계산을 권장합니다.
        </p>
      ) : null}
      {runMutation.error ? <ErrorMessage message={runMutation.error.message} /> : null}
      {matchQuery.error && !match ? (
        <p className="mt-4 text-sm text-slate-500">
          아직 저장된 적합도 분석 결과가 없습니다. 완료된 공고 분석과 커리어 프로필이 필요합니다.
        </p>
      ) : null}

      {match ? (
        <div className="mt-5 grid gap-5">
          <ScoreCard match={match} />
          <div className="grid gap-4 md:grid-cols-3">
            <EvidenceList title="일치 기술" items={match.matched_skills} emptyText="일치 기술이 없습니다." />
            <EvidenceList title="보완 기술" items={match.missing_skills} emptyText="보완 기술이 없습니다." />
            <EvidenceList title="연결 프로젝트" items={match.matched_projects} emptyText="연결 프로젝트가 없습니다." />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <EvidenceList title="강점" items={match.strengths} emptyText="강점 근거가 없습니다." />
            <EvidenceList title="보완점" items={match.gaps} emptyText="보완점이 없습니다." />
            <EvidenceList title="위험요소" items={match.risks} emptyText="위험요소가 없습니다." />
          </div>
          <FeedbackForm
            feedbackType={feedbackType}
            rating={rating}
            comment={comment}
            isPending={feedbackMutation.isPending}
            onFeedbackTypeChange={setFeedbackType}
            onRatingChange={setRating}
            onCommentChange={setComment}
            onSubmit={() => feedbackMutation.mutate()}
          />
          {feedbackMutation.error ? <ErrorMessage message={feedbackMutation.error.message} /> : null}
          <RunAndFeedbackList
            runs={runsQuery.data?.data.items ?? []}
            feedback={feedbackQuery.data?.data.items ?? []}
          />
          <button
            className="button-secondary border-rose-200 text-rose-700"
            type="button"
            disabled={deleteMutation.isPending}
            onClick={() => {
              if (window.confirm("적합도 분석 결과를 삭제할까요? 실행 이력은 보존됩니다.")) {
                deleteMutation.mutate();
              }
            }}
          >
            {deleteMutation.isPending ? "삭제 중..." : "적합도 결과 삭제"}
          </button>
          {deleteMutation.error ? <ErrorMessage message={deleteMutation.error.message} /> : null}
        </div>
      ) : null}
    </section>
  );
}

function ScoreCard({ match }: { match: JobMatchPublic }) {
  return (
    <div className="rounded-2xl border border-slate-200 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-500">종합 점수</p>
          <p className="mt-1 text-4xl font-bold text-slate-950">{match.total_score}</p>
        </div>
        <div className="text-right">
          <Badge>{gradeLabels[match.grade] ?? match.grade}</Badge>
          <p className="mt-2 text-sm font-semibold text-sky-700">
            {recommendationLabels[match.recommendation_status] ?? match.recommendation_status}
          </p>
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-700">{match.recommendation_summary}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {Object.entries(match.scores).map(([key, value]) => (
          <div className="rounded-xl bg-slate-50 px-3 py-2" key={key}>
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium capitalize text-slate-700">{key}</span>
              <span className="font-semibold text-slate-950">{value}</span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
              <div className="h-full rounded-full bg-sky-500" style={{ width: `${value}%` }} />
            </div>
          </div>
        ))}
      </div>
      <p className="mt-3 text-xs text-slate-500">
        Profile completeness {match.profile_completeness}% · {match.explanation_provider} ·{" "}
        {match.calculated_at ? new Date(match.calculated_at).toLocaleString() : ""}
      </p>
    </div>
  );
}

function EvidenceList({
  title,
  items,
  emptyText,
}: {
  title: string;
  items: Record<string, unknown>[];
  emptyText: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 p-4">
      <h3 className="font-semibold text-slate-950">{title}</h3>
      <div className="mt-3 grid gap-2">
        {items.length === 0 ? <p className="text-sm text-slate-500">{emptyText}</p> : null}
        {items.map((item, index) => (
          <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700" key={`${title}-${index}`}>
            <p className="font-medium text-slate-950">
              {String(item.title ?? item.name ?? item.code ?? item.project_id ?? "항목")}
            </p>
            {item.description ? <p className="mt-1 text-slate-500">{String(item.description)}</p> : null}
            {item.evidence ? <p className="mt-1 text-slate-500">근거: {String(item.evidence)}</p> : null}
            {item.reason ? <p className="mt-1 text-slate-500">{String(item.reason)}</p> : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function FeedbackForm({
  feedbackType,
  rating,
  comment,
  isPending,
  onFeedbackTypeChange,
  onRatingChange,
  onCommentChange,
  onSubmit,
}: {
  feedbackType: JobMatchFeedbackType;
  rating: string;
  comment: string;
  isPending: boolean;
  onFeedbackTypeChange: (value: JobMatchFeedbackType) => void;
  onRatingChange: (value: string) => void;
  onCommentChange: (value: string) => void;
  onSubmit: () => void;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 p-4">
      <h3 className="font-semibold text-slate-950">결과 피드백</h3>
      <div className="mt-3 grid gap-3 md:grid-cols-[1fr_120px]">
        <select
          className="input"
          value={feedbackType}
          onChange={(event) => onFeedbackTypeChange(event.target.value as JobMatchFeedbackType)}
        >
          {Object.entries(feedbackLabels).map(([value, label]) => (
            <option value={value} key={value}>
              {label}
            </option>
          ))}
        </select>
        <input
          className="input"
          min={1}
          max={5}
          type="number"
          value={rating}
          onChange={(event) => onRatingChange(event.target.value)}
        />
      </div>
      <textarea
        className="input mt-3 min-h-20"
        placeholder="점수나 근거가 실제와 다른 부분을 남겨주세요."
        value={comment}
        onChange={(event) => onCommentChange(event.target.value)}
      />
      <button className="button-secondary mt-3" type="button" disabled={isPending} onClick={onSubmit}>
        {isPending ? "저장 중..." : "피드백 저장"}
      </button>
    </div>
  );
}

function RunAndFeedbackList({
  runs,
  feedback,
}: {
  runs: { id: number; status: string; total_score: number | null; error_code: string | null }[];
  feedback: { id: number; feedback_type: string; rating: number | null; comment: string | null }[];
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-2xl border border-slate-200 p-4">
        <h3 className="font-semibold text-slate-950">실행 이력</h3>
        <div className="mt-3 grid gap-2 text-sm text-slate-600">
          {runs.length === 0 ? "실행 이력이 없습니다." : null}
          {runs.map((run) => (
            <div className="rounded-xl bg-slate-50 px-3 py-2" key={run.id}>
              #{run.id} · {run.status}
              {run.total_score !== null ? ` · ${run.total_score}점` : ""}
              {run.error_code ? ` · ${run.error_code}` : ""}
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200 p-4">
        <h3 className="font-semibold text-slate-950">피드백</h3>
        <div className="mt-3 grid gap-2 text-sm text-slate-600">
          {feedback.length === 0 ? "저장된 피드백이 없습니다." : null}
          {feedback.map((item) => (
            <div className="rounded-xl bg-slate-50 px-3 py-2" key={item.id}>
              {feedbackLabels[item.feedback_type as JobMatchFeedbackType] ?? item.feedback_type}
              {item.rating ? ` · ${item.rating}/5` : ""}
              {item.comment ? <p className="mt-1 text-slate-500">{item.comment}</p> : null}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Badge({ children }: { children: string }) {
  return <span className="rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">{children}</span>;
}

function ErrorMessage({ message }: { message: string }) {
  return <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{message}</p>;
}
