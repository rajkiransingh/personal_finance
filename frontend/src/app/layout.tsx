import "./globals.css";
import Sidebar from "@/components/sidebar";
import Topbar from "@/components/topbar";
import { Inter, Poppins } from "next/font/google";
import localFont from "next/font/local";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-body"
});

const playwrite = localFont({
  src: "../styles/fonts/PlaywriteFont.ttf",
  variable: "--font-header",
});

export const metadata = {
  title: "Mera Paisa",
  description: "Personal Finance Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${poppins.variable} ${playwrite.variable}`}>
      <body className="flex bg-[var(--color-bg)] text-[var(--color-text-primary)]">
        <Sidebar />
        <main className="flex-1 flex flex-col min-h-screen bg-[var(--color-bg)]">
          <Topbar />
          <div className="flex-1 p-6 bg-[var(--color-bg)]">{children}</div>
        </main>
      </body>
    </html>
  );
}