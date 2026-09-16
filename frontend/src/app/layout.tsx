import type { Metadata } from "next";

import Header from "@/components/Header";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: { default: "AMUCS Nexus", template: "%s | AMUCS Nexus" },
  description:
    "Knowledge, search, and AI information platform for the AMU Department of Computer Science.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Header />
        {children}
        <footer className="site-footer">
          <p>
            Open-source. Source-grounded. Not an official AMU communication channel.
          </p>
        </footer>
      </body>
    </html>
  );
}