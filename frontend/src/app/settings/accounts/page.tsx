import { AppHeader } from "@/components/app-header";
import { OAuthAccountsManager } from "@/components/auth/oauth-accounts-manager";

export default function SettingsAccountsPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <OAuthAccountsManager />
      </main>
    </>
  );
}
