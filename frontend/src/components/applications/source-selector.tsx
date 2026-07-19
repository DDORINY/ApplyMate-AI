import type { ApplicationOptionItem } from "@/types/application";

type SourceSelectorProps = {
  label: string;
  value: string;
  options: ApplicationOptionItem[] | undefined;
  onChange: (value: string) => void;
  placeholder?: string;
};

export function SourceSelector({ label, value, options, onChange, placeholder = "선택 안 함" }: SourceSelectorProps) {
  return (
    <label className="grid gap-2 text-sm font-medium text-slate-700">
      {label}
      <select className="input" value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">{placeholder}</option>
        {(options ?? []).map((option) => (
          <option key={option.id} value={option.id} disabled={Boolean(option.disabled_reason)}>
            {option.label}
            {option.description ? ` · ${option.description}` : ""}
            {option.disabled_reason ? ` (${option.disabled_reason})` : ""}
          </option>
        ))}
      </select>
    </label>
  );
}
