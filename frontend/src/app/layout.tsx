import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Golden Cross — Quantitative Trading Research Platform",
    template: "%s | Golden Cross",
  },
  description:
    "Professional quantitative trading research platform. Create strategies, backtest, scan markets, and analyze performance.",
  keywords: [
    "algorithmic trading",
    "quantitative research",
    "backtesting",
    "stock scanner",
    "portfolio analytics",
    "EMA strategy",
    "NSE",
  ],
  authors: [{ name: "Golden Cross Platform" }],
  openGraph: {
    type: "website",
    locale: "en_IN",
    siteName: "Golden Cross Research Platform",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} dark h-full`} suppressHydrationWarning>
      <body className="min-h-full bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
