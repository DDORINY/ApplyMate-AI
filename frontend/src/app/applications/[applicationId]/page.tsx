import { ApplicationDetailPanel } from "@/components/applications/application-detail-panel";

export default async function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ applicationId: string }>;
}) {
  const { applicationId } = await params;

  return (
    <main className="page-shell">
      <ApplicationDetailPanel applicationId={Number(applicationId)} />
    </main>
  );
}
