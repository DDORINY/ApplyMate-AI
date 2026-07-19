import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { JobCreatePanel } from "@/components/jobs/job-create-panel";

export default function NewJobPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto grid w-full max-w-5xl gap-5">
          <div>
            <Link className="text-sm font-medium text-sky-700 hover:underline" href="/jobs">
              ← 채용공고 목록
            </Link>
            <h1 className="mt-3 text-3xl font-semibold text-slate-950">채용공고 등록</h1>
            <p className="mt-2 text-slate-600">직접 입력 또는 URL 등록 방식으로 개인 채용공고 보관함에 저장합니다.</p>
          </div>
          <JobCreatePanel />
        </section>
      </main>
    </>
  );
}
