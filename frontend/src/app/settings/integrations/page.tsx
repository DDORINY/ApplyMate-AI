import { AppHeader } from "@/components/app-header";
import { CalendarIntegrationPanel } from "@/components/integrations/calendar-integration-panel";
import { GmailIntegrationPanel } from "@/components/integrations/gmail-integration-panel";

export default function SettingsIntegrationsPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <CalendarIntegrationPanel />
        <GmailIntegrationPanel />
      </main>
    </>
  );
}
