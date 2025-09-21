// app/page.tsx
import Link from "next/link";

export default function Home() {
  const box = { display:"block", padding:"14px 16px", border:"1px solid #111", borderRadius:10, textAlign:"center" } as const;
  return (
    <section>
      <h1 style={{ fontSize:24, fontWeight:700, marginBottom:16 }}>리뷰메이트</h1>
      <div style={{ display:"grid", gap:12, maxWidth:360 }}>
        <Link href="/compose" style={box}>1. 리뷰 맡기기</Link>
        <Link href="/history" style={box}>2. 히스토리</Link>
        <Link href="/marketplace" style={box}>3. Marketplace</Link>
      </div>
    </section>
  );
}
