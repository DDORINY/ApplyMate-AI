import { AppHeader } from "@/components/app-header";
import { RecommendationHistoryPanel } from "@/components/recommendations/recommendation-history-panel";

export default function RecommendationHistoryPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-6">
      <AppHeader />
      <RecommendationHistoryPanel />
    </main>
  );
}
