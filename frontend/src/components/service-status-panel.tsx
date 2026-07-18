"use client";

import { useEffect, useState } from "react";

import { fetchHealth } from "@/lib/api/health";
import type { HealthData } from "@/types/health";

type LoadState = "loading" | "ready" | "error";

export function ServiceStatusPanel() {
  const [state, setState] = useState<LoadState>("loading");
  const [health, setHealth] = useState<HealthData | null>(null);
  const [message, setMessage] = useState("서비스 상태를 확인하고 있습니다.");

  useEffect(() => {
    let isMounted = true;

    fetchHealth()
      .then((response) => {
        if (!isMounted) {
          return;
        }
        setHealth(response.data);
        setMessage(response.message);
        setState("ready");
      })
      .catch(() => {
        if (!isMounted) {
          return;
        }
        setHealth(null);
        setMessage("Backend Health API에 연결할 수 없습니다.");
        setState("error");
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const rows = [
    { label: "Frontend", value: "UP" },
    { label: "Backend", value: health?.status ?? "UNKNOWN" },
    { label: "Database", value: health?.database ?? "UNKNOWN" },
    { label: "Redis", value: health?.redis ?? "UNKNOWN" },
  ];

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-4">
        <p className="text-sm font-medium text-slate-500">
          {state === "loading" ? "Loading" : state === "error" ? "Error" : "Ready"}
        </p>
        <p className="mt-1 text-lg font-semibold text-slate-950">{message}</p>
      </div>
      <div className="grid gap-0 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label} className="border-b border-slate-100 px-5 py-4 sm:border-r">
            <p className="text-sm text-slate-500">{row.label}</p>
            <p
              className={
                row.value === "UP"
                  ? "mt-1 text-2xl font-semibold text-emerald-700"
                  : row.value === "DOWN"
                    ? "mt-1 text-2xl font-semibold text-rose-700"
                    : "mt-1 text-2xl font-semibold text-slate-500"
              }
            >
              {row.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
