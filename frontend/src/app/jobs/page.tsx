import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { JobListPanel } from "@/components/jobs/job-list-panel";

export default function JobsPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto grid w-full max-w-6xl gap-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-medium text-sky-700">ApplyMate AI v0.2.0</p>
              <h1 className="mt-2 text-3xl font-semibold text-slate-950">채용공고 관리</h1>
              <p className="mt-2 text-slate-600">관심 공고를 직접 등록하거나 URL로 가져오고, 상태와 메모를 관리합니다.</p>
            </div>
            <Link className="button-primary" href="/jobs/new">
              채용공고 등록
            </Link>
          </div>
          <JobListPanel />
        </section>
      </main>
    </>
  );
}
