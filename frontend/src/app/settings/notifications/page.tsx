import { NotificationSettingsPanel } from "@/components/notifications/notification-settings-panel";

export default function NotificationSettingsPage() {
  return (
    <main className="mx-auto grid w-full max-w-5xl gap-6 px-5 py-10 sm:px-8">
      <NotificationSettingsPanel />
    </main>
  );
}
