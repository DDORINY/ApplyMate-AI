"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { listResumes } from "@/lib/api/resume";

export function ResumeListPanel() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const resumesQuery = useQuery({
    queryKey: ["resumes", page],
    queryFn: () => listResumes({ page, size: 10 }),
    retry: false,
  });

  useEffect(() => {
    if (resumesQuery.error?.message === "로그인이 필요합니다.") {
      router.push("/login");
    }
  }, [resumesQuery.error, router]);

  const data = resumesQuery.data?.data;

  if (resumesQuery.isLoading) {
    return <div className="panel max-w-none">이력서를 불러오는 중입니다.</div>;
  }
  if (resumesQuery.error) {
    return <div className="panel max-w-none text-rose-700">{resumesQuery.error.message}</div>;
  }
  if (!data || data.items.length === 0) {
    return (
      <div className="panel max-w-none">
        <p className="text-slate-700">등록된 이력서가 없습니다.</p>
        <Link className="button-primary mt-4 inline-flex" href="/resumes/new">
          첫 이력서 업로드
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-4">
      {data.items.map((resume) => (
        <article className="panel max-w-none" key={resume.id}>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-sky-700">{resume.is_default ? "기본 이력서" : "이력서"}</p>
              <Link className="mt-1 block text-xl font-semibold text-slate-950 hover:underline" href={`/resumes/${resume.id}`}>
                {resume.title}
              </Link>
              <p className="mt-2 text-sm text-slate-600">{resume.description ?? "설명 없음"}</p>
              <p className="mt-2 text-sm text-slate-500">파일 {resume.files.length}개</p>
            </div>
            <Link className="button-secondary" href={`/resumes/${resume.id}`}>
              상세 보기
            </Link>
          </div>
        </article>
      ))}

      {data.total_pages > 1 ? (
        <div className="flex items-center justify-center gap-3">
          <button className="button-secondary" type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>
            이전
          </button>
          <span className="text-sm text-slate-600">
            {data.page} / {data.total_pages}
          </span>
          <button className="button-secondary" type="button" disabled={page >= data.total_pages} onClick={() => setPage((value) => value + 1)}>
            다음
          </button>
        </div>
      ) : null}
    </div>
  );
}
