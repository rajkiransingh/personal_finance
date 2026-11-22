"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import AdminOnly from "@/components/admin-only";
import { useAuth } from "@/lib/auth";

interface Member {
  user_id: number;
  name: string | null;
  scope_mode: string;
}
interface Household {
  household_id: number;
  name: string;
  is_active: boolean;
  shared_domains: string | null;
  members: Member[];
}
interface AdminUser {
  user_id: number;
  name: string;
  email: string | null;
}

export default function AdminAccessPage() {
  const { user } = useAuth();
  const [households, setHouseholds] = useState<Household[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [first, setFirst] = useState("");
  const [second, setSecond] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(() => {
    if (user?.role !== "admin") return;
    void apiFetch("/api/admin/households")
      .then((res) => res.json())
      .then(setHouseholds)
      .catch(() => setHouseholds([]));
    void apiFetch("/api/admin/users")
      .then((res) => res.json())
      .then(setUsers)
      .catch(() => setUsers([]));
  }, [user?.role]);

  useEffect(load, [load]);

  const createHousehold = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    if (!first || !second || first === second) {
      setError("Choose two different people.");
      return;
    }
    const response = await apiFetch("/api/admin/households", {
      method: "POST",
      body: JSON.stringify({
        name: "Household",
        members: [
          { user_id: Number(first), scope_mode: "household" },
          { user_id: Number(second), scope_mode: "self" },
        ],
      }),
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      setError(detail.detail || "Could not link accounts");
      return;
    }
    setFirst("");
    setSecond("");
    load();
  };

  const setScopeMode = async (householdId: number, member: Member, scope_mode: string) => {
    await apiFetch(`/api/admin/households/${householdId}/members/${member.user_id}`, {
      method: "PUT",
      body: JSON.stringify({ scope_mode }),
    });
    load();
  };

  const toggleHousehold = async (household: Household) => {
    await apiFetch(`/api/admin/households/${household.household_id}`, {
      method: "PUT",
      body: JSON.stringify({ is_active: !household.is_active }),
    });
    load();
  };

  return (
    <AdminOnly>
      <div className="mb-6">
        <h1 className="text-[26px] font-extrabold tracking-tight text-[var(--color-ink)]">
          Access &amp; sharing
        </h1>
        <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
          Link two accounts so one partner can switch to a combined household view. The other stays personal-only.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_360px]">
        <div className="flex flex-col gap-5">
          {households.length === 0 && (
            <section className="card p-5 text-[length:var(--text-sm)] text-[var(--color-muted)]">
              No households linked yet.
            </section>
          )}
          {households.map((household) => (
            <section className="card" key={household.household_id}>
              <div className="card-head">
                <div>
                  <h2 className="card-title">{household.name}</h2>
                  <span className="card-note">
                    Shared domains: {household.shared_domains || "all"}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge ${household.is_active ? "badge-positive" : "badge-negative"}`}>
                    {household.is_active ? "Active" : "Disabled"}
                  </span>
                  <button className="btn btn-secondary btn-sm" type="button" onClick={() => void toggleHousehold(household)}>
                    {household.is_active ? "Disable" : "Enable"}
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Person</th>
                      <th>Combined view</th>
                    </tr>
                  </thead>
                  <tbody>
                    {household.members.map((member) => (
                      <tr key={member.user_id}>
                        <td className="font-semibold">{member.name || `User ${member.user_id}`}</td>
                        <td>
                          <select
                            className="field field-sm"
                            value={member.scope_mode}
                            onChange={(event) => void setScopeMode(household.household_id, member, event.target.value)}
                          >
                            <option value="self">Personal only</option>
                            <option value="household">Can switch to household</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ))}
        </div>

        <section className="card">
          <div className="card-head">
            <h2 className="card-title">Link a couple</h2>
          </div>
          <form onSubmit={createHousehold} className="flex flex-col gap-4 p-5">
            <div>
              <label className="field-label" htmlFor="first-person">First person</label>
              <select id="first-person" className="field" value={first} onChange={(e) => setFirst(e.target.value)}>
                <option value="">Choose…</option>
                {users.map((user) => <option key={user.user_id} value={user.user_id}>{user.name}</option>)}
              </select>
              <p className="field-help">This person can switch between personal and household views.</p>
            </div>
            <div>
              <label className="field-label" htmlFor="second-person">Second person</label>
              <select id="second-person" className="field" value={second} onChange={(e) => setSecond(e.target.value)}>
                <option value="">Choose…</option>
                {users.map((user) => <option key={user.user_id} value={user.user_id}>{user.name}</option>)}
              </select>
            </div>
            {error && <p className="text-[length:var(--text-sm)] font-semibold text-[var(--color-danger-text)]">{error}</p>}
            <button className="btn btn-primary" type="submit">Link accounts</button>
          </form>
        </section>
      </div>
    </AdminOnly>
  );
}
