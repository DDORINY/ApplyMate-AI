import { Suspense } from "react";

import { AppHeader } from "@/components/app-header";
import { VerifyEmailPanel } from "@/components/auth/verify-email-panel";

export default function VerifyEmailPage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto w-full max-w-2xl">
          <h1 className="text-3xl font-semibold text-slate-950">이메일 인증</h1>
          <p className="mt-3 text-base leading-7 text-slate-600">
            ApplyMate AI 계정의 이메일 인증 링크를 확인합니다.
          </p>
          <div className="mt-6">
            <Suspense fallback={<div className="panel">인증 링크를 확인하는 중입니다.</div>}>
              <VerifyEmailPanel />
            </Suspense>
          </div>
        </section>
      </main>
    </>
  );
}
