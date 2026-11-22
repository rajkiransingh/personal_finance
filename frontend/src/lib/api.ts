"use client";

const CSRF_COOKIE = "mp_csrf";

export function getCsrfToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((entry) => entry.startsWith(`${CSRF_COOKIE}=`));
  return match ? decodeURIComponent(match.split("=")[1]) : null;
}

/** Same-origin fetch with cookie credentials and a CSRF header for mutations. */
export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const method = (init.method || "GET").toUpperCase();
  const headers = new Headers(init.headers);

  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const token = getCsrfToken();
    if (token) headers.set("X-CSRF-Token", token);
    if (!headers.has("Content-Type") && init.body && typeof init.body === "string") {
      headers.set("Content-Type", "application/json");
    }
  }

  const response = await fetch(input, {
    ...init,
    headers,
    credentials: "same-origin",
  });

  const onAuthPage =
    typeof window !== "undefined" &&
    (window.location.pathname === "/login" ||
      window.location.pathname === "/change-password");
  if (response.status === 401 && !input.startsWith("/api/auth/login") && !onAuthPage) {
    window.location.assign("/login");
  }
  return response;
}

export async function apiJson<T>(input: string, init: RequestInit = {}): Promise<T> {
  const response = await apiFetch(input, init);
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}
