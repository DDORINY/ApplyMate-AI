import { AppHeader } from "@/components/app-header";
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";

export default function ForgotPasswordPage() {
  return (
    <>
      <AppHeader />
      <main className="auth-page">
        <section className="auth-card">
          <h1 className="text-2xl font-semibold text-slate-950">비밀번호 찾기</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            가입한 이메일을 입력하면 계정이 존재하는 경우 재설정 링크를 발송합니다.
          </p>
          <div className="mt-6">
            <ForgotPasswordForm />
          </div>
        </section>
      </main>
    </>
  );
}
