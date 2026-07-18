import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <>
      <AppHeader />
      <main className="auth-page">
        <section className="auth-card">
          <p className="text-sm font-medium text-sky-700">ApplyMate AI</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">로그인</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            로그인하면 내 계정과 커리어 프로필 화면을 사용할 수 있습니다.
          </p>
          <div className="mt-6">
            <LoginForm />
          </div>
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
