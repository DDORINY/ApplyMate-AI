"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getOAuthProviders, startOAuth } from "@/lib/api/auth";
import type { OAuthProvider } from "@/types/auth";

const providerLabels: Record<OAuthProvider, string> = {
  GOOGLE: "Google",
  GITHUB: "GitHub",
};

export function OAuthButtons({ redirectPath = "/me" }: { redirectPath?: string }) {
  const [selectedProvider, setSelectedProvider] = useState<OAuthProvider | null>(null);
  const providersQuery = useQuery({
    queryKey: ["oauth-providers"],
    queryFn: getOAuthProviders,
  });

  async function handleStart(provider: OAuthProvider) {
    setSelectedProvider(provider);
    try {
      const response = await startOAuth(provider, redirectPath);
      window.location.href = response.data.authorization_url;
    } finally {
      setSelectedProvider(null);
    }
  }

  if (providersQuery.isLoading) {
    return <p className="text-sm text-slate-500">소셜 로그인 제공자를 확인하고 있습니다.</p>;
  }

  if (providersQuery.isError || !providersQuery.data) {
    return <p className="text-sm text-rose-700">소셜 로그인 정보를 불러오지 못했습니다.</p>;
  }

  return (
    <div className="grid gap-2">
      {providersQuery.data.data.providers.map((item) => (
        <button
          className="button-secondary w-full"
          disabled={!item.enabled || selectedProvider === item.provider}
          key={item.provider}
          type="button"
          onClick={() => handleStart(item.provider)}
        >
          {item.enabled
            ? `${providerLabels[item.provider]}로 계속하기`
            : `${providerLabels[item.provider]} 설정 필요`}
        </button>
      ))}
    </div>
  );
}
