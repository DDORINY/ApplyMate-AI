"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getOAuthAccounts, getOAuthProviders, me, startOAuthLink, unlinkOAuthAccount } from "@/lib/api/auth";
import type { OAuthProvider } from "@/types/auth";

const providerLabels: Record<OAuthProvider, string> = {
  GOOGLE: "Google",
  GITHUB: "GitHub",
};

export function OAuthAccountsManager() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [linkingProvider, setLinkingProvider] = useState<OAuthProvider | null>(null);

  const meQuery = useQuery({ queryKey: ["me"], queryFn: me, retry: false });
  const providersQuery = useQuery({ queryKey: ["oauth-providers"], queryFn: getOAuthProviders });
  const accountsQuery = useQuery({
    queryKey: ["oauth-accounts"],
    queryFn: getOAuthAccounts,
    enabled: meQuery.isSuccess,
  });
  const unlinkMutation = useMutation({
    mutationFn: unlinkOAuthAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["oauth-accounts"] }),
  });

  useEffect(() => {
    if (meQuery.isError) {
      router.push("/login");
    }
  }, [meQuery.isError, router]);

  async function handleLink(provider: OAuthProvider) {
    setLinkingProvider(provider);
    try {
      const response = await startOAuthLink(provider, "/settings/accounts");
      window.location.href = response.data.authorization_url;
    } finally {
      setLinkingProvider(null);
    }
  }

  if (meQuery.isLoading || accountsQuery.isLoading || providersQuery.isLoading) {
    return <div className="panel">계정 연결 정보를 확인하고 있습니다.</div>;
  }

  if (meQuery.isError || !meQuery.data) {
    return <div className="panel">로그인이 필요합니다.</div>;
  }

  const accounts = accountsQuery.data?.data.accounts ?? [];
  const linkedProviders = new Set(accounts.map((account) => account.provider));
  const providers = providersQuery.data?.data.providers ?? [];

  return (
    <section className="mx-auto grid w-full max-w-3xl gap-6">
      <div>
        <p className="text-sm font-medium text-sky-700">Account settings</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">소셜 계정 연결</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          Google 또는 GitHub 계정을 연결해 다음 로그인부터 비밀번호 없이 사용할 수 있습니다.
          마지막 로그인 수단은 해제할 수 없습니다.
        </p>
      </div>

      <div className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">연결된 계정</h2>
        {accounts.length === 0 ? (
          <p className="mt-3 text-sm text-slate-600">아직 연결된 소셜 계정이 없습니다.</p>
        ) : (
          <ul className="mt-4 grid gap-3">
            {accounts.map((account) => (
              <li
                className="flex flex-col gap-3 rounded-lg border border-slate-200 p-4 sm:flex-row sm:items-center sm:justify-between"
                key={account.provider}
              >
                <div>
                  <p className="font-semibold text-slate-950">{providerLabels[account.provider]}</p>
                  <p className="mt-1 text-sm text-slate-600">
                    {account.provider_email}
                    {account.provider_username ? ` · ${account.provider_username}` : ""}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    최근 사용: {account.last_login_at ?? "기록 없음"}
                  </p>
                </div>
                <button
                  className="button-secondary"
                  disabled={!account.can_unlink || unlinkMutation.isPending}
                  type="button"
                  onClick={() => unlinkMutation.mutate(account.provider)}
                >
                  {account.can_unlink ? "연결 해제" : "해제 불가"}
                </button>
              </li>
            ))}
          </ul>
        )}
        {unlinkMutation.error ? (
          <p className="mt-3 text-sm text-rose-700">{unlinkMutation.error.message}</p>
        ) : null}
      </div>

      <div className="panel max-w-none">
        <h2 className="text-lg font-semibold text-slate-950">새 소셜 계정 연결</h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {providers.map((item) => (
            <button
              className="button-primary"
              disabled={!item.enabled || linkedProviders.has(item.provider) || linkingProvider === item.provider}
              key={item.provider}
              type="button"
              onClick={() => handleLink(item.provider)}
            >
              {linkedProviders.has(item.provider)
                ? `${providerLabels[item.provider]} 연결됨`
                : `${providerLabels[item.provider]} 연결`}
            </button>
          ))}
        </div>
      </div>

      <Link className="text-sm font-medium text-sky-700" href="/me">
        내 계정으로 돌아가기
      </Link>
    </section>
  );
}
