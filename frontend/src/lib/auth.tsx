"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { apiFetch, apiJson } from "./api";

export type ViewMode = "personal" | "household";

export interface AuthUser {
  user_id: number;
  name: string;
  email: string | null;
  role: "admin" | "user";
  must_change_password: boolean;
  view: ViewMode;
  can_household_view: boolean;
}

export interface Preferences {
  theme: string | null;
  filters: Record<string, unknown>;
  strategies: Record<string, unknown>;
  page_size: number | null;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  preferences: Preferences;
  login: (email: string, password: string) => Promise<AuthUser>;
  logout: () => Promise<void>;
  setView: (view: ViewMode) => Promise<void>;
  changePassword: (current: string, next: string) => Promise<AuthUser>;
  savePreferences: (patch: Partial<Preferences>) => Promise<void>;
  refresh: () => Promise<void>;
}

const EMPTY_PREFERENCES: Preferences = {
  theme: null,
  filters: {},
  strategies: {},
  page_size: null,
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [preferences, setPreferences] = useState<Preferences>(EMPTY_PREFERENCES);

  const applyTheme = useCallback((theme: string | null) => {
    if (theme !== "light" && theme !== "dark") return;
    document.documentElement.dataset.mode = theme;
    try {
      localStorage.setItem("mera-paisa-mode", theme);
    } catch {
      // private browsing may block storage; the in-memory mode still applies
    }
  }, []);

  const refresh = useCallback(async () => {
    try {
      const me = await apiJson<AuthUser>("/api/auth/me");
      setUser(me);
      const prefs = await apiJson<Preferences>("/api/auth/preferences");
      setPreferences(prefs);
      applyTheme(prefs.theme);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [applyTheme]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "Sign in failed");
      }
      const me = (await response.json()) as AuthUser;
      setUser(me);
      setLoading(false);
      try {
        const prefs = await apiJson<Preferences>("/api/auth/preferences");
        setPreferences(prefs);
        applyTheme(prefs.theme);
      } catch {
        // preferences are optional on first login
      }
      return me;
    },
    [applyTheme]
  );

  const logout = useCallback(async () => {
    await apiFetch("/api/auth/logout", { method: "POST" });
    setUser(null);
    setPreferences(EMPTY_PREFERENCES);
  }, []);

  const setView = useCallback(async (view: ViewMode) => {
    await apiFetch("/api/auth/view", {
      method: "POST",
      body: JSON.stringify({ view }),
    });
    setUser((current) => (current ? { ...current, view } : current));
  }, []);

  const changePassword = useCallback(
    async (current_password: string, new_password: string) => {
      const response = await apiFetch("/api/auth/change-password", {
        method: "POST",
        body: JSON.stringify({ current_password, new_password }),
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail.detail || "Could not change password");
      }
      const updated = (await response.json()) as AuthUser;
      setUser(updated);
      return updated;
    },
    []
  );

  const savePreferences = useCallback(
    async (patch: Partial<Preferences>) => {
      await apiFetch("/api/auth/preferences", {
        method: "PUT",
        body: JSON.stringify(patch),
      });
      setPreferences((current) => ({ ...current, ...patch }));
      if (patch.theme) applyTheme(patch.theme);
    },
    [applyTheme]
  );

  const value = useMemo(
    () => ({
      user,
      loading,
      preferences,
      login,
      logout,
      setView,
      changePassword,
      savePreferences,
      refresh,
    }),
    [
      user,
      loading,
      preferences,
      login,
      logout,
      setView,
      changePassword,
      savePreferences,
      refresh,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
