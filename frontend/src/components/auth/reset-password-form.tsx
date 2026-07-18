"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { resetPassword } from "@/lib/api/auth";

const schema = z
  .object({
    new_password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다."),
    new_password_confirm: z.string().min(8, "비밀번호 확인을 입력해 주세요."),
  })
  .refine((value) => value.new_password === value.new_password_confirm, {
    path: ["new_password_confirm"],
    message: "비밀번호가 일치하지 않습니다.",
  });

type ResetPasswordValues = z.infer<typeof schema>;

export function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const form = useForm<ResetPasswordValues>({
    resolver: zodResolver(schema),
    defaultValues: { new_password: "", new_password_confirm: "" },
  });
  const mutation = useMutation({
    mutationFn: (values: ResetPasswordValues) =>
      resetPassword({
        token,
        new_password: values.new_password,
        new_password_confirm: values.new_password_confirm,
      }),
  });

  if (!token) {
    return (
      <div className="grid gap-4">
        <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-800">
          비밀번호 재설정 토큰이 없습니다. 메일의 링크로 다시 접근해 주세요.
        </p>
        <Link className="button-secondary text-center" href="/forgot-password">
          재설정 메일 다시 받기
        </Link>
      </div>
    );
  }

  return (
    <form className="grid gap-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <Field label="새 비밀번호" error={form.formState.errors.new_password?.message}>
        <input
          className="input"
          type="password"
          {...form.register("new_password")}
          autoComplete="new-password"
        />
      </Field>
      <Field label="새 비밀번호 확인" error={form.formState.errors.new_password_confirm?.message}>
        <input
          className="input"
          type="password"
          {...form.register("new_password_confirm")}
          autoComplete="new-password"
        />
      </Field>
      {mutation.isSuccess ? (
        <p className="rounded-2xl bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-800">
          비밀번호가 재설정되었습니다. 새 비밀번호로 다시 로그인해 주세요.
        </p>
      ) : null}
      {mutation.error ? <p className="text-sm text-rose-700">{mutation.error.message}</p> : null}
      <button className="button-primary" type="submit" disabled={mutation.isPending || mutation.isSuccess}>
        {mutation.isPending ? "변경 중..." : "비밀번호 재설정"}
      </button>
      {mutation.isSuccess ? (
        <Link className="button-secondary text-center" href="/login">
          로그인하기
        </Link>
      ) : null}
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
