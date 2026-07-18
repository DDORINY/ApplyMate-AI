"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { login } from "@/lib/api/auth";

const schema = z.object({
  email: z.string().email("이메일 형식이 올바르지 않습니다."),
  password: z.string().min(1, "비밀번호를 입력해 주세요."),
});

type LoginFormValues = z.infer<typeof schema>;

export function LoginForm() {
  const router = useRouter();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });
  const mutation = useMutation({
    mutationFn: login,
    onSuccess: () => router.push("/me"),
  });

  return (
    <form className="grid gap-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <Field label="이메일" error={form.formState.errors.email?.message}>
        <input className="input" {...form.register("email")} autoComplete="email" />
      </Field>
      <Field label="비밀번호" error={form.formState.errors.password?.message}>
        <input
          className="input"
          type="password"
          {...form.register("password")}
          autoComplete="current-password"
        />
      </Field>
      {mutation.error ? <p className="text-sm text-rose-700">{mutation.error.message}</p> : null}
      <button className="button-primary" type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "로그인 중..." : "로그인"}
      </button>
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
