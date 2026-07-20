import { AppHeader } from "@/components/app-header";
import { RecommendationSettingsPanel } from "@/components/recommendations/recommendation-settings-panel";

export default function RecommendationSettingsPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-6">
      <AppHeader />
      <RecommendationSettingsPanel />
    </main>
  );
}
