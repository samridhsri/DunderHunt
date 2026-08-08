import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DunderHunt — Personal Decision Support Job Hunter",
  description: "Turn a messy job search into a ranked queue of decisions while keeping final control with Sam.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
