"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import {
  changePassword,
  getSecurityEvents,
  getSessions,
  me,
  revokeAllSessions,
  revokeOtherSessions,
  revokeSession,
  sendEmailVerification,
  setPassword,
} from "@/lib/api/auth";

const changeSchema = z
  .object({
    current_password: z.string().min(1, "현재 비밀번호를 입력해 주세요."),
    new_password: z.string().min(8, "새 비밀번호는 8자 이상이어야 합니다."),
    new_password_confirm: z.string().min(8, "새 비밀번호 확인을 입력해 주세요."),
  })
  .refine((value) => value.new_password === value.new_password_confirm, {
    path: ["new_password_confirm"],
    message: "비밀번호가 일치하지 않습니다.",
  });

const setSchema = z
  .object({
    new_password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다."),
    new_password_confirm: z.string().min(8, "비밀번호 확인을 입력해 주세요."),
  })
  .refine((value) => value.new_password === value.new_password_confirm, {
    path: ["new_password_confirm"],
    message: "비밀번호가 일치하지 않습니다.",
  });

type ChangePasswordValues = z.infer<typeof changeSchema>;
type SetPasswordValues = z.infer<typeof setSchema>;

export function AccountSecurityPanel() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const meQuery = useQuery({ queryKey: ["me"], queryFn: me, retry: false });
  const sessionsQuery = useQuery({ queryKey: ["auth", "sessions"], queryFn: getSessions });
  const eventsQuery = useQuery({ queryKey: ["auth", "events"], queryFn: getSecurityEvents });

  const changeForm = useForm<ChangePasswordValues>({
    resolver: zodResolver(changeSchema),
    defaultValues: { current_password: "", new_password: "", new_password_confirm: "" },
  });
  const setForm = useForm<SetPasswordValues>({
    resolver: zodResolver(setSchema),
    defaultValues: { new_password: "", new_password_confirm: "" },
  });

  useEffect(() => {
    if (meQuery.isError) {
      router.push("/login");
    }
  }, [meQuery.isError, router]);

  const refreshSecurityData = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["me"] }),
      queryClient.invalidateQueries({ queryKey: ["auth", "sessions"] }),
      queryClient.invalidateQueries({ queryKey: ["auth", "events"] }),
    ]);
  };

  const emailMutation = useMutation({
    mutationFn: sendEmailVerification,
    onSuccess: refreshSecurityData,
  });
  const changeMutation = useMutation({
    mutationFn: changePassword,
    onSuccess: async () => {
      changeForm.reset();
      await refreshSecurityData();
    },
  });
  const setMutation = useMutation({
    mutationFn: setPassword,
    onSuccess: async () => {
      setForm.reset();
      await refreshSecurityData();
    },
  });
  const revokeMutation = useMutation({
    mutationFn: revokeSession,
    onSuccess: refreshSecurityData,
  });
  const revokeOthersMutation = useMutation({
    mutationFn: revokeOtherSessions,
    onSuccess: refreshSecurityData,
  });
  const revokeAllMutation = useMutation({
    mutationFn: revokeAllSessions,
    onSuccess: () => router.push("/login"),
  });

  if (meQuery.isLoading) {
    return <div className="panel">계정 정보를 불러오고 있습니다.</div>;
  }
  if (meQuery.isError || !meQuery.data) {
    return <div className="panel">로그인이 필요합니다.</div>;
  }

  const user = meQuery.data.data;
  const sessions = sessionsQuery.data?.data.sessions ?? [];
  const events = eventsQuery.data?.data.events ?? [];

  return (
    <div className="grid gap-6">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">이메일 인증</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {user.email_verified
                ? "이메일 인증이 완료된 계정입니다."
                : "계정 복구와 보안 알림을 위해 이메일 인증을 완료해 주세요."}
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">
            {user.email_verified ? "인증 완료" : "미인증"}
          </span>
        </div>
        {!user.email_verified ? (
          <div className="mt-4 grid gap-2">
            <button
              className="button-primary w-fit"
              type="button"
              disabled={emailMutation.isPending}
              onClick={() => emailMutation.mutate()}
            >
              {emailMutation.isPending ? "발송 중..." : "인증 메일 다시 보내기"}
            </button>
            {emailMutation.isSuccess ? (
              <p className="text-sm text-emerald-700">인증 메일을 발송했습니다.</p>
            ) : null}
            {emailMutation.error ? (
              <p className="text-sm text-rose-700">{emailMutation.error.message}</p>
            ) : null}
          </div>
        ) : null}
      </section>

      <section className="panel max-w-none">
        <h2 className="text-xl font-semibold text-slate-950">
          {user.has_password ? "비밀번호 변경" : "비밀번호 설정"}
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {user.has_password
            ? "비밀번호를 변경하면 현재 세션을 제외한 다른 세션이 로그아웃됩니다."
            : "소셜 로그인 계정에 비밀번호를 설정하면 이메일/비밀번호 로그인도 사용할 수 있습니다."}
        </p>
        {user.has_password ? (
          <form
            className="mt-4 grid gap-3"
            onSubmit={changeForm.handleSubmit((values) => changeMutation.mutate(values))}
          >
            <Field label="현재 비밀번호" error={changeForm.formState.errors.current_password?.message}>
              <input
                className="input"
                type="password"
                {...changeForm.register("current_password")}
                autoComplete="current-password"
              />
            </Field>
            <Field label="새 비밀번호" error={changeForm.formState.errors.new_password?.message}>
              <input
                className="input"
                type="password"
                {...changeForm.register("new_password")}
                autoComplete="new-password"
              />
            </Field>
            <Field
              label="새 비밀번호 확인"
              error={changeForm.formState.errors.new_password_confirm?.message}
            >
              <input
                className="input"
                type="password"
                {...changeForm.register("new_password_confirm")}
                autoComplete="new-password"
              />
            </Field>
            <MutationStatus
              success={changeMutation.isSuccess ? "비밀번호가 변경되었습니다." : null}
              error={changeMutation.error?.message}
            />
            <button className="button-primary w-fit" type="submit" disabled={changeMutation.isPending}>
              {changeMutation.isPending ? "변경 중..." : "비밀번호 변경"}
            </button>
          </form>
        ) : (
          <form
            className="mt-4 grid gap-3"
            onSubmit={setForm.handleSubmit((values) => setMutation.mutate(values))}
          >
            <Field label="새 비밀번호" error={setForm.formState.errors.new_password?.message}>
              <input
                className="input"
                type="password"
                {...setForm.register("new_password")}
                autoComplete="new-password"
              />
            </Field>
            <Field
              label="새 비밀번호 확인"
              error={setForm.formState.errors.new_password_confirm?.message}
            >
              <input
                className="input"
                type="password"
                {...setForm.register("new_password_confirm")}
                autoComplete="new-password"
              />
            </Field>
            <MutationStatus
              success={setMutation.isSuccess ? "비밀번호가 설정되었습니다." : null}
              error={setMutation.error?.message}
            />
            <button className="button-primary w-fit" type="submit" disabled={setMutation.isPending}>
              {setMutation.isPending ? "설정 중..." : "비밀번호 설정"}
            </button>
          </form>
        )}
      </section>

      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">로그인 세션</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              현재 활성화된 기기별 로그인 세션을 확인하고 필요하면 로그아웃할 수 있습니다.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              className="button-secondary"
              type="button"
              disabled={revokeOthersMutation.isPending}
              onClick={() => revokeOthersMutation.mutate()}
            >
              다른 세션 로그아웃
            </button>
            <button
              className="button-secondary"
              type="button"
              disabled={revokeAllMutation.isPending}
              onClick={() => revokeAllMutation.mutate()}
            >
              모든 세션 로그아웃
            </button>
          </div>
        </div>
        <div className="mt-4 grid gap-3">
          {sessionsQuery.isLoading ? <p className="text-sm text-slate-600">세션을 불러오는 중입니다.</p> : null}
          {sessions.map((session) => (
            <div
              className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-700"
              key={session.session_id}
            >
              <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="font-semibold text-slate-950">
                    {session.device_name ?? "알 수 없는 기기"}
                    {session.current ? " · 현재 세션" : ""}
                  </p>
                  <p className="mt-1 text-slate-500">
                    최근 사용: {session.last_used_at ?? session.created_at}
                  </p>
                  <p className="mt-1 break-all text-slate-500">{session.user_agent ?? "User-Agent 없음"}</p>
                </div>
                {!session.current ? (
                  <button
                    className="button-secondary"
                    type="button"
                    disabled={revokeMutation.isPending}
                    onClick={() => revokeMutation.mutate(session.session_id)}
                  >
                    로그아웃
                  </button>
                ) : null}
              </div>
            </div>
          ))}
          {!sessionsQuery.isLoading && sessions.length === 0 ? (
            <p className="text-sm text-slate-600">활성 세션이 없습니다.</p>
          ) : null}
        </div>
      </section>

      <section className="panel max-w-none">
        <h2 className="text-xl font-semibold text-slate-950">최근 보안 이벤트</h2>
        <div className="mt-4 grid gap-2">
          {eventsQuery.isLoading ? (
            <p className="text-sm text-slate-600">보안 이벤트를 불러오는 중입니다.</p>
          ) : null}
          {events.map((event) => (
            <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700" key={event.id}>
              <p className="font-semibold text-slate-950">{event.event_type}</p>
              <p className="mt-1 text-slate-500">{event.created_at}</p>
            </div>
          ))}
          {!eventsQuery.isLoading && events.length === 0 ? (
            <p className="text-sm text-slate-600">아직 기록된 보안 이벤트가 없습니다.</p>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function MutationStatus({ success, error }: { success: string | null; error?: string }) {
  if (success) {
    return <p className="text-sm text-emerald-700">{success}</p>;
  }
  if (error) {
    return <p className="text-sm text-rose-700">{error}</p>;
  }
  return null;
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
