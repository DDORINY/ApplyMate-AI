import { AppHeader } from "@/components/app-header";
import { DashboardPanel } from "@/components/dashboard/dashboard-panel";

export default function DashboardPage() {
  return (
    <>
      <AppHeader />
      <main className="page-shell">
        <DashboardPanel />
      </main>
    </>
  );
}
