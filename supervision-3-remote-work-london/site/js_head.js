(function () {
  "use strict";
  const $ = id => document.getElementById(id);
  const tip = $("tip");
  const show = (h, ev) => { tip.innerHTML = h; tip.style.display = "block"; tip.style.left = Math.min(ev.clientX + 14, innerWidth - 280) + "px"; tip.style.top = ev.clientY + 14 + "px"; };
  const hide = () => tip.style.display = "none";
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; };
  const tx = (p, x, y, s, a) => { const t = el("text", Object.assign({ x, y, "font-family": "Arial, sans-serif", "font-size": 12, fill: "#333" }, a || {}), p); t.textContent = s; return t; };
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const OR = css("--or"), BL = css("--bl"), GR = css("--gr");
  const sgn = v => { const r = Math.round(v * 10) / 10; return (r > 0 ? "+" : r < 0 ? "−" : "") + Math.abs(r).toFixed(1); };

