import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { ApplicationListPanel } from "@/components/applications/application-list-panel";

export default function ApplicationsPage() {
  return (
    <>
      <AppHeader />
      <main className="page-shell">
        <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">Applications</p>
            <h1 className="mt-1 text-3xl font-bold text-slate-950">지원 현황</h1>
            <p className="mt-2 text-slate-600">지원 준비부터 결과까지 공고별 진행 상태를 한 곳에서 관리합니다.</p>
          </div>
          <Link className="button-primary" href="/applications/new">
            지원 항목 추가
          </Link>
        </div>
        <ApplicationListPanel />
      </main>
    </>
  );
}
