import { AppHeader } from "@/components/app-header";
import { ProfileManager } from "@/components/profile/profile-manager";

export default function ProfilePage() {
  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <ProfileManager />
      </main>
    </>
  );
}
