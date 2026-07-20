import { DocumentImprovementDetailPanel } from "@/components/documents/document-improvement-detail-panel";

export default async function DocumentImprovementRunPage({
  params,
}: {
  params: Promise<{ documentId: string; runId: string }>;
}) {
  const { documentId, runId } = await params;
  return (
    <main className="mx-auto grid w-full max-w-7xl gap-6 px-5 py-10 sm:px-8">
      <DocumentImprovementDetailPanel documentId={Number(documentId)} runId={Number(runId)} />
    </main>
  );
}
