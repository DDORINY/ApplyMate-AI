import { AppHeader } from "@/components/app-header";
import { AccountSecurityPanel } from "@/components/auth/account-security-panel";

export default function SecuritySettingsPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto w-full max-w-4xl">
          <h1 className="text-3xl font-semibold text-slate-950">계정 보안</h1>
          <p className="mt-3 text-base leading-7 text-slate-600">
            이메일 인증, 비밀번호, 로그인 세션과 최근 보안 이벤트를 한 곳에서 관리합니다.
          </p>
          <div className="mt-6">
            <AccountSecurityPanel />
          </div>
        </section>
      </main>
    </>
  );
}
