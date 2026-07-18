"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { logout, me } from "@/lib/api/auth";

export function ProtectedUserPanel() {
  const router = useRouter();
  const query = useQuery({
    queryKey: ["me"],
    queryFn: me,
    retry: false,
  });
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => router.push("/login"),
  });

  useEffect(() => {
    if (query.isError) {
      router.push("/login");
    }
  }, [query.isError, router]);

  if (query.isLoading) {
    return <div className="panel">로그인 상태를 확인하고 있습니다.</div>;
  }

  if (query.isError || !query.data) {
    return <div className="panel">로그인이 필요합니다.</div>;
  }

  const user = query.data.data;

  return (
    <div className="panel grid gap-4">
      <div>
        <p className="text-sm text-slate-500">현재 사용자</p>
        <h2 className="mt-1 text-2xl font-semibold text-slate-950">{user.name}</h2>
        <p className="mt-1 text-slate-600">{user.email}</p>
      </div>
      <dl className="grid gap-3 text-sm text-slate-700">
        <div className="flex justify-between gap-4">
          <dt>상태</dt>
          <dd className="font-medium">{user.status}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt>이메일 인증</dt>
          <dd className="font-medium">{user.email_verified ? "완료" : "미인증"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt>비밀번호 로그인</dt>
          <dd className="font-medium">{user.has_password ? "설정됨" : "미설정"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt>최근 로그인</dt>
          <dd className="font-medium">{user.last_login_at ?? "기록 없음"}</dd>
        </div>
      </dl>
      <div className="flex flex-wrap gap-2">
        <Link className="button-primary" href="/profile">
          프로필 관리
        </Link>
        <Link className="button-secondary" href="/settings/accounts">
          계정 연결
        </Link>
        <Link className="button-secondary" href="/settings/security">
          보안 설정
        </Link>
        <button
          className="button-secondary"
          disabled={logoutMutation.isPending}
          type="button"
          onClick={() => logoutMutation.mutate()}
        >
          {logoutMutation.isPending ? "로그아웃 중..." : "로그아웃"}
        </button>
      </div>
    </div>
  );
}
