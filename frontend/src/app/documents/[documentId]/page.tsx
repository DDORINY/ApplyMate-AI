import { DocumentDetailPanel } from "@/components/documents/document-detail-panel";

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ documentId: string }>;
}) {
  const { documentId } = await params;
  return (
    <main className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-10 sm:px-8">
      <DocumentDetailPanel documentId={Number(documentId)} />
    </main>
  );
}
