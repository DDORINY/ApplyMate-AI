import { Suspense } from "react";

import { CalendarCreatePanel } from "@/components/calendar/calendar-create-panel";

export default function NewCalendarEventPage() {
  return (
    <main className="page-shell">
      <Suspense fallback={<div className="panel max-w-none">일정 생성 화면을 준비하는 중입니다.</div>}>
        <CalendarCreatePanel />
      </Suspense>
    </main>
  );
}
