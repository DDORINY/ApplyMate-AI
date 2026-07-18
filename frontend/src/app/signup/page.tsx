import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { OAuthButtons } from "@/components/auth/oauth-buttons";
import { SignupForm } from "@/components/auth/signup-form";

export default function SignupPage() {
  return (
    <>
      <AppHeader />
      <main className="auth-page">
        <section className="auth-card">
          <p className="text-sm font-medium text-sky-700">ApplyMate AI</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">회원가입</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Google 또는 GitHub로 빠르게 시작하거나, 이메일과 비밀번호로 계정을 만들 수 있습니다.
          </p>
          <div className="mt-6">
            <OAuthButtons redirectPath="/me" />
          </div>
          <Divider />
          <SignupForm />
          <p className="mt-5 text-sm text-slate-600">
            이미 계정이 있나요?{" "}
            <Link className="font-medium text-sky-700" href="/login">
              로그인
            </Link>
          </p>
        </section>
      </main>
    </>
  );
}

function Divider() {
  return (
    <div className="my-6 flex items-center gap-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
      <span className="h-px flex-1 bg-slate-200" />
      또는
      <span className="h-px flex-1 bg-slate-200" />
    </div>
  );
}
