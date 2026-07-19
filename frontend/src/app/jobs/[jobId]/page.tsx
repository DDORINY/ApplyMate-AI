import { AppHeader } from "@/components/app-header";
import { JobDetailPanel } from "@/components/jobs/job-detail-panel";

type JobDetailPageProps = {
  params: Promise<{ jobId: string }>;
};

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { jobId } = await params;

  return (
    <>
      <AppHeader />
      <main className="min-h-screen px-5 py-8 sm:px-8">
        <section className="mx-auto w-full max-w-6xl">
          <JobDetailPanel jobId={Number(jobId)} />
        </section>
      </main>
    </>
  );
}
