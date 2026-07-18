import { ServiceStatusPanel } from "@/components/service-status-panel";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen px-5 py-8 sm:px-8">
      <section className="mx-auto flex w-full max-w-4xl flex-col gap-6">
        <div>
          <p className="text-sm font-medium text-sky-700">ApplyMate AI v0.1.0</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-normal text-slate-950 sm:text-4xl">
            서비스 상태
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
            프론트엔드와 백엔드, PostgreSQL, Redis 연결 상태를 확인합니다.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link className="button-primary" href="/signup">
              회원가입
            </Link>
            <Link className="button-secondary" href="/login">
              로그인
            </Link>
            <Link className="button-secondary" href="/me">
              내 계정
            </Link>
          </div>
        </div>
        <ServiceStatusPanel />
      </section>
    </main>
  );
}
