"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "홈", icon: "⌂" },
  { href: "/dashboard", label: "대시보드", icon: "▣" },
  { href: "/profile", label: "커리어 프로필", icon: "◇" },
  { href: "/jobs", label: "채용공고", icon: "✦" },
  { href: "/resumes", label: "이력서", icon: "◫" },
  { href: "/documents", label: "지원 문서", icon: "✎" },
  { href: "/applications", label: "지원 현황", icon: "●" },
  { href: "/calendar", label: "일정", icon: "◷" },
  { href: "/inbox-candidates", label: "메일 후보", icon: "✉" },
  { href: "/recommendations", label: "공고 추천", icon: "★" },
];

const accountItems = [
  { href: "/login", label: "로그인" },
  { href: "/signup", label: "회원가입" },
  { href: "/me", label: "내 계정" },
  { href: "/settings/accounts", label: "계정 연결" },
  { href: "/settings/integrations", label: "외부 연동" },
  { href: "/settings/recommendations", label: "추천 설정" },
  { href: "/settings/security", label: "보안" },
];

function isActive(pathname: string, href: string) {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppHeader() {
  const pathname = usePathname();

  return (
    <aside className="app-sidebar" aria-label="ApplyMate AI 앱 내비게이션">
      <div className="app-sidebar-inner">
        <div className="space-y-5">
          <Link className="flex items-center gap-3" href="/">
            <span className="app-brand-mark">A</span>
            <span>
              <span className="block text-sm font-black tracking-tight text-slate-950">ApplyMate</span>
              <span className="block text-xs font-semibold text-violet-500">AI 취업 매니저</span>
            </span>
          </Link>

          <nav aria-label="주요 화면" className="grid gap-1">
            {navItems.map((item) => (
              <Link
                className={`nav-link ${isActive(pathname, item.href) ? "nav-link-active" : ""}`}
                href={item.href}
                key={item.href}
              >
                <span aria-hidden="true" className="w-4 text-center text-xs">
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>

        <div className="app-sidebar-cta hidden lg:block">
          <p className="text-xs font-semibold opacity-80">오늘의 추천 준비</p>
          <p className="mt-2 text-sm font-bold leading-5">지원 현황과 일정을 한 화면에서 정리해 보세요.</p>
          <Link
            className="mt-4 inline-flex rounded-full bg-white px-4 py-2 text-xs font-bold text-violet-700"
            href="/dashboard"
          >
            대시보드 보기
          </Link>
        </div>

        <nav aria-label="회원 및 계정 관리" className="grid gap-1 border-t border-violet-100 pt-4">
          <p className="px-2 text-xs font-bold uppercase tracking-wider text-violet-400">계정 관리</p>
          {accountItems.map((item) => (
            <Link
              className={`nav-link ${isActive(pathname, item.href) ? "nav-link-active" : ""}`}
              href={item.href}
              key={item.href}
            >
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  );
}
