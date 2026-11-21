import "./globals.css";
import Sidebar from "@/components/sidebar";
import Topbar from "@/components/topbar";
import Footer from "@/components/footer";
import { Plus_Jakarta_Sans } from "next/font/google";
import Providers from "./providers";

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
          <div className="flex min-h-screen w-full bg-paper">
            <Sidebar />
            <div className="flex min-h-screen min-w-0 flex-1 flex-col bg-paper">
              <Topbar />
              <main className="flex-1 overflow-y-auto px-5 py-6 md:px-8 md:py-8">
                <div className="mx-auto w-full max-w-[1440px]">{children}</div>
              </main>
              <Footer />
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
