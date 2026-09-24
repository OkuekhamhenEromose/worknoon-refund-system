import React from "react";
import "./globals.css";

export const metadata = { title: "Worknoon Refund Support", description: "AI-powered refund support assessment" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
