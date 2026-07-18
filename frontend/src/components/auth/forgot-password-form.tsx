"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { forgotPassword } from "@/lib/api/auth";

const schema = z.object({
  email: z.string().email("이메일 형식이 올바르지 않습니다."),
});

type ForgotPasswordValues = z.infer<typeof schema>;

export function ForgotPasswordForm() {
  const form = useForm<ForgotPasswordValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  });
  const mutation = useMutation({
    mutationFn: (values: ForgotPasswordValues) => forgotPassword(values.email),
  });

  return (
    <form className="grid gap-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <Field label="가입 이메일" error={form.formState.errors.email?.message}>
        <input className="input" {...form.register("email")} autoComplete="email" />
      </Field>
      {mutation.isSuccess ? (
        <p className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-800">
          계정이 존재하면 비밀번호 재설정 안내 메일을 발송합니다.
        </p>
      ) : null}
      {mutation.error ? <p className="text-sm text-rose-700">{mutation.error.message}</p> : null}
      <button className="button-primary" type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "요청 중..." : "재설정 메일 받기"}
      </button>
      <Link className="text-sm font-medium text-slate-700 underline-offset-4 hover:underline" href="/login">
        로그인으로 돌아가기
      </Link>
    </form>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      {children}
      {error ? <span className="text-sm font-normal text-rose-700">{error}</span> : null}
    </label>
  );
}
