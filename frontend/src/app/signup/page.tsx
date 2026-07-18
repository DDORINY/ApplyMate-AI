import Link from "next/link";

import { SignupForm } from "@/components/auth/signup-form";

export default function SignupPage() {
  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="text-sm font-medium text-sky-700">ApplyMate AI</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">회원가입</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          이메일과 비밀번호로 계정을 생성합니다.
        </p>
        <div className="mt-6">
          <SignupForm />
        </div>
        <p className="mt-5 text-sm text-slate-600">
          이미 계정이 있나요?{" "}
          <Link className="font-medium text-sky-700" href="/login">
            로그인
          </Link>
        </p>
      </section>
    </main>
  );
}
