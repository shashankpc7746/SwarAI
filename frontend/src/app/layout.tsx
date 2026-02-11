import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";

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
  title: "SwarAI",
  description: "Advanced multi-agent AI system powered by CrewAI, LangChain, and Groq LLM with voice recognition, file management, and intelligent automation.",
  keywords: ["AI Assistant", "SwarAI", "Multi-Agent", "Voice Recognition", "Automation", "CrewAI", "LangChain"],
  authors: [{ name: "SwarAI Team" }],
  icons: {
    icon: "/swarai_favicon.png",
    shortcut: "/swarai_favicon.png",
    apple: "/swarai_favicon.png",
  },
  openGraph: {
    title: "SwarAI - Multi-Agent AI Assistant",
    description: "Advanced multi-agent AI system with voice recognition and intelligent automation",
    type: "website",
    siteName: "SwarAI",
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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <body className="antialiased m-0 p-0" suppressHydrationWarning>
        <Providers>
          <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
            <div className="relative z-10">
              {children}
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
