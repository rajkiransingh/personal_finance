import "./globals.css";
import AppShell from "@/components/app-shell";
import { Plus_Jakarta_Sans } from "next/font/google";
import Providers from "./providers";
import { AuthProvider } from "@/lib/auth";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "600", "800"],
  variable: "--font-jakarta",
  display: "swap",
});

export const metadata = {
  title: "Mera Paisa · Personal Finance Tracker",
  description:
    "A personal money app for an Indian household: net worth, portfolio, cash flow and the transactions behind them.",
};

const themeScript = `
(function () {
  try {
    var stored = localStorage.getItem('mera-paisa-mode');
    var mode = stored || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.dataset.mode = mode;
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${jakarta.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-screen bg-paper font-body text-ink antialiased">
        <Providers>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </Providers>
      </body>
    </html>
  );
}
