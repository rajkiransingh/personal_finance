"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import AdminOnly from "@/components/admin-only";
import { useAuth } from "@/lib/auth";

interface AdminUser {
  user_id: number;
  name: string;
  email: string | null;
  role: string;
  is_active: boolean;
  auth_provider: string;
  must_change_password: boolean;
}

const emptyForm = { name: "", email: "", password: "", role: "user" };

export default function AdminUsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    if (user?.role !== "admin") return;
    void apiFetch("/api/admin/users")
      .then((res) => res.json())
      .then(setUsers)
      .catch(() => setUsers([]));
  }, [user?.role]);

  useEffect(load, [load]);

  const create = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await apiFetch("/api/admin/users", {
        method: "POST",
        body: JSON.stringify(form),
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "Could not create account");
      }
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create account");
    } finally {
      setBusy(false);
    }
  };

  const toggleActive = async (user: AdminUser) => {
    await apiFetch(`/api/admin/users/${user.user_id}`, {
      method: "PUT",
      body: JSON.stringify({ is_active: !user.is_active }),
    });
    load();
  };

  const changeRole = async (user: AdminUser) => {
    const role = user.role === "admin" ? "user" : "admin";
    await apiFetch(`/api/admin/users/${user.user_id}`, {
      method: "PUT",
      body: JSON.stringify({ role }),
    });
    load();
  };

  const resetPassword = async (user: AdminUser) => {
    const next = window.prompt(`New temporary password for ${user.name} (10+ characters)`);
    if (!next) return;
    const response = await apiFetch(`/api/admin/users/${user.user_id}/reset-password`, {
      method: "POST",
      body: JSON.stringify({ new_password: next }),
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      window.alert(detail.detail || "Could not reset password");
    }
    load();
  };

  return (
    <AdminOnly>
      <div className="mb-6">
        <h1 className="text-[26px] font-extrabold tracking-tight text-[var(--color-ink)]">Users</h1>
        <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
          Only administrators can add accounts or change roles.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_360px]">
        <section className="card card-flush">
          <div className="card-head">
            <h2 className="card-title">Accounts</h2>
            <span className="card-note">{users.length} total</span>
          </div>
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th className="num">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.user_id}>
                    <td className="font-semibold">{user.name}</td>
                    <td>{user.email || "—"}</td>
                    <td>
                      <span className={`badge ${user.role === "admin" ? "badge-warning" : "badge-neutral"}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${user.is_active ? "badge-positive" : "badge-negative"}`}>
                        {user.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td className="num">
                      <div className="flex justify-end gap-1">
                        <button className="btn btn-secondary btn-sm" type="button" onClick={() => void changeRole(user)}>
                          {user.role === "admin" ? "Make user" : "Make admin"}
                        </button>
                        <button className="btn btn-secondary btn-sm" type="button" onClick={() => void toggleActive(user)}>
                          {user.is_active ? "Disable" : "Enable"}
                        </button>
                        <button className="btn btn-ghost btn-sm" type="button" onClick={() => void resetPassword(user)}>
                          Reset password
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="card">
          <div className="card-head">
            <h2 className="card-title">Add an account</h2>
          </div>
          <form onSubmit={create} className="flex flex-col gap-4 p-5">
            <div>
              <label className="field-label" htmlFor="new-name">Name</label>
              <input id="new-name" className="field" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="field-label" htmlFor="new-email">Email</label>
              <input id="new-email" className="field" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div>
              <label className="field-label" htmlFor="new-password">Temporary password</label>
              <input id="new-password" className="field" type="password" required minLength={10} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
              <p className="field-help">They will be asked to change it at first sign-in.</p>
            </div>
            <div>
              <label className="field-label" htmlFor="new-role">Role</label>
              <select id="new-role" className="field" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            {error && <p className="text-[length:var(--text-sm)] font-semibold text-[var(--color-danger-text)]">{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? "Creating…" : "Create account"}
            </button>
          </form>
        </section>
      </div>
    </AdminOnly>
  );
}
