"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { logout, me } from "@/lib/api/auth";
import { profileApi } from "@/lib/api/profile";
import type {
  CareerProfile,
  ExcludedCondition,
  Experience,
  JobPreference,
  PortfolioLink,
  Project,
  UserSkill,
} from "@/types/profile";

const profileSchema = z.object({
  display_name: z.string().min(1, "표시 이름을 입력해 주세요."),
  headline: z.string().optional(),
  career_level: z.enum(["ENTRY", "JUNIOR", "MID", "SENIOR", "CAREER_CHANGE"]),
  years_of_experience: z.number().min(0).max(60),
  desired_job_title: z.string().min(1, "희망 직무를 입력해 주세요."),
  introduction: z.string().optional(),
});

const skillSchema = z.object({
  name: z.string().min(1, "기술명을 입력해 주세요."),
  proficiency_level: z.enum(["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]),
  years_of_experience: z.number().min(0).max(60),
  is_primary: z.boolean(),
});

const experienceSchema = z
  .object({
    company_name: z.string().min(1, "회사명을 입력해 주세요."),
    position: z.string().min(1, "직무를 입력해 주세요."),
    employment_type: z.enum([
      "FULL_TIME",
      "CONTRACT",
      "INTERN",
      "FREELANCE",
      "PART_TIME",
      "SELF_EMPLOYED",
      "OTHER",
    ]),
    start_date: z.string().min(1, "시작일을 입력해 주세요."),
    end_date: z.string().optional(),
    is_current: z.boolean(),
    description: z.string().optional(),
    achievements: z.string().optional(),
  })
  .refine((value) => value.is_current || Boolean(value.end_date), {
    path: ["end_date"],
    message: "종료된 경력은 종료일이 필요합니다.",
  });

const projectSchema = z.object({
  name: z.string().min(1, "프로젝트명을 입력해 주세요."),
  summary: z.string().optional(),
  role: z.string().optional(),
  start_date: z.string().min(1, "시작일을 입력해 주세요."),
  end_date: z.string().optional(),
  is_ongoing: z.boolean(),
  repository_url: z.string().url().optional().or(z.literal("")),
  service_url: z.string().url().optional().or(z.literal("")),
  skill_names: z.string().optional(),
});

const preferenceSchema = z.object({
  preferred_locations: z.string().optional(),
  desired_roles: z.string().optional(),
  priority_keywords: z.string().optional(),
  remote_preference: z.enum(["ONSITE", "HYBRID", "REMOTE", "ANY"]),
  minimum_salary: z.number().min(0).optional(),
});

const exclusionSchema = z.object({
  condition_type: z.enum([
    "EMPLOYMENT_TYPE",
    "LOCATION",
    "COMPANY_SIZE",
    "REQUIRED_SKILL",
    "EXCLUDED_KEYWORD",
    "MINIMUM_EXPERIENCE",
    "EDUCATION_REQUIREMENT",
    "OTHER",
  ]),
  value: z.string().min(1, "제외 조건 값을 입력해 주세요."),
  reason: z.string().optional(),
  is_active: z.boolean(),
});

const portfolioSchema = z.object({
  link_type: z.enum(["GITHUB", "NOTION", "PORTFOLIO", "BLOG", "LINKEDIN", "OTHER"]),
  title: z.string().min(1, "제목을 입력해 주세요."),
  url: z.string().url("http 또는 https URL을 입력해 주세요."),
  is_primary: z.boolean(),
  display_order: z.number().min(0),
});

export function ProfileManager() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const userQuery = useQuery({ queryKey: ["me"], queryFn: me, retry: false });
  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: profileApi.getProfile,
    retry: false,
  });
  const skillsQuery = useQuery({ queryKey: ["profile", "skills"], queryFn: profileApi.listSkills });
  const experiencesQuery = useQuery({
    queryKey: ["profile", "experiences"],
    queryFn: profileApi.listExperiences,
  });
  const projectsQuery = useQuery({
    queryKey: ["profile", "projects"],
    queryFn: profileApi.listProjects,
  });
  const preferencesQuery = useQuery({
    queryKey: ["profile", "preferences"],
    queryFn: profileApi.getPreferences,
    retry: false,
  });
  const exclusionsQuery = useQuery({
    queryKey: ["profile", "exclusions"],
    queryFn: profileApi.listExclusions,
  });
  const linksQuery = useQuery({
    queryKey: ["profile", "links"],
    queryFn: profileApi.listPortfolioLinks,
  });

  useEffect(() => {
    if (userQuery.isError) {
      router.push("/login");
    }
  }, [router, userQuery.isError]);

  const invalidate = (key: string[]) => queryClient.invalidateQueries({ queryKey: key });
  const logoutMutation = useMutation({ mutationFn: logout, onSuccess: () => router.push("/login") });

  if (userQuery.isLoading) {
    return <div className="panel mx-auto max-w-3xl">로그인 상태를 확인하고 있습니다.</div>;
  }

  if (userQuery.isError) {
    return <div className="panel mx-auto max-w-3xl">로그인이 필요합니다.</div>;
  }

  return (
    <section className="mx-auto grid w-full max-w-6xl gap-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-sky-700">ApplyMate AI v0.1.2</p>
          <h1 className="mt-2 text-3xl font-semibold text-slate-950">커리어 프로필</h1>
          <p className="mt-2 text-slate-600">
            지원 전략의 기준이 되는 경력, 기술, 프로젝트, 선호 조건을 관리합니다.
          </p>
        </div>
        <div className="flex gap-2">
          <Link className="button-secondary" href="/me">
            내 계정
          </Link>
          <button className="button-secondary" onClick={() => logoutMutation.mutate()} type="button">
            로그아웃
          </button>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <ProfileForm
          initial={profileQuery.data?.data}
          onSaved={() => void invalidate(["profile"])}
        />
        <SkillSection
          items={skillsQuery.data?.data ?? []}
          onChanged={() => void invalidate(["profile", "skills"])}
        />
        <ExperienceSection
          items={experiencesQuery.data?.data ?? []}
          onChanged={() => void invalidate(["profile", "experiences"])}
        />
        <ProjectSection
          items={projectsQuery.data?.data ?? []}
          onChanged={() => void invalidate(["profile", "projects"])}
        />
        <PreferenceSection
          initial={preferencesQuery.data?.data}
          onChanged={() => void invalidate(["profile", "preferences"])}
        />
        <ExclusionSection
          items={exclusionsQuery.data?.data ?? []}
          onChanged={() => void invalidate(["profile", "exclusions"])}
        />
        <PortfolioSection
          items={linksQuery.data?.data ?? []}
          onChanged={() => void invalidate(["profile", "links"])}
        />
      </div>
    </section>
  );
}

function splitList(value?: string) {
  return value
    ?.split(",")
    .map((item) => item.trim())
    .filter(Boolean) ?? [];
}

function optionalUrl(value?: string) {
  return value?.trim() ? value.trim() : null;
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="panel max-w-none">
      <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function ProfileForm({ initial, onSaved }: { initial?: CareerProfile; onSaved: () => void }) {
  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    values: {
      display_name: initial?.display_name ?? "",
      headline: initial?.headline ?? "",
      career_level: initial?.career_level ?? "JUNIOR",
      years_of_experience: initial?.years_of_experience ?? 0,
      desired_job_title: initial?.desired_job_title ?? "",
      introduction: initial?.introduction ?? "",
    },
  });
  const mutation = useMutation({ mutationFn: profileApi.saveProfile, onSuccess: onSaved });

  return (
    <Section title="기본 프로필">
      <form className="grid gap-3" onSubmit={form.handleSubmit((value) => mutation.mutate(value))}>
        <input className="input" placeholder="표시 이름" {...form.register("display_name")} />
        <input className="input" placeholder="한 줄 소개" {...form.register("headline")} />
        <select className="input" {...form.register("career_level")}>
          {["ENTRY", "JUNIOR", "MID", "SENIOR", "CAREER_CHANGE"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <input
          className="input"
          placeholder="전체 경력 연수"
          type="number"
          {...form.register("years_of_experience", { valueAsNumber: true })}
        />
        <input className="input" placeholder="희망 직무" {...form.register("desired_job_title")} />
        <textarea className="input min-h-24" placeholder="자기소개" {...form.register("introduction")} />
        <SubmitButton pending={mutation.isPending} label="프로필 저장" />
      </form>
    </Section>
  );
}

function SkillSection({ items, onChanged }: { items: UserSkill[]; onChanged: () => void }) {
  const form = useForm<z.infer<typeof skillSchema>>({
    resolver: zodResolver(skillSchema),
    defaultValues: {
      name: "",
      proficiency_level: "INTERMEDIATE",
      years_of_experience: 0,
      is_primary: false,
    },
  });
  const add = useMutation({ mutationFn: profileApi.addSkill, onSuccess: onChanged });
  const remove = useMutation({ mutationFn: profileApi.deleteSkill, onSuccess: onChanged });

  return (
    <Section title="기술 스택">
      <form
        className="grid gap-3"
        onSubmit={form.handleSubmit((value) => add.mutate(value, { onSuccess: () => form.reset() }))}
      >
        <input className="input" placeholder="기술명" {...form.register("name")} />
        <select className="input" {...form.register("proficiency_level")}>
          {["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <input
          className="input"
          type="number"
          placeholder="경력 연수"
          {...form.register("years_of_experience", { valueAsNumber: true })}
        />
        <label className="text-sm">
          <input type="checkbox" {...form.register("is_primary")} /> 대표 기술
        </label>
        <SubmitButton pending={add.isPending} label="기술 추가" />
      </form>
      <List
        items={items.map(
          (item) =>
            `${item.skill.name} · ${item.proficiency_level}${item.is_primary ? " · 대표" : ""}`,
        )}
        ids={items.map((item) => item.id)}
        onDelete={(id) => remove.mutate(id)}
      />
    </Section>
  );
}

function ExperienceSection({ items, onChanged }: { items: Experience[]; onChanged: () => void }) {
  const form = useForm<z.infer<typeof experienceSchema>>({
    resolver: zodResolver(experienceSchema),
    defaultValues: {
      company_name: "",
      position: "",
      employment_type: "FULL_TIME",
      start_date: "",
      end_date: "",
      is_current: false,
      description: "",
      achievements: "",
    },
  });
  const add = useMutation({ mutationFn: profileApi.addExperience, onSuccess: onChanged });
  const remove = useMutation({ mutationFn: profileApi.deleteExperience, onSuccess: onChanged });
  return (
    <Section title="경력">
      <form
        className="grid gap-3"
        onSubmit={form.handleSubmit((value) =>
          add.mutate(
            { ...value, end_date: value.is_current ? null : value.end_date },
            { onSuccess: () => form.reset() },
          ),
        )}
      >
        <input className="input" placeholder="회사명" {...form.register("company_name")} />
        <input className="input" placeholder="직무 또는 직책" {...form.register("position")} />
        <select className="input" {...form.register("employment_type")}>
          {["FULL_TIME", "CONTRACT", "INTERN", "FREELANCE", "PART_TIME", "SELF_EMPLOYED", "OTHER"].map(
            (item) => (
              <option key={item}>{item}</option>
            ),
          )}
        </select>
        <input className="input" type="date" {...form.register("start_date")} />
        <input className="input" type="date" {...form.register("end_date")} />
        <label className="text-sm">
          <input type="checkbox" {...form.register("is_current")} /> 재직 중
        </label>
        <textarea className="input" placeholder="담당 업무" {...form.register("description")} />
        <SubmitButton pending={add.isPending} label="경력 추가" />
      </form>
      <List
        items={items.map((item) => `${item.company_name} · ${item.position}`)}
        ids={items.map((item) => item.id)}
        onDelete={(id) => remove.mutate(id)}
      />
    </Section>
  );
}

function ProjectSection({ items, onChanged }: { items: Project[]; onChanged: () => void }) {
  const form = useForm<z.infer<typeof projectSchema>>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: "",
      summary: "",
      role: "",
      start_date: "",
      end_date: "",
      is_ongoing: false,
      repository_url: "",
      service_url: "",
      skill_names: "",
    },
  });
  const add = useMutation({ mutationFn: profileApi.addProject, onSuccess: onChanged });
  const remove = useMutation({ mutationFn: profileApi.deleteProject, onSuccess: onChanged });
  return (
    <Section title="프로젝트">
      <form
        className="grid gap-3"
        onSubmit={form.handleSubmit((value) =>
          add.mutate(
            {
              ...value,
              end_date: value.is_ongoing ? null : value.end_date || null,
              repository_url: optionalUrl(value.repository_url),
              service_url: optionalUrl(value.service_url),
              skill_names: splitList(value.skill_names),
            },
            { onSuccess: () => form.reset() },
          ),
        )}
      >
        <input className="input" placeholder="프로젝트명" {...form.register("name")} />
        <input className="input" placeholder="역할" {...form.register("role")} />
        <input className="input" type="date" {...form.register("start_date")} />
        <input className="input" type="date" {...form.register("end_date")} />
        <input className="input" placeholder="기술 스택, 쉼표로 구분" {...form.register("skill_names")} />
        <input className="input" placeholder="GitHub URL" {...form.register("repository_url")} />
        <SubmitButton pending={add.isPending} label="프로젝트 추가" />
      </form>
      <List
        items={items.map((item) => `${item.name}${item.role ? ` · ${item.role}` : ""}`)}
        ids={items.map((item) => item.id)}
        onDelete={(id) => remove.mutate(id)}
      />
    </Section>
  );
}

function PreferenceSection({ initial, onChanged }: { initial?: JobPreference; onChanged: () => void }) {
  const form = useForm<z.infer<typeof preferenceSchema>>({
    resolver: zodResolver(preferenceSchema),
    values: {
      preferred_locations: initial?.preferred_locations.join(", ") ?? "",
      desired_roles: initial?.desired_roles.join(", ") ?? "",
      priority_keywords: initial?.priority_keywords.join(", ") ?? "",
      remote_preference: initial?.remote_preference ?? "ANY",
      minimum_salary: initial?.minimum_salary ?? 0,
    },
  });
  const save = useMutation({ mutationFn: profileApi.savePreferences, onSuccess: onChanged });
  return (
    <Section title="희망 조건">
      <form
        className="grid gap-3"
        onSubmit={form.handleSubmit((value) =>
          save.mutate({
            preferred_employment_types: ["FULL_TIME"],
            preferred_company_sizes: ["ANY"],
            preferred_locations: splitList(value.preferred_locations),
            desired_roles: splitList(value.desired_roles),
            priority_keywords: splitList(value.priority_keywords),
            remote_preference: value.remote_preference,
            minimum_salary: value.minimum_salary,
          }),
        )}
      >
        <input className="input" placeholder="희망 지역, 쉼표로 구분" {...form.register("preferred_locations")} />
        <input className="input" placeholder="희망 직무, 쉼표로 구분" {...form.register("desired_roles")} />
        <select className="input" {...form.register("remote_preference")}>
          {["ANY", "ONSITE", "HYBRID", "REMOTE"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <input
          className="input"
          type="number"
          placeholder="최소 희망 연봉"
          {...form.register("minimum_salary", { valueAsNumber: true })}
        />
        <SubmitButton pending={save.isPending} label="희망 조건 저장" />
      </form>
    </Section>
  );
}

function ExclusionSection({ items, onChanged }: { items: ExcludedCondition[]; onChanged: () => void }) {
  const form = useForm<z.infer<typeof exclusionSchema>>({
    resolver: zodResolver(exclusionSchema),
    defaultValues: { condition_type: "LOCATION", value: "", reason: "", is_active: true },
  });
  const add = useMutation({ mutationFn: profileApi.addExclusion, onSuccess: onChanged });
  const remove = useMutation({ mutationFn: profileApi.deleteExclusion, onSuccess: onChanged });
  return (
    <Section title="지원 제외 조건">
      <form
        className="grid gap-3"
        onSubmit={form.handleSubmit((value) => add.mutate(value, { onSuccess: () => form.reset() }))}
      >
        <select className="input" {...form.register("condition_type")}>
          {["LOCATION", "COMPANY_SIZE", "REQUIRED_SKILL", "EXCLUDED_KEYWORD", "OTHER"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <input className="input" placeholder="제외 값" {...form.register("value")} />
        <input className="input" placeholder="이유" {...form.register("reason")} />
        <SubmitButton pending={add.isPending} label="제외 조건 추가" />
      </form>
      <List
        items={items.map(
          (item) => `${item.condition_type} · ${item.value}${item.is_active ? "" : " · 비활성"}`,
        )}
        ids={items.map((item) => item.id)}
        onDelete={(id) => remove.mutate(id)}
      />
    </Section>
  );
}

function PortfolioSection({ items, onChanged }: { items: PortfolioLink[]; onChanged: () => void }) {
  const form = useForm<z.infer<typeof portfolioSchema>>({
    resolver: zodResolver(portfolioSchema),
    defaultValues: {
      link_type: "GITHUB",
      title: "",
      url: "",
      is_primary: false,
      display_order: 0,
    },
  });
  const add = useMutation({ mutationFn: profileApi.addPortfolioLink, onSuccess: onChanged });
  const remove = useMutation({ mutationFn: profileApi.deletePortfolioLink, onSuccess: onChanged });
  return (
    <Section title="포트폴리오 링크">
      <form
        className="grid gap-3"
        onSubmit={form.handleSubmit((value) => add.mutate(value, { onSuccess: () => form.reset() }))}
      >
        <select className="input" {...form.register("link_type")}>
          {["GITHUB", "NOTION", "PORTFOLIO", "BLOG", "LINKEDIN", "OTHER"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <input className="input" placeholder="제목" {...form.register("title")} />
        <input className="input" placeholder="https://..." {...form.register("url")} />
        <label className="text-sm">
          <input type="checkbox" {...form.register("is_primary")} /> 대표 링크
        </label>
        <SubmitButton pending={add.isPending} label="링크 추가" />
      </form>
      <List
        items={items.map((item) => `${item.title} · ${item.url}${item.is_primary ? " · 대표" : ""}`)}
        ids={items.map((item) => item.id)}
        onDelete={(id) => remove.mutate(id)}
      />
    </Section>
  );
}

function SubmitButton({ pending, label }: { pending: boolean; label: string }) {
  return (
    <button className="button-primary" disabled={pending} type="submit">
      {pending ? "저장 중..." : label}
    </button>
  );
}

function List({ items, ids, onDelete }: { items: string[]; ids: number[]; onDelete: (id: number) => void }) {
  if (items.length === 0) {
    return <p className="mt-4 text-sm text-slate-500">아직 등록된 항목이 없습니다.</p>;
  }
  return (
    <ul className="mt-4 grid gap-2">
      {items.map((item, index) => (
        <li
          className="flex items-center justify-between gap-3 rounded-md border border-slate-200 px-3 py-2 text-sm"
          key={ids[index]}
        >
          <span className="min-w-0 break-words">{item}</span>
          <button
            className="text-rose-700"
            onClick={() => window.confirm("삭제할까요?") && onDelete(ids[index])}
            type="button"
          >
            삭제
          </button>
        </li>
      ))}
    </ul>
  );
}
