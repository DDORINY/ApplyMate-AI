import { AppHeader } from "@/components/app-header";
import { DocumentListPanel } from "@/components/documents/document-list-panel";

export default function DocumentsPage() {
  return (
    <>
      <AppHeader />
      <main className="page-shell grid gap-6">
        <div>
          <p className="text-sm font-semibold text-violet-600">Application documents</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">지원 문서</h1>
          <p className="mt-3 text-slate-600">
            이력서, 커리어 프로필, 채용공고 분석과 적합도 결과를 근거로 자기소개서 초안을 관리합니다.
          </p>
        </div>
        <DocumentListPanel />
      </main>
    </>
  );
}
