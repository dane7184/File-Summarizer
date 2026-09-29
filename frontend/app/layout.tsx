import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "File Summarizer",
  description: "Upload a file and get an AI summary",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
