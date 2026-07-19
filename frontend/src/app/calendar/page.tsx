import Link from "next/link";
import { Suspense } from "react";

import { CalendarListPanel } from "@/components/calendar/calendar-list-panel";

export default function CalendarPage() {
  return (
    <main className="page-shell">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-500">Calendar</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-950">일정 관리</h1>
          <p className="mt-2 text-slate-600">지원 마감, 코딩 테스트, 과제, 면접, 결과 발표를 한곳에서 관리합니다.</p>
        </div>
        <Link className="button-primary" href="/calendar/new">
          일정 추가
        </Link>
      </div>
      <Suspense fallback={<div className="panel max-w-none">일정 목록을 준비하는 중입니다.</div>}>
        <CalendarListPanel />
      </Suspense>
    </main>
  );
}
