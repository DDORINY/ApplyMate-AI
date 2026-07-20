import { NotificationListPanel } from "@/components/notifications/notification-list-panel";

export default function NotificationsPage() {
  return (
    <main className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-10 sm:px-8">
      <NotificationListPanel />
    </main>
  );
}
