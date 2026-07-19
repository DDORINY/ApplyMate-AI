import { AppHeader } from "@/components/app-header";
import { ResumeCreatePanel } from "@/components/resumes/resume-create-panel";

export default function NewResumePage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto grid w-full max-w-3xl gap-5">
          <div>
            <p className="text-sm font-medium text-sky-700">ApplyMate AI v0.3.0</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-950">이력서 업로드</h1>
            <p className="mt-2 text-slate-600">원본 파일명은 표시용으로만 저장하고 내부 파일명은 UUID로 분리합니다.</p>
          </div>
          <ResumeCreatePanel />
        </section>
      </main>
    </>
  );
}
