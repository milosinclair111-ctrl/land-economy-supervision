  // ================= model (Krugman 1991, FKV normalisation, plus theta)
  const SIG = 5, MU = 0.4;
  function solve(lam, T, th, w0) {
    const s = SIG, farm = (1 - MU) / 2, L = [lam, 1 - lam], tf = Math.pow(T, 1 - s);
    let w = w0 ? w0.slice() : [1, 1], G = [1, 1];
    for (let it = 0; it < 3000; it++) {
      const Y = [MU * ((1 - th) * L[0] * w[0] + th * L[1] * w[1]) + farm, MU * ((1 - th) * L[1] * w[1] + th * L[0] * w[0]) + farm];
      const a0 = Math.pow(w[0], 1 - s), a1 = Math.pow(w[1], 1 - s);
      G = [Math.pow(L[0] * a0 + L[1] * a1 * tf, 1 / (1 - s)), Math.pow(L[0] * a0 * tf + L[1] * a1, 1 / (1 - s))];
      const g0 = Math.pow(G[0], s - 1), g1 = Math.pow(G[1], s - 1);
      const n0 = Math.pow(Y[0] * g0 + Y[1] * g1 * tf, 1 / s), n1 = Math.pow(Y[0] * g0 * tf + Y[1] * g1, 1 / s);
      const d = Math.max(Math.abs(n0 - w[0]), Math.abs(n1 - w[1]));
      w = [0.5 * w[0] + 0.5 * n0, 0.5 * w[1] + 0.5 * n1];
      if (d < 1e-10) break;
    }
    const c = [Math.pow(G[0], -MU), Math.pow(G[1], -MU)];
    return { w, om: [w[0] * ((1 - th) * c[0] + th * c[1]), w[1] * ((1 - th) * c[1] + th * c[0])] };
  }
  const gap = (lam, T, th) => { const o = solve(lam, T, th).om; return o[0] - o[1]; };
  const regime = (T, q) => { const s = gap(0.5001, T, q) - gap(0.4999, T, q) < 0, c = gap(1, T, q) > 0; return s && c ? "both" : s ? "disp" : c ? "cp" : "part"; };

  // ================= STEP 1: dots
  (function () {
    const cv = $("dots"), cx = cv.getContext("2d"), W = cv.width, H = cv.height;
    const N = 120, NF = 60;
    let lam = 0.5, wcache = null, n1 = 60;
    const C = [{ x: W * 0.27, y: H * 0.53 }, { x: W * 0.73, y: H * 0.53 }];
    // golden-angle packing positions
    const slot = (k, n) => { const r = 14.5 * Math.sqrt(k + 0.5), a = k * 2.39996; return [r * Math.cos(a), r * Math.sin(a)]; };
    const dots = []; for (let i = 0; i < N; i++) dots.push({ x: C[i % 2].x, y: C[i % 2].y });
    const T = $("t1"), TH = $("th1");
    const upd = () => { $("t1v").textContent = (+T.value).toFixed(2); $("th1v").textContent = (+TH.value).toFixed(2); };
    T.addEventListener("input", upd); TH.addEventListener("input", upd); upd();
    $("even").addEventListener("click", () => { lam = 0.5; });
    $("head").addEventListener("click", () => { lam = 0.62; });
    let last = 0;
    function frame(ts) {
      const t = +T.value, th = +TH.value;
      const r = solve(lam, t, th, wcache); wcache = r.w;
      const g = r.om[0] - r.om[1];
      // migration towards the higher real wage, with a little noise so history is never perfectly even
      lam += 2.0 * lam * (1 - lam) * g;
      // if an even split is unstable, give region 1 a small push so the tip always goes the same way
      if (Math.abs(lam - 0.5) < 0.02 && gap(0.51, t, th) - gap(0.49, t, th) > 0) lam += 0.003;
      lam = Math.min(0.996, Math.max(0.004, lam));   // never exactly 0 or 1, so a cluster can still unravel
      const target = (lam - 0.004) / 0.992 * N;
      if (Math.abs(target - n1) > 0.75) n1 = Math.round(target);   // small hysteresis so a dot doesn't flicker between regions
      cx.clearRect(0, 0, W, H);
      for (let k = 0; k < 2; k++) {
        const ln = n1 / N, share = k === 0 ? (MU * ln + (1 - MU) / 2) : (MU * (1 - ln) + (1 - MU) / 2);
        cx.beginPath(); cx.arc(C[k].x, C[k].y, 95 + 190 * share, 0, 6.283); cx.fillStyle = "#f4f2ec"; cx.fill(); cx.strokeStyle = "#cfcabd"; cx.lineWidth = 2; cx.stroke();
        cx.fillStyle = "#333"; cx.font = "bold 30px Arial"; cx.textAlign = "center";
        cx.fillText(k === 0 ? "Region 1" : "Region 2", C[k].x, 34);
        cx.font = "26px Arial"; cx.fillStyle = "#555";
        cx.fillText("real wage " + (r.om[k] / ((r.om[0] + r.om[1]) / 2) * 100).toFixed(0), C[k].x, H - 22);
      }
      // farmers: fixed, half each side
      for (let i = 0; i < NF; i++) { const k = i % 2, [dx, dy] = slot(Math.floor(i / 2), 0); cx.beginPath(); cx.arc(C[k].x + dx, C[k].y + dy, 7, 0, 6.283); cx.fillStyle = "#b9b6ad"; cx.fill(); }
            for (let i = 0; i < N; i++) {
        const k = i < n1 ? 0 : 1, idx = k === 0 ? i : N - 1 - i;   // fixed seat for each dot, so dots don't jump around
        const [dx, dy] = slot(NF / 2 + idx, N);
        const tx_ = C[k].x + dx, ty_ = C[k].y + dy, d = dots[i];
        d.x += (tx_ - d.x) * 0.08; d.y += (ty_ - d.y) * 0.08;
        cx.beginPath(); cx.arc(d.x, d.y, 9, 0, 6.283); cx.fillStyle = OR; cx.fill();
      }
      const pct = Math.round(Math.min(100, Math.max(0, (lam - 0.004) / 0.992 * 100)));
      let dir;
      if (Math.abs(g) < 2e-4 && pct > 40 && pct < 60) dir = (gap(0.51, t, th) - gap(0.49, t, th) < 0) ? "Settled at an even split: the pull of the bigger market is too weak to start a snowball. Lower the trade cost to see it tip." : "Even split, but it is unstable here: any small push will tip it.";
      else if (pct >= 99 || pct <= 1) dir = "Settled: one region has all the mobile workers. Raise the trade cost or θ far enough and it spreads out again.";
      else dir = g > 0 ? "Region 1 pays more, so workers are moving there." : "Region 2 pays more, so workers are moving there.";
      $("dotsread").textContent = `Trade cost ${t.toFixed(2)}, θ ${th.toFixed(2)}: region 1 has ${pct}% of the mobile workers. ${dir}`;
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  })();

  // ================= STEP 2: building the map
  (function () {
    const cv = $("map"), cx = cv.getContext("2d"), W = cv.width, H = cv.height;
    const l = 90, r = 20, t = 20, b = 80, nT = 84, nq = 45, lo = 1.01, hi = 2.2, qhi = 0.45;
    const cw = (W - l - r) / nT, ch = (H - t - b) / nq;
    const col = { cp: OR, both: GR, disp: BL, part: "#bbb" };
    function axes() {
      cx.fillStyle = "#fff"; cx.fillRect(0, 0, W, H);
      cx.strokeStyle = "#333"; cx.lineWidth = 2; cx.beginPath(); cx.moveTo(l, t); cx.lineTo(l, H - b); cx.lineTo(W - r, H - b); cx.stroke();
      cx.fillStyle = "#333"; cx.font = "24px Arial"; cx.textAlign = "center";
      [1.2, 1.4, 1.6, 1.8, 2.0, 2.2].forEach(v => cx.fillText(v.toFixed(1), l + (v - lo) / (hi - lo) * (W - l - r), H - b + 34));
      cx.fillText("Trade cost T (cheaper to the left)", (l + W - r) / 2, H - 10);
      cx.textAlign = "right"; [0, 0.1, 0.2, 0.3, 0.4].forEach(v => cx.fillText(v.toFixed(1), l - 12, H - b - v / qhi * (H - t - b) + 8));
      cx.textAlign = "left"; cx.fillText("θ", 18, t + 20);
    }
    axes();
    let running = false, done = false;
    $("runmap").addEventListener("click", () => {
      if (running) return; running = true; axes();
      let j = 0, runs = 0;
      const step = () => {
        for (let rep = 0; rep < 2 && j < nq; rep++, j++) {
          const q = qhi * (j + 0.5) / nq;
          for (let i = 0; i < nT; i++) {
            const T = lo + (hi - lo) * (i + 0.5) / nT, k = regime(T, q); runs++;
            cx.fillStyle = col[k]; cx.fillRect(l + i * cw, H - b - (j + 1) * ch, cw + 0.6, ch + 0.6);
          }
        }
        $("mapread").textContent = `Runs completed: ${runs.toLocaleString("en-GB")} of 3,780`;
        if (j < nq) requestAnimationFrame(step);
        else {
          running = false; done = true;
          cx.font = "bold 30px Arial"; cx.fillStyle = "#fff"; cx.textAlign = "center";
          cx.fillText("One cluster", l + (1.2 - lo) / (hi - lo) * (W - l - r), H - b - 0.05 / qhi * (H - t - b));
          cx.fillText("Spread out", l + (1.95 - lo) / (hi - lo) * (W - l - r), H - b - 0.3 / qhi * (H - t - b));
          $("mapread").textContent = "Done: 3,780 runs. Remote work moves us left and up at once, so where we end up depends on which move is bigger.";
        }
      };
      requestAnimationFrame(step);
    });
  })();

