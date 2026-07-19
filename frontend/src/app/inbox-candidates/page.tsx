import { AppHeader } from "@/components/app-header";
import { EmailCandidateListPanel } from "@/components/integrations/email-candidate-list-panel";

export default function InboxCandidatesPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen bg-slate-50 px-5 py-8 sm:px-8">
        <EmailCandidateListPanel />
      </main>
    </>
  );
}
