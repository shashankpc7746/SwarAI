import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CrewAI Agentic Assistant | Modern AI Experience",
  description: "Advanced multi-agent AI system powered by CrewAI with voice recognition, file management, and intelligent automation.",
  keywords: ["AI Assistant", "CrewAI", "Multi-Agent", "Voice Recognition", "Automation"],
  authors: [{ name: "CrewAI Team" }],
  openGraph: {
    title: "CrewAI Agentic Assistant",
    description: "Advanced multi-agent AI system with voice recognition and intelligent automation",
    type: "website",
    siteName: "CrewAI Assistant",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="antialiased">
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
          <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
          <div className="relative z-10">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
