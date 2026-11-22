"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import AdminOnly from "@/components/admin-only";
import { useAuth } from "@/lib/auth";

interface AdminUser {
  user_id: number;
  name: string;
  email: string | null;
  role: string;
  is_active: boolean;
}
interface Household {
  household_id: number;
  name: string;
  is_active: boolean;
  members: { user_id: number; name: string; scope_mode: string }[];
}

export default function AdminOverviewPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [households, setHouseholds] = useState<Household[]>([]);

  useEffect(() => {
    if (user?.role !== "admin") return;
    void apiFetch("/api/admin/users")
      .then((res) => res.json())
      .then(setUsers)
      .catch(() => setUsers([]));
    void apiFetch("/api/admin/households")
      .then((res) => res.json())
      .then(setHouseholds)
      .catch(() => setHouseholds([]));
  }, [user?.role]);

  return (
    <AdminOnly>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-[26px] font-extrabold tracking-tight text-[var(--color-ink)]">
            Admin console
          </h1>
          <p className="text-[length:var(--text-sm)] text-[var(--color-muted)]">
            Manage who can sign in, what they can see, and how the app is configured.
          </p>
        </div>
        <span className="badge badge-warning">Administrator only</span>
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <section className="card">
          <div className="card-head">
            <h2 className="card-title">Accounts</h2>
          </div>
          <p className="card-body text-[32px] font-extrabold text-[var(--color-ink)]">{users.length}</p>
          <p className="border-t border-[var(--color-rule)] px-5 py-3 text-[length:var(--text-xs)] text-[var(--color-muted)]">
            {users.filter((u) => u.is_active).length} active
          </p>
        </section>
        <section className="card">
          <div className="card-head">
            <h2 className="card-title">Households</h2>
          </div>
          <p className="card-body text-[32px] font-extrabold text-[var(--color-ink)]">{households.length}</p>
          <p className="border-t border-[var(--color-rule)] px-5 py-3 text-[length:var(--text-xs)] text-[var(--color-muted)]">
            Combined views configured
          </p>
        </section>
        <section className="card">
          <div className="card-head">
            <h2 className="card-title">Personal data access</h2>
          </div>
          <p className="card-body text-[length:var(--text-sm)] text-[var(--color-muted)]">
            The Financer account manages the app but cannot see anyone&apos;s assets or transactions.
          </p>
        </section>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">
        <Link href="/admin/users" className="card card-interactive">
          <div className="card-head">
            <h2 className="card-title">Users</h2>
            <span className="card-note">Create accounts, roles and passwords</span>
          </div>
        </Link>
        <Link href="/admin/access" className="card card-interactive">
          <div className="card-head">
            <h2 className="card-title">Access &amp; sharing</h2>
            <span className="card-note">Link couples · choose who can combine views</span>
          </div>
        </Link>
      </div>
    </AdminOnly>
  );
}
