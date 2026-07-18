import Link from "next/link";

import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="text-sm font-medium text-sky-700">ApplyMate AI</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">로그인</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          로그인하면 보호된 사용자 정보 화면으로 이동합니다.
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
  );
}
