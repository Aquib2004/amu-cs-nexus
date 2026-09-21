import type { Metadata } from "next";

import Header from "@/components/Header";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: { default: "AMUCS Nexus", template: "%s | AMUCS Nexus" },
  description:
    "Knowledge, search, and AI information platform for the AMU Department of Computer Science. Ask YouRobo, the source-grounded assistant.",
  // The same AMU mark is used as the browser favicon so the tab is identifiable.
  icons: { icon: "/amu-logo.png" },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main-content">
          Skip to content
        </a>
        <Header />
        <main id="main-content">{children}</main>
        <footer className="site-footer">
          <p>
            AMUCS Nexus · Open-source and source-grounded. Not an official AMU
            communication channel. Verify final details on official AMU pages.
          </p>
        </footer>
      </body>
    </html>
  );
}