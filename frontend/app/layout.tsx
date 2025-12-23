import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Disha - AI Health Coach",
  description: "India's first AI health coach - Your personal health companion",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
