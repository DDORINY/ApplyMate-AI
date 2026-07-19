"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { createResume, uploadResumeFile } from "@/lib/api/resume";

const schema = z.object({
  title: z.string().min(1, "이력서 제목을 입력해 주세요."),
  description: z.string().optional(),
  is_default: z.boolean(),
  file: z.custom<FileList>().refine((files) => files?.length === 1, "PDF 또는 DOCX 파일을 선택해 주세요."),
});

type FormValues = z.infer<typeof schema>;

export function ResumeCreatePanel() {
  const router = useRouter();
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { title: "", description: "", is_default: false },
  });

  const mutation = useMutation({
    mutationFn: async (values: FormValues) => {
      const resume = await createResume({
        title: values.title,
        description: values.description || null,
        is_default: values.is_default,
      });
      await uploadResumeFile(resume.data.id, values.file[0]);
      return resume;
    },
    onSuccess: (response) => router.push(`/resumes/${response.data.id}`),
  });

  return (
    <form className="panel grid max-w-none gap-5" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <label className="grid gap-2 text-sm font-medium text-slate-700">
        이력서 제목
        <input className="input" placeholder="예: 백엔드 개발자 이력서" {...form.register("title")} />
        {form.formState.errors.title ? <span className="text-rose-700">{form.formState.errors.title.message}</span> : null}
      </label>
      <label className="grid gap-2 text-sm font-medium text-slate-700">
        설명
        <textarea className="input min-h-28" placeholder="이력서 용도나 버전을 적어 두세요." {...form.register("description")} />
      </label>
      <label className="grid gap-2 text-sm font-medium text-slate-700">
        파일
        <input
          className="input"
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          {...form.register("file")}
        />
        {form.formState.errors.file ? <span className="text-rose-700">{form.formState.errors.file.message}</span> : null}
      </label>
      <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
        <input type="checkbox" {...form.register("is_default")} />
        기본 이력서로 설정
      </label>
      <p className="rounded-2xl bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
        PDF와 DOCX만 업로드할 수 있습니다. 원본 파일명은 표시용으로만 저장되고, 내부 저장명은 UUID로 분리됩니다.
      </p>
      {mutation.error ? <p className="text-sm text-rose-700">{mutation.error.message}</p> : null}
      <button className="button-primary w-fit" type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "업로드 중..." : "이력서 업로드"}
      </button>
    </form>
  );
}
