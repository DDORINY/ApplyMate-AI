import { DocumentImprovementCreatePanel } from "@/components/documents/document-improvement-create-panel";

export default async function DocumentImprovePage({
  params,
}: {
  params: Promise<{ documentId: string }>;
}) {
  const { documentId } = await params;
  return (
    <main className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-10 sm:px-8">
      <DocumentImprovementCreatePanel documentId={Number(documentId)} />
    </main>
  );
}
