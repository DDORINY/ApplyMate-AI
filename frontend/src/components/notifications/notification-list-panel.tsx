"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  archiveNotification,
  dismissNotification,
  listNotifications,
  markNotificationRead,
  readAllNotifications,
  runDueNotifications,
} from "@/lib/api/notification";
import type { NotificationStatus } from "@/types/notification";
import { notificationEventLabels, notificationPriorityLabels, notificationStatusLabels } from "./notification-labels";

export function NotificationListPanel() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<NotificationStatus | "">("");
  const notificationsQuery = useQuery({
    queryKey: ["notifications", status],
    queryFn: () => listNotifications({ status }),
    retry: false,
  });

  useEffect(() => {
    if (notificationsQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [notificationsQuery.error, router]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["notifications"] });
    queryClient.invalidateQueries({ queryKey: ["notification-unread-count"] });
  };
  const readMutation = useMutation({ mutationFn: markNotificationRead, onSuccess: invalidate });
  const dismissMutation = useMutation({ mutationFn: dismissNotification, onSuccess: invalidate });
  const archiveMutation = useMutation({ mutationFn: archiveNotification, onSuccess: invalidate });
  const readAllMutation = useMutation({ mutationFn: readAllNotifications, onSuccess: invalidate });
  const runDueMutation = useMutation({ mutationFn: runDueNotifications, onSuccess: invalidate });

  const data = notificationsQuery.data?.data;

  return (
    <div className="grid gap-5">
      <section className="panel max-w-none">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold text-violet-600">Notification Center</p>
            <h1 className="mt-1 text-2xl font-bold text-slate-950">알림</h1>
            <p className="mt-2 text-sm text-slate-600">일정, 추천, 메일 후보, 문서 개선 결과를 한곳에서 확인합니다.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="button-secondary" type="button" disabled={readAllMutation.isPending} onClick={() => readAllMutation.mutate()}>
              모두 읽음
            </button>
            <button className="button-secondary" type="button" disabled={runDueMutation.isPending} onClick={() => runDueMutation.mutate()}>
              알림 처리 실행
            </button>
            <Link className="button-primary" href="/settings/notifications">
              알림 설정
            </Link>
          </div>
        </div>
        <label className="mt-5 grid max-w-xs gap-2 text-sm font-medium text-slate-700">
          상태 필터
          <select className="input" value={status} onChange={(event) => setStatus(event.target.value as NotificationStatus | "")}>
            <option value="">전체</option>
            {Object.entries(notificationStatusLabels).map(([value, label]) => (
              <option value={value} key={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </section>

      {notificationsQuery.isLoading ? <div className="panel max-w-none">알림을 불러오는 중입니다.</div> : null}
      {notificationsQuery.error ? <div className="panel max-w-none text-rose-700">{notificationsQuery.error.message}</div> : null}
      {data?.items.length === 0 ? <div className="panel max-w-none text-slate-600">표시할 알림이 없습니다.</div> : null}

      <div className="grid gap-3">
        {data?.items.map((notification) => (
          <article className="panel max-w-none" key={notification.id}>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p className="text-xs font-bold text-violet-600">
                  {notificationEventLabels[notification.event_type]} · {notificationPriorityLabels[notification.priority]} ·{" "}
                  {notificationStatusLabels[notification.status]}
                </p>
                <h2 className="mt-1 text-lg font-semibold text-slate-950">{notification.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{notification.message}</p>
                {notification.source_url ? (
                  <Link className="mt-3 inline-flex text-sm font-semibold text-violet-700 hover:underline" href={notification.source_url}>
                    연결 화면 열기
                  </Link>
                ) : null}
              </div>
              <div className="flex shrink-0 flex-wrap gap-2">
                <button className="button-secondary" type="button" disabled={readMutation.isPending} onClick={() => readMutation.mutate(notification.id)}>
                  읽음
                </button>
                <button className="button-secondary" type="button" disabled={dismissMutation.isPending} onClick={() => dismissMutation.mutate(notification.id)}>
                  해제
                </button>
                <button className="button-secondary" type="button" disabled={archiveMutation.isPending} onClick={() => archiveMutation.mutate(notification.id)}>
                  보관
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
