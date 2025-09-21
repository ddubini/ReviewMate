// app/layout.tsx
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body style={{ fontFamily: "system-ui, sans-serif" }}>
        <header style={{ padding: 12, borderBottom: "1px solid #eee" }}>
          <nav style={{ display: "flex", gap: 12 }}>
            <Link href="/">홈</Link>
            <Link href="/compose">리뷰 맡기기</Link>
            <Link href="/history">히스토리</Link>
            <Link href="/marketplace">Marketplace</Link>
          </nav>
        </header>
        <main style={{ maxWidth: 860, margin: "0 auto", padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}








