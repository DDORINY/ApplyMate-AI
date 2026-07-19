import Link from "next/link";

const navItems = [
  { href: "/", label: "홈" },
  { href: "/dashboard", label: "대시보드" },
  { href: "/profile", label: "프로필" },
  { href: "/jobs", label: "채용공고" },
  { href: "/resumes", label: "이력서" },
  { href: "/documents", label: "지원 문서" },
  { href: "/applications", label: "지원 현황" },
  { href: "/calendar", label: "일정" },
];

const accountItems = [
  { href: "/login", label: "로그인" },
  { href: "/signup", label: "회원가입" },
  { href: "/me", label: "내 계정" },
  { href: "/settings/accounts", label: "계정 연결" },
  { href: "/settings/security", label: "보안" },
];

export function AppHeader() {
  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-5 py-4 sm:px-8 lg:flex-row lg:items-center lg:justify-between">
        <Link className="text-lg font-semibold text-slate-950" href="/">
          ApplyMate AI
        </Link>
        <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center lg:justify-end">
          <nav aria-label="주요 화면" className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <Link className="nav-link" href={item.href} key={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
          <nav
            aria-label="회원 및 계정 관리"
            className="flex flex-wrap gap-2 border-slate-200 pt-2 sm:border-l sm:pl-3 sm:pt-0"
          >
            {accountItems.map((item) => (
              <Link className="nav-link" href={item.href} key={item.href}>
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
