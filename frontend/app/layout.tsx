import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "PanelStat — Panel Regression Platform",
  description: "No-code panel data regression analysis for researchers and analysts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: { fontSize: "14px", borderRadius: "8px" },
          }}
        />
        {children}
      </body>
    </html>
  );
}
