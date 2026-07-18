import { ProtectedUserPanel } from "@/components/auth/protected-user-panel";

export default function MePage() {
  return (
    <main className="min-h-screen px-5 py-8 sm:px-8">
      <section className="mx-auto w-full max-w-2xl">
        <h1 className="text-3xl font-semibold text-slate-950">내 계정</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          Access Token과 HttpOnly Refresh Token으로 보호되는 인증 확인 화면입니다.
        </p>
        <div className="mt-6">
          <ProtectedUserPanel />
        </div>
      </section>
    </main>
  );
}
