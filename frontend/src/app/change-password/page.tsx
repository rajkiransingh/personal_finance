"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function ChangePasswordPage() {
  const router = useRouter();
  const { changePassword, logout } = useAuth();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (next !== confirm) {
      setError("The new passwords do not match.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const updated = await changePassword(current, next);
      router.replace(updated.role === "admin" ? "/admin" : "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not change password");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-10">
      <section className="card w-full max-w-[460px]">
        <div className="card-head">
          <div>
            <h1 className="card-title">Set a new password</h1>
            <p className="card-note">
              Use at least 10 characters. You stay signed in after saving.
            </p>
          </div>
        </div>
        <form onSubmit={submit} className="flex flex-col gap-4 p-5">
          <div>
            <label className="field-label" htmlFor="current">Current password</label>
            <input id="current" className="field" type="password" autoComplete="current-password" required value={current} onChange={(e) => setCurrent(e.target.value)} />
          </div>
          <div>
            <label className="field-label" htmlFor="next">New password</label>
            <input id="next" className="field" type="password" autoComplete="new-password" required value={next} onChange={(e) => setNext(e.target.value)} />
          </div>
          <div>
            <label className="field-label" htmlFor="confirm">Confirm new password</label>
            <input id="confirm" className="field" type="password" autoComplete="new-password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} />
          </div>
          {error && (
            <p className="rounded-[var(--radius-control)] bg-[var(--color-well)] px-3 py-2 text-[length:var(--text-sm)] font-semibold text-[var(--color-danger-text)]">
              {error}
            </p>
          )}
          <button className="btn btn-primary w-full" type="submit" disabled={busy}>
            {busy ? "Saving…" : "Save password"}
          </button>
          <button className="btn btn-ghost w-full" type="button" onClick={async () => { await logout(); router.replace("/login"); }}>
            Sign out
          </button>
        </form>
      </section>
    </main>
  );
}
