"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect } from "react";

import { verifyEmail } from "@/lib/api/auth";

export function VerifyEmailPanel() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const mutation = useMutation({
    mutationFn: verifyEmail,
  });

  useEffect(() => {
    if (token && mutation.isIdle) {
      mutation.mutate(token);
    }
  }, [mutation, token]);

  if (!token) {
    return (
      <div className="panel grid gap-4">
        <p className="text-sm leading-6 text-rose-700">
          이메일 인증 토큰이 없습니다. 메일의 링크로 다시 접근하거나 보안 설정에서 인증 메일을
          다시 요청해 주세요.
        </p>
        <Link className="button-secondary text-center" href="/settings/security">
          보안 설정으로 이동
        </Link>
      </div>
    );
  }

  return (
    <div className="panel grid gap-4">
      {mutation.isPending ? (
        <p className="text-sm text-slate-600">이메일 인증을 확인하고 있습니다.</p>
      ) : null}
      {mutation.isSuccess ? (
        <>
          <p className="text-sm leading-6 text-emerald-800">이메일 인증이 완료되었습니다.</p>
          <Link className="button-primary text-center" href="/me">
            내 계정으로 이동
          </Link>
        </>
      ) : null}
      {mutation.error ? (
        <>
          <p className="text-sm leading-6 text-rose-700">{mutation.error.message}</p>
          <Link className="button-secondary text-center" href="/settings/security">
            인증 메일 다시 요청
          </Link>
        </>
      ) : null}
    </div>
  );
}
