import { Suspense } from "react";

import { AppHeader } from "@/components/app-header";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";

export default function ResetPasswordPage() {
  return (
    <>
      <AppHeader />
      <main className="auth-page">
        <section className="auth-card">
          <h1 className="text-2xl font-semibold text-slate-950">비밀번호 재설정</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            메일로 받은 링크가 유효하면 새 비밀번호를 설정할 수 있습니다.
          </p>
          <div className="mt-6">
            <Suspense fallback={<p className="text-sm text-slate-600">토큰을 확인하는 중입니다.</p>}>
              <ResetPasswordForm />
            </Suspense>
          </div>
        </section>
      </main>
    </>
  );
}
