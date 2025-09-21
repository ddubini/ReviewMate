// app/compose/page.tsx
"use client";

import { useState } from "react";

// 완성형 한글(가-힣) 1자 이상 포함 + 한글/공백만 허용
const HANGUL_SYLLABLE = /[\uAC00-\uD7A3]/;
const HANGUL_ONLY     = /^[\uAC00-\uD7A3\s]+$/;
// 숫자만
const DIGITS_ONLY     = /^\d+$/;

function isValidHangul(s: string) {
  const t = (s ?? "").trim();
  return t.length > 0 && HANGUL_ONLY.test(t) && HANGUL_SYLLABLE.test(t);
}
function isValidDigits(s: string) {
  const t = (s ?? "").trim();
  return t.length > 0 && DIGITS_ONLY.test(t);
}

export default function ComposePage() {
  // 진행 단계: 0 장소, 1 메뉴&가격, 2 대기, 3 톤, 4 사진/완료
  const [idx, setIdx] = useState(0);

  // 입력값(화면에 그대로 유지)
  const [place, setPlace]     = useState("");
  const [item, setItem]       = useState("");
  const [price, setPrice]     = useState("");    // 숫자만
  const [waitMin, setWaitMin] = useState("");    // 숫자만(필수)
  const [tone, setTone]       = useState("");
  const [photoUrl, setPhotoUrl] = useState<string|null>(null);

  // 🔒 절대 자동 진행 안 함: setIdx는 여기(onNext)에서만 호출
  const onNext = () => {
    // 단계별 검증 (버튼 눌렀을 때만 체크)
    if (idx === 0) {
      if (!isValidHangul(place)) return;
      setIdx(1);
      return;
    }
    if (idx === 1) {
      if (!isValidHangul(item)) return;
      if (!isValidDigits(price)) return;
      setIdx(2);
      return;
    }
    if (idx === 2) {
      if (!isValidDigits(waitMin)) return;
      setIdx(3);
      return;
    }
    if (idx === 3) {
      if (!isValidHangul(tone)) return;
      setIdx(4);
      return;
    }
    if (idx === 4) {
      // 완료 단계: 필요 시 요약 화면 등으로 연결
      alert("입력 완료!");
      return;
    }
  };

  const input = {
    width:"100%", padding:"10px 12px", border:"1px solid #ddd", borderRadius:8, fontSize:16,
  } as const;

  // 버튼 활성화(UX용, 없어도 됨 — 자동 진행과 무관)
  const canNext =
    idx === 0 ? isValidHangul(place) :
    idx === 1 ? isValidHangul(item) && isValidDigits(price) :
    idx === 2 ? isValidDigits(waitMin) :
    idx === 3 ? isValidHangul(tone) :
    true;

  return (
    <section>
      <h1 style={{ fontSize:20, fontWeight:700, marginBottom:12 }}>리뷰 맡기기</h1>

      {/* 1. 장소(한글만) */}
      {idx >= 0 && (
        <div style={{ border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16 }}>
          <div style={{ fontWeight:700, marginBottom:8 }}>1. 장소 (한글만)</div>
          <input
            placeholder="예: 스시지현"
            value={place}
            onChange={(e) => setPlace(e.target.value)}
            // ⛔ onKeyDown/자동 이동 없음
            style={input}
          />
          <div style={{ fontSize:12, color:"#6b7280", marginTop:6 }}>
            완성형 한글(가–힣)과 공백만 허용. 자음/모음 1글자만으론 진행 불가.
          </div>
          <div style={{ marginTop:10 }}>
            <button
              type="button"
              onClick={onNext}
              disabled={!canNext}
              style={{
                padding:"10px 14px", border:"1px solid #111", borderRadius:10,
                background: canNext ? "#111" : "#bbb", color:"#fff",
                cursor: canNext ? "pointer" : "not-allowed",
              }}
            >
              다음
            </button>
          </div>
        </div>
      )}

      {/* 2. 메뉴 & 가격 */}
      {idx >= 1 && (
        <div style={{ border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16 }}>
          <div style={{ fontWeight:700, marginBottom:8 }}>2. 메뉴 & 가격 (메뉴=한글, 가격=숫자)</div>
          <div style={{ display:"grid", gap:8 }}>
            <input
              placeholder="예: 오마카세"
              value={item}
              onChange={(e) => setItem(e.target.value)}
              style={input}
            />
            <div style={{ position:"relative" }}>
              <input
                placeholder="예: 60000"
                value={price}
                onChange={(e) => setPrice(e.target.value.replace(/\D+/g, ""))}
                inputMode="numeric"
                style={{ ...input, paddingRight:44 }}
              />
              <span style={{
                position:"absolute", right:12, top:0, bottom:0,
                display:"flex", alignItems:"center", color:"#555", pointerEvents:"none"
              }}>원</span>
            </div>
          </div>
          <div style={{ marginTop:10 }}>
            <button
              type="button"
              onClick={onNext}
              disabled={!canNext}
              style={{
                padding:"10px 14px", border:"1px solid #111", borderRadius:10,
                background: canNext ? "#111" : "#bbb", color:"#fff",
                cursor: canNext ? "pointer" : "not-allowed",
              }}
            >
              다음
            </button>
          </div>
        </div>
      )}

      {/* 3. 대기 시간(숫자만) */}
      {idx >= 2 && (
        <div style={{ border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16 }}>
          <div style={{ fontWeight:700, marginBottom:8 }}>3. 대기 시간 (분, 숫자만)</div>
          <input
            placeholder="예: 10"
            value={waitMin}
            onChange={(e) => setWaitMin(e.target.value.replace(/\D+/g, ""))}
            inputMode="numeric"
            style={input}
          />
          <div style={{ fontSize:12, color:"#6b7280", marginTop:6 }}>
            숫자만 허용(필수). 한글/기호가 섞이면 진행 불가.
          </div>
          <div style={{ marginTop:10 }}>
            <button
              type="button"
              onClick={onNext}
              disabled={!canNext}
              style={{
                padding:"10px 14px", border:"1px solid #111", borderRadius:10,
                background: canNext ? "#111" : "#bbb", color:"#fff",
                cursor: canNext ? "pointer" : "not-allowed",
              }}
            >
              다음
            </button>
          </div>
        </div>
      )}

      {/* 4. 톤 힌트(한글만) */}
      {idx >= 3 && (
        <div style={{ border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16 }}>
          <div style={{ fontWeight:700, marginBottom:8 }}>4. 톤 힌트 (한글만)</div>
          <input
            placeholder="예: 조금 더 감성적으로"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            style={input}
          />
          <div style={{ marginTop:10 }}>
            <button
              type="button"
              onClick={onNext}
              disabled={!canNext}
              style={{
                padding:"10px 14px", border:"1px solid #111", borderRadius:10,
                background: canNext ? "#111" : "#bbb", color:"#fff",
                cursor: canNext ? "pointer" : "not-allowed",
              }}
            >
              다음
            </button>
          </div>
        </div>
      )}

      {/* 5. 사진(선택) */}
      {idx >= 4 && (
        <div style={{ border:"1px solid #eee", borderRadius:12, padding:16, marginBottom:16 }}>
          <div style={{ fontWeight:700, marginBottom:8 }}>5. 사진 (선택)</div>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (!f) return;
              const url = URL.createObjectURL(f);
              setPhotoUrl(url);
            }}
          />
          {photoUrl && (
            <img
              src={photoUrl}
              alt="preview"
              style={{ marginTop:8, height:120, objectFit:"cover", borderRadius:8, border:"1px solid #ddd" }}
            />
          )}
          <div style={{ marginTop:10 }}>
            <button
              type="button"
              onClick={onNext}
              style={{
                padding:"10px 14px", border:"1px solid #111", borderRadius:10,
                background:"#111", color:"#fff", cursor:"pointer",
              }}
            >
              완료
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

