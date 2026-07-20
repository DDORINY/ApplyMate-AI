import { AppHeader } from "@/components/app-header";
import { RecommendationDetailPanel } from "@/components/recommendations/recommendation-detail-panel";

export default async function RecommendationDetailPage({
  params,
}: {
  params: Promise<{ recommendationId: string }>;
}) {
  const { recommendationId } = await params;
  return (
    <>
      <AppHeader />
      <main className="page-shell">
        <RecommendationDetailPanel recommendationId={Number(recommendationId)} />
      </main>
    </>
  );
}
