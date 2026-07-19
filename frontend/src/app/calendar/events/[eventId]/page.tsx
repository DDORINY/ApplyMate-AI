import { CalendarDetailPanel } from "@/components/calendar/calendar-detail-panel";

export default async function CalendarEventDetailPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;

  return (
    <main className="page-shell">
      <CalendarDetailPanel eventId={Number(eventId)} />
    </main>
  );
}
