import Link from "next/link";

import { AppHeader } from "@/components/app-header";
import { ServiceStatusPanel } from "@/components/service-status-panel";

export default function Home() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto flex w-full max-w-4xl flex-col gap-6">
          <div>
            <p className="text-sm font-medium text-sky-700">ApplyMate AI v0.1.3</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-slate-950 sm:text-4xl">
              개인용 AI 취업 매니저
            </h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
              회원가입, 로그인, 소셜 로그인, 커리어 프로필, 기술 스택, 경력, 프로젝트,
              희망 조건을 한 곳에서 관리합니다.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link className="button-primary" href="/profile">
                프로필 관리
              </Link>
              <Link className="button-secondary" href="/signup">
                회원가입
              </Link>
              <Link className="button-secondary" href="/login">
                로그인
              </Link>
              <Link className="button-secondary" href="/settings/accounts">
                소셜 계정 연결
              </Link>
            </div>
          </div>
          <ServiceStatusPanel />
        </section>
      </main>
    </>
  );
}
