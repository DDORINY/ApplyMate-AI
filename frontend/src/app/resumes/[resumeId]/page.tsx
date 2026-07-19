import { AppHeader } from "@/components/app-header";
import { ResumeDetailPanel } from "@/components/resumes/resume-detail-panel";

type ResumeDetailPageProps = {
  params: Promise<{ resumeId: string }>;
};

export default async function ResumeDetailPage({ params }: ResumeDetailPageProps) {
  const { resumeId } = await params;

  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto w-full max-w-6xl">
          <ResumeDetailPanel resumeId={Number(resumeId)} />
        </section>
      </main>
    </>
  );
}
