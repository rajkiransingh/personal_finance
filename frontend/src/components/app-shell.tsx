"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./sidebar";
import Topbar from "./topbar";
import Footer from "./footer";
import { useAuth } from "@/lib/auth";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user } = useAuth();

  // The sign-in and password-reset screens stand alone, without app chrome.
  if (pathname === "/login" || pathname === "/change-password") {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen w-full bg-paper">
      <Sidebar />
      <div className="flex min-h-screen min-w-0 flex-1 flex-col bg-paper">
        <Topbar />
        <main className="flex-1 overflow-y-auto px-5 py-6 md:px-8 md:py-8">
          <div className="mx-auto w-full max-w-[1440px]" key={`${user?.view || "personal"}`}>
            {children}
          </div>
        </main>
        <Footer />
      </div>
    </div>
  );
}
