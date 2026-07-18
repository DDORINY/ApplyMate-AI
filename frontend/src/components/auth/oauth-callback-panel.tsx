"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";

import { exchangeOAuthTicket } from "@/lib/api/auth";

const errorMessages: Record<string, string> = {
  OAUTH_ACCOUNT_LINK_REQUIRED:
    "같은 이메일의 기존 계정이 있습니다. 먼저 이메일로 로그인한 뒤 계정 연결 화면에서 소셜 계정을 연결해 주세요.",
  OAUTH_VERIFIED_EMAIL_REQUIRED: "검증된 이메일을 제공하는 소셜 계정만 사용할 수 있습니다.",
  OAUTH_PROVIDER_DISABLED: "현재 사용할 수 없는 소셜 로그인 제공자입니다.",
  OAUTH_STATE_INVALID: "소셜 로그인 요청이 유효하지 않습니다. 다시 시도해 주세요.",
  OAUTH_STATE_EXPIRED: "소셜 로그인 요청이 만료되었습니다. 다시 시도해 주세요.",
};

export function OAuthCallbackPanel() {
  const router = useRouter();
  const params = useSearchParams();
  const ticket = params.get("ticket");
  const error = params.get("error");
  const redirectPath = params.get("redirect_path") || "/me";

  const mutation = useMutation({
    mutationFn: exchangeOAuthTicket,
    onSuccess: (response) => {
      router.replace(response.data.redirect_path || redirectPath);
    },
  });

  useEffect(() => {
    if (ticket && !mutation.isPending && !mutation.isSuccess) {
      mutation.mutate(ticket);
    }
  }, [mutation, ticket]);

  if (error) {
    return (
      <div className="panel grid gap-4">
        <h1 className="text-2xl font-semibold text-slate-950">소셜 로그인 실패</h1>
        <p className="text-sm leading-6 text-rose-700">
          {errorMessages[error] ?? "소셜 로그인 처리 중 오류가 발생했습니다."}
        </p>
        <Link className="button-primary text-center" href="/login">
          로그인으로 돌아가기
        </Link>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="panel grid gap-4">
        <h1 className="text-2xl font-semibold text-slate-950">소셜 로그인 확인 필요</h1>
        <p className="text-sm leading-6 text-slate-600">로그인 ticket이 없습니다. 다시 시도해 주세요.</p>
        <Link className="button-primary text-center" href="/login">
          로그인으로 돌아가기
        </Link>
      </div>
    );
  }

  return (
    <div className="panel grid gap-4">
      <h1 className="text-2xl font-semibold text-slate-950">소셜 로그인 처리 중</h1>
      <p className="text-sm leading-6 text-slate-600">
        안전하게 로그인 정보를 교환하고 있습니다. 잠시만 기다려 주세요.
      </p>
      {mutation.error ? <p className="text-sm text-rose-700">{mutation.error.message}</p> : null}
    </div>
  );
}
