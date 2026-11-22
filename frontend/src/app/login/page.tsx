"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { user, loading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.replace(user.must_change_password ? "/change-password" : user.role === "admin" ? "/admin" : "/");
    }
  }, [loading, user, router]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const me = await login(email, password);
      router.replace(me.must_change_password ? "/change-password" : me.role === "admin" ? "/admin" : "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-10">
      <div className="w-full max-w-[420px]">
        <div className="mb-6 flex items-center gap-3">
          <span className="brand-mark" aria-hidden="true">M</span>
          <span className="flex flex-col">
            <span className="wordmark text-[var(--color-ink)]">Mera Paisa</span>
            <span className="text-[length:var(--text-xs)] text-[var(--color-muted)]">
              money, made clear
            </span>
          </span>
        </div>

        <section className="card">
          <div className="card-head">
            <div>
              <h1 className="card-title">Welcome back</h1>
              <p className="card-note">Sign in to see your money picture.</p>
            </div>
          </div>

          <form onSubmit={submit} className="flex flex-col gap-4 p-5">
            <div>
              <label className="field-label" htmlFor="email">Email</label>
              <input
                id="email"
                className="field auth-field"
                type="email"
                autoComplete="username"
                required
                value={email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>
            <div>
              <label className="field-label" htmlFor="password">Password</label>
              <input
                id="password"
                className="field auth-field"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>

            {error && (
              <p className="rounded-[var(--radius-control)] bg-[var(--color-well)] px-3 py-2 text-[length:var(--text-sm)] font-semibold text-[var(--color-danger-text)]">
                {error}
              </p>
            )}

            <button className="btn btn-primary auth-submit w-full" type="submit" disabled={busy}>
              {busy ? "Signing in…" : "Sign in"}
            </button>
            <p className="text-center text-[length:var(--text-xs)] text-[var(--color-muted)]">
              Accounts are created by your administrator.
            </p>
          </form>
        </section>
      </div>
    </main>
  );
}
