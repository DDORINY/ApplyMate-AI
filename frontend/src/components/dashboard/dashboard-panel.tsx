"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import type { ReactNode } from "react";
import { useState } from "react";

import { getDashboard } from "@/lib/api/dashboard";
import { listJobRecommendationSnapshots, listJobRecommendations } from "@/lib/api/job-recommendation";
import type {
  DashboardActivityItem,
  DashboardData,
  DashboardDeadlineItem,
  DashboardPeriod,
  DashboardPreparingApplication,
  DashboardRecentDocument,
  DashboardRecentJobAnalysis,
  DashboardRecentMatch,
  DashboardRecentResumeAnalysis,
  DashboardScheduleItem,
} from "@/types/dashboard";
import type { JobRecommendation, JobRecommendationSnapshot } from "@/types/job-recommendation";

const periodOptions: { label: string; value: DashboardPeriod }[] = [
  { label: "최근 7일", value: "7d" },
  { label: "최근 30일", value: "30d" },
  { label: "최근 90일", value: "90d" },
  { label: "전체", value: "all" },
];

const statusLabels: Record<string, string> = {
  PREPARING: "지원 준비",
  APPLIED: "지원 완료",
  IN_PROGRESS: "전형 진행",
  INTERVIEW: "면접",
  OFFER: "합격/오퍼",
  REJECTED: "불합격",
  WITHDRAWN: "철회",
  CLOSED: "종료",
};

const activityLabels: Record<string, string> = {
  APPLICATION_UPDATED: "지원 현황",
  SCHEDULE_EVENT: "일정",
  JOB_ANALYSIS: "공고 분석",
  JOB_MATCH: "적합도",
  RESUME_ANALYSIS: "이력서 분석",
  APPLICATION_DOCUMENT: "지원 문서",
};

export function DashboardPanel() {
  const [period, setPeriod] = useState<DashboardPeriod>("30d");
  const dashboardQuery = useQuery({
    queryKey: ["dashboard", period],
    queryFn: () => getDashboard({ period, timezone: "Asia/Seoul", recent_limit: 6 }),
    retry: false,
  });
  const recommendationsQuery = useQuery({
    queryKey: ["dashboard-job-recommendations"],
    queryFn: () => listJobRecommendations({ include_outdated: false, size: 3 }),
    retry: false,
  });
  const recommendationSnapshotsQuery = useQuery({
    queryKey: ["dashboard-job-recommendation-snapshots"],
    queryFn: () => listJobRecommendationSnapshots({ size: 1 }),
    retry: false,
  });

  if (dashboardQuery.isLoading) {
    return <DashboardSkeleton />;
  }

  if (dashboardQuery.error) {
    return (
      <section className="panel max-w-none">
        <p className="text-sm font-semibold text-rose-700">대시보드를 불러오지 못했습니다.</p>
        <p className="mt-2 text-sm text-slate-600">{dashboardQuery.error.message}</p>
      </section>
    );
  }

  const dashboard = dashboardQuery.data?.data;
  if (!dashboard) {
    return (
      <section className="panel max-w-none">
        <p className="text-sm text-slate-600">표시할 대시보드 데이터가 없습니다.</p>
      </section>
    );
  }

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-sky-700">Dashboard</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">오늘의 지원 현황</h1>
            <p className="mt-2 text-sm text-slate-600">
              지원 상태, 일정, 마감, 최근 AI 분석 결과를 한 화면에서 확인합니다.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {periodOptions.map((option) => (
              <button
                className={period === option.value ? "button-primary" : "button-secondary"}
                key={option.value}
                type="button"
                onClick={() => setPeriod(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-500">
          기준 시간대: {dashboard.timezone} · 생성 시각: {formatDateTime(dashboard.generated_at)}
        </p>
      </section>

      <section className="panel max-w-none overflow-hidden">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">RULE_BASED</p>
            <h2 className="mt-1 text-2xl font-black text-slate-950">규칙 기반 채용공고 추천</h2>
            <p className="mt-2 text-sm text-slate-600">
              저장된 공고와 커리어 프로필을 비교해 추천 점수, 추천 이유, 부족 조건을 확인합니다.
            </p>
          </div>
          <Link className="button-primary" href="/recommendations">
            추천 공고 보기
          </Link>
        </div>
      </section>

      <DashboardRecommendationSection
        isLoading={recommendationsQuery.isLoading}
        items={recommendationsQuery.data?.data.items ?? []}
        latestSnapshot={recommendationSnapshotsQuery.data?.data.items[0] ?? null}
      />

      <SummaryCards dashboard={dashboard} />

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <StatusDistribution dashboard={dashboard} />
        <ActivityCard dashboard={dashboard} />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <ScheduleSection title="오늘 일정" items={dashboard.today_events} emptyText="오늘 예정된 일정이 없습니다." />
        <ScheduleSection title="이번 주 일정" items={dashboard.week_events} emptyText="이번 주 일정이 없습니다." />
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <DeadlineSection title="다가오는 일정 마감" items={dashboard.upcoming_deadlines} />
        <DeadlineSection title="마감 임박 공고" items={dashboard.due_soon_jobs} />
        <PreparingSection items={dashboard.preparing_applications} />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <JobAnalysisSection items={dashboard.recent_job_analyses} />
        <MatchSection items={dashboard.recent_matches} />
        <ResumeAnalysisSection items={dashboard.recent_resume_analyses} />
        <DocumentSection items={dashboard.recent_documents} />
      </div>
    </div>
  );
}

function DashboardRecommendationSection({
  isLoading,
  items,
  latestSnapshot,
}: {
  isLoading: boolean;
  items: JobRecommendation[];
  latestSnapshot: JobRecommendationSnapshot | null;
}) {
  const gradeLabels: Record<string, string> = {
    EXCELLENT: "매우 적합",
    GOOD: "적합",
    POSSIBLE: "검토 가능",
    LOW: "낮음",
    BLOCKED: "필수 조건 확인",
  };

  return (
    <section className="grid gap-3 lg:grid-cols-3">
      {isLoading ? (
        <div className="panel max-w-none lg:col-span-3">
          <p className="text-sm text-slate-500">추천 공고를 불러오는 중입니다.</p>
        </div>
      ) : null}
      {!isLoading && items.length === 0 ? (
        <Link className="panel max-w-none border-dashed lg:col-span-3" href="/recommendations">
          <p className="text-sm font-semibold text-violet-600">추천 준비</p>
          <h2 className="mt-1 text-lg font-bold text-slate-950">아직 생성된 추천 공고가 없습니다.</h2>
          <p className="mt-2 text-sm text-slate-600">저장된 공고와 프로필을 기준으로 추천을 생성해 보세요.</p>
        </Link>
      ) : null}
      {latestSnapshot ? (
        <Link className="rounded-3xl border border-violet-100 bg-violet-600 p-5 text-white shadow-sm transition hover:bg-violet-700" href="/recommendations/history">
          <p className="text-sm font-semibold opacity-80">마지막 추천 실행</p>
          <h2 className="mt-1 text-lg font-bold">{formatDateTime(latestSnapshot.generated_at)}</h2>
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs font-bold">
            <span className="rounded-2xl bg-white/15 px-2 py-2">신규 {latestSnapshot.new_count}</span>
            <span className="rounded-2xl bg-white/15 px-2 py-2">변경 {latestSnapshot.changed_count}</span>
            <span className="rounded-2xl bg-white/15 px-2 py-2">추천 {latestSnapshot.recommended_count}</span>
          </div>
        </Link>
      ) : null}
      {items.map((item) => (
        <Link className="rounded-3xl border border-violet-100 bg-white p-5 shadow-sm transition hover:border-violet-300" href={`/recommendations/${item.id}`} key={item.id}>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-violet-600">{item.job.company_name}</p>
              <h2 className="mt-1 text-lg font-bold text-slate-950">{item.job.title}</h2>
            </div>
            <div className="rounded-2xl bg-violet-50 px-3 py-2 text-right">
              <p className="text-xl font-black text-violet-600">{item.score}</p>
              <p className="text-[11px] font-bold text-violet-500">{gradeLabels[item.grade]}</p>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-500">
            {item.recommendation_type} · {item.job.location ?? "지역 미상"}
          </p>
        </Link>
      ))}
    </section>
  );
}

function SummaryCards({ dashboard }: { dashboard: DashboardData }) {
  const cards = [
    { label: "전체 지원", value: dashboard.summary.total_applications, href: "/applications" },
    { label: "지원 준비", value: dashboard.summary.preparing_applications, href: "/applications?status=PREPARING" },
    { label: "전형 진행", value: dashboard.summary.in_progress_applications, href: "/applications" },
    { label: "이번 주 일정", value: dashboard.summary.week_events, href: "/calendar" },
    { label: "다가오는 마감", value: dashboard.summary.upcoming_deadlines, href: "/calendar" },
    { label: "마감 임박 공고", value: dashboard.summary.due_soon_jobs, href: "/jobs" },
  ];
  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
      {cards.map((card) => (
        <Link className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-sky-300" href={card.href} key={card.label}>
          <p className="text-sm font-medium text-slate-500">{card.label}</p>
          <p className="mt-3 text-3xl font-bold text-slate-950">{card.value}</p>
        </Link>
      ))}
    </section>
  );
}

function StatusDistribution({ dashboard }: { dashboard: DashboardData }) {
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-semibold text-slate-950">지원 상태 분포</h2>
      <div className="mt-4 grid gap-3">
        {dashboard.application_status_counts.map((item) => (
          <div key={item.group}>
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-slate-700">{statusLabels[item.group] ?? item.label}</span>
              <span className="text-slate-500">
                {item.count}건 · {item.percentage}%
              </span>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full rounded-full bg-sky-600" style={{ width: `${Math.min(item.percentage, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function ActivityCard({ dashboard }: { dashboard: DashboardData }) {
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-semibold text-slate-950">최근 활동</h2>
      <div className="mt-4 grid gap-3">
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">선택 기간 신규 지원</p>
          <p className="mt-2 text-2xl font-bold text-slate-950">{dashboard.application_activity.new_applications}건</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">선택 기간 상태 변경</p>
          <p className="mt-2 text-2xl font-bold text-slate-950">{dashboard.application_activity.status_changes}건</p>
        </div>
        <div className="grid gap-2">
          {dashboard.recent_activities.map((item) => (
            <ActivityItem item={item} key={item.id} />
          ))}
          {dashboard.recent_activities.length === 0 ? <p className="text-sm text-slate-500">최근 활동이 없습니다.</p> : null}
        </div>
      </div>
    </section>
  );
}

function ScheduleSection({ title, items, emptyText }: { title: string; items: DashboardScheduleItem[]; emptyText: string }) {
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      <div className="mt-4 grid gap-3">
        {items.map((item) => (
          <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={`/calendar/events/${item.id}`} key={item.id}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold text-sky-700">{item.event_type}</p>
                <h3 className="mt-1 font-semibold text-slate-950">{item.title}</h3>
                <p className="mt-1 text-sm text-slate-600">{formatDateTime(item.start_at)}</p>
              </div>
              <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                {item.effective_status}
              </span>
            </div>
            {item.has_conflict ? <p className="mt-3 text-sm font-medium text-amber-700">겹치는 일정이 있습니다.</p> : null}
          </Link>
        ))}
        {items.length === 0 ? <p className="text-sm text-slate-500">{emptyText}</p> : null}
      </div>
    </section>
  );
}

function DeadlineSection({ title, items }: { title: string; items: DashboardDeadlineItem[] }) {
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      <div className="mt-4 grid gap-3">
        {items.map((item) => (
          <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={item.link_path} key={`${item.kind}-${item.id}`}>
            <p className="text-xs font-semibold text-rose-700">{item.kind === "JOB" ? "공고 마감" : "일정 마감"}</p>
            <h3 className="mt-1 font-semibold text-slate-950">{item.job_title ?? item.title}</h3>
            <p className="mt-1 text-sm text-slate-600">{item.company_name ?? "회사 정보 없음"}</p>
            <p className="mt-2 text-xs text-slate-500">{formatDateTime(item.due_at)} · {formatHours(item.hours_remaining)}</p>
          </Link>
        ))}
        {items.length === 0 ? <p className="text-sm text-slate-500">7일 이내 마감 항목이 없습니다.</p> : null}
      </div>
    </section>
  );
}

function PreparingSection({ items }: { items: DashboardPreparingApplication[] }) {
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-semibold text-slate-950">지원 준비 중</h2>
      <div className="mt-4 grid gap-3">
        {items.map((item) => (
          <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={item.link_path} key={item.id}>
            <p className="text-xs font-semibold text-sky-700">{item.priority}</p>
            <h3 className="mt-1 font-semibold text-slate-950">{item.job_title ?? "직무 정보 없음"}</h3>
            <p className="mt-1 text-sm text-slate-600">{item.company_name ?? "회사 정보 없음"}</p>
            <p className="mt-2 text-xs text-slate-500">
              계획일: {item.planned_apply_at ? formatDateTime(item.planned_apply_at) : "미정"}
            </p>
          </Link>
        ))}
        {items.length === 0 ? <p className="text-sm text-slate-500">준비 중인 지원 항목이 없습니다.</p> : null}
      </div>
    </section>
  );
}

function JobAnalysisSection({ items }: { items: DashboardRecentJobAnalysis[] }) {
  return (
    <RecentSection title="최근 공고 분석" emptyText="최근 공고 분석 결과가 없습니다.">
      {items.map((item) => (
        <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={item.link_path} key={item.id}>
          <p className="text-xs font-semibold text-sky-700">{item.status}</p>
          <h3 className="mt-1 font-semibold text-slate-950">{item.job_title ?? "공고 정보 없음"}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-slate-600">{item.summary ?? "요약 정보가 없습니다."}</p>
          <p className="mt-2 text-xs text-slate-500">{formatDateTime(item.updated_at)}</p>
        </Link>
      ))}
    </RecentSection>
  );
}

function MatchSection({ items }: { items: DashboardRecentMatch[] }) {
  return (
    <RecentSection title="최근 적합도 분석" emptyText="최근 적합도 분석 결과가 없습니다.">
      {items.map((item) => (
        <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={item.link_path} key={item.id}>
          <div className="flex items-center justify-between gap-3">
            <h3 className="font-semibold text-slate-950">{item.job_title ?? "공고 정보 없음"}</h3>
            <span className="rounded-full bg-sky-100 px-2 py-1 text-xs font-bold text-sky-700">{item.total_score}점</span>
          </div>
          <p className="mt-1 text-sm text-slate-600">{item.grade} · {item.recommendation_status}</p>
          <p className="mt-2 text-xs text-slate-500">{formatDateTime(item.updated_at)}</p>
        </Link>
      ))}
    </RecentSection>
  );
}

function ResumeAnalysisSection({ items }: { items: DashboardRecentResumeAnalysis[] }) {
  return (
    <RecentSection title="최근 이력서 분석" emptyText="최근 이력서 분석 결과가 없습니다.">
      {items.map((item) => (
        <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={item.link_path} key={item.id}>
          <p className="text-xs font-semibold text-sky-700">{item.status}</p>
          <h3 className="mt-1 font-semibold text-slate-950">{item.resume_title ?? item.filename ?? "이력서"}</h3>
          <p className="mt-1 text-sm text-slate-600">기술 {item.skills_count}개 · 경험 {item.experiences_count}개</p>
          <p className="mt-2 text-xs text-slate-500">{formatDateTime(item.updated_at)}</p>
        </Link>
      ))}
    </RecentSection>
  );
}

function DocumentSection({ items }: { items: DashboardRecentDocument[] }) {
  return (
    <RecentSection title="최근 지원 문서" emptyText="최근 생성된 지원 문서가 없습니다.">
      {items.map((item) => (
        <Link className="rounded-2xl border border-slate-200 p-4 transition hover:border-sky-300" href={item.link_path} key={item.id}>
          <p className="text-xs font-semibold text-sky-700">{item.document_type}</p>
          <h3 className="mt-1 font-semibold text-slate-950">{item.title}</h3>
          <p className="mt-1 text-sm text-slate-600">버전 {item.current_version_number ?? 0} · {item.status}</p>
          <p className="mt-2 text-xs text-slate-500">{formatDateTime(item.updated_at)}</p>
        </Link>
      ))}
    </RecentSection>
  );
}

function RecentSection({ title, emptyText, children }: { title: string; emptyText: string; children: ReactNode }) {
  const hasChildren = Array.isArray(children) ? children.length > 0 : Boolean(children);
  return (
    <section className="panel max-w-none">
      <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      <div className="mt-4 grid gap-3">{hasChildren ? children : <p className="text-sm text-slate-500">{emptyText}</p>}</div>
    </section>
  );
}

function ActivityItem({ item }: { item: DashboardActivityItem }) {
  const content = (
    <div className="rounded-2xl border border-slate-200 p-3">
      <p className="text-xs font-semibold text-slate-500">{activityLabels[item.activity_type] ?? item.activity_type}</p>
      <p className="mt-1 text-sm font-semibold text-slate-950">{item.title}</p>
      <p className="mt-1 text-xs text-slate-500">{formatDateTime(item.occurred_at)}</p>
    </div>
  );
  return item.link_path ? (
    <Link className="transition hover:opacity-80" href={item.link_path}>
      {content}
    </Link>
  ) : (
    content
  );
}

function DashboardSkeleton() {
  return (
    <div className="grid gap-5">
      {Array.from({ length: 4 }).map((_, index) => (
        <section className="panel max-w-none animate-pulse" key={index}>
          <div className="h-5 w-40 rounded bg-slate-200" />
          <div className="mt-4 h-24 rounded bg-slate-100" />
        </section>
      ))}
    </div>
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatHours(value: number | null) {
  if (value === null) {
    return "남은 시간 미정";
  }
  if (value < 0) {
    return "기한 지남";
  }
  if (value < 24) {
    return `${value}시간 남음`;
  }
  return `${Math.floor(value / 24)}일 남음`;
}
