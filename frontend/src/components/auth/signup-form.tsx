"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { signup } from "@/lib/api/auth";

const schema = z
  .object({
    name: z.string().min(1, "이름을 입력해 주세요."),
    email: z.string().email("이메일 형식이 올바르지 않습니다."),
    password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다."),
    confirmPassword: z.string(),
  })
  .refine((value) => value.password === value.confirmPassword, {
    path: ["confirmPassword"],
    message: "비밀번호가 일치하지 않습니다.",
  });

type SignupFormValues = z.infer<typeof schema>;

export function SignupForm() {
  const router = useRouter();
  const form = useForm<SignupFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "", email: "", password: "", confirmPassword: "" },
  });
  const mutation = useMutation({
    mutationFn: signup,
    onSuccess: () => router.push("/login?joined=1"),
  });

  return (
    <form
      className="grid gap-4"
      onSubmit={form.handleSubmit((values) =>
        mutation.mutate({
          name: values.name,
          email: values.email,
          password: values.password,
        }),
      )}
    >
      <Field label="이름" error={form.formState.errors.name?.message}>
        <input className="input" {...form.register("name")} autoComplete="name" />
      </Field>
      <Field label="이메일" error={form.formState.errors.email?.message}>
        <input className="input" {...form.register("email")} autoComplete="email" />
      </Field>
      <Field label="비밀번호" error={form.formState.errors.password?.message}>
        <input
          className="input"
          type="password"
          {...form.register("password")}
          autoComplete="new-password"
        />
      </Field>
      <Field label="비밀번호 확인" error={form.formState.errors.confirmPassword?.message}>
        <input
          className="input"
          type="password"
          {...form.register("confirmPassword")}
          autoComplete="new-password"
        />
      </Field>
      <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
        가입 후 입력한 이메일로 인증 링크가 발송됩니다. 인증을 완료하면 계정 보안 화면에서
        세션과 비밀번호를 관리할 수 있어요.
      </p>
      {mutation.error ? <p className="text-sm text-rose-700">{mutation.error.message}</p> : null}
      <button className="button-primary" type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "가입 중..." : "회원가입"}
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
