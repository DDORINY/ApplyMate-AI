import { Suspense } from "react";

import { AppHeader } from "@/components/app-header";
import { OAuthCallbackPanel } from "@/components/auth/oauth-callback-panel";

export default function OAuthCallbackPage() {
  return (
    <>
      <AppHeader />
      <main className="auth-page">
        <Suspense fallback={<div className="panel">소셜 로그인을 확인하고 있습니다.</div>}>
          <OAuthCallbackPanel />
        </Suspense>
      </main>
    </>
  );
}
