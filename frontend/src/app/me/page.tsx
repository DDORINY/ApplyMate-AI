import { AppHeader } from "@/components/app-header";
import { ProtectedUserPanel } from "@/components/auth/protected-user-panel";

export default function MePage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto w-full max-w-2xl">
          <h1 className="text-3xl font-semibold text-slate-950">내 계정</h1>
          <p className="mt-3 text-base leading-7 text-slate-600">
            로그인한 사용자 정보와 인증 상태를 확인하고, 프로필 또는 계정 보안 화면으로 이동할 수
            있습니다.
          </p>
          <div className="mt-6">
            <ProtectedUserPanel />
          </div>
        </section>
      </main>
    </>
  );
}
