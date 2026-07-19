import { DocumentCreatePanel } from "@/components/documents/document-create-panel";

export default function NewDocumentPage() {
  return (
    <main className="mx-auto grid w-full max-w-4xl gap-6 px-5 py-10 sm:px-8">
      <div>
        <p className="text-sm font-semibold text-blue-700">New document</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">지원 문서 생성</h1>
        <p className="mt-3 text-slate-600">
          문항과 연결할 근거 ID를 입력하면 AI가 출처가 표시된 초안을 생성합니다.
        </p>
      </div>
      <DocumentCreatePanel />
    </main>
  );
}
