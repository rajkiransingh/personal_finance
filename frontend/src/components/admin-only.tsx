"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function AdminOnly({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user && user.role !== "admin") router.replace("/");
  }, [loading, user, router]);

  if (loading || !user || user.role !== "admin") {
    return (
      <section className="card p-5 text-[length:var(--text-sm)] text-[var(--color-muted)]">
        Checking administrator access…
      </section>
    );
  }
  return <>{children}</>;
}
