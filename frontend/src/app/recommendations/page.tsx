import { AppHeader } from "@/components/app-header";
import { RecommendationListPanel } from "@/components/recommendations/recommendation-list-panel";

export default function RecommendationsPage() {
  return (
    <>
      <AppHeader />
      <main className="page-shell">
        <RecommendationListPanel />
      </main>
    </>
  );
}
