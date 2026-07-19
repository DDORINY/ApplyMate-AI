import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { ResumeListPanel } from "@/components/resumes/resume-list-panel";

export default function ResumesPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto grid w-full max-w-6xl gap-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-medium text-sky-700">ApplyMate AI v0.3.0</p>
              <h1 className="mt-2 text-3xl font-semibold text-slate-950">이력서 관리</h1>
              <p className="mt-2 text-slate-600">PDF 또는 DOCX 이력서를 업로드하고 후속 분석의 근거 파일로 관리합니다.</p>
            </div>
            <Link className="button-primary" href="/resumes/new">
              이력서 업로드
            </Link>
          </div>
          <ResumeListPanel />
        </section>
      </main>
    </>
  );
}
