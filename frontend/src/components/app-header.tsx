import Link from "next/link";

const navItems = [
  { href: "/", label: "홈" },
  { href: "/signup", label: "회원가입" },
  { href: "/login", label: "로그인" },
  { href: "/me", label: "내 계정" },
  { href: "/profile", label: "프로필" },
];

export function AppHeader() {
  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <Link className="text-lg font-semibold text-slate-950" href="/">
          ApplyMate AI
        </Link>
        <nav aria-label="주요 화면" className="flex flex-wrap gap-2">
          {navItems.map((item) => (
            <Link className="nav-link" href={item.href} key={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
