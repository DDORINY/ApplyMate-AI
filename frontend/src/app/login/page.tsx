import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { LoginForm } from "@/components/auth/login-form";
import { OAuthButtons } from "@/components/auth/oauth-buttons";

export default function LoginPage() {
  return (
    <>
      <AppHeader />
      <main className="auth-page">
        <section className="auth-card">
          <p className="text-sm font-medium text-sky-700">ApplyMate AI</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">로그인</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            이메일 로그인 또는 소셜 로그인을 사용해 지원 현황과 커리어 프로필을 이어서 관리하세요.
          </p>
          <div className="mt-6">
            <OAuthButtons redirectPath="/me" />
          </div>
          <Divider />
          <LoginForm />
          <p className="mt-5 text-sm text-slate-600">
            계정이 없나요?{" "}
            <Link className="font-medium text-sky-700" href="/signup">
              회원가입
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
