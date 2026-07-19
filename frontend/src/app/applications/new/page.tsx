import { Suspense } from "react";

import { ApplicationCreatePanel } from "@/components/applications/application-create-panel";

export default function NewApplicationPage() {
  return (
    <main className="page-shell">
      <Suspense fallback={<div className="panel max-w-none">지원 항목 생성 화면을 준비하는 중입니다.</div>}>
        <ApplicationCreatePanel />
      </Suspense>
    </main>
  );
}
