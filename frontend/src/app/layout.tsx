import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "AMUCS Nexus",
  description: "Knowledge, search, and AI information platform for the AMU Department of Computer Science.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
