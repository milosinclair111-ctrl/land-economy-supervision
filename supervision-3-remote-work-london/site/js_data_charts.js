  // ================= STEP 4: change in London's share, by industry (data from analysis.py)
  (function () {
    const drawBars = (id, list, col) => {
      const svg = $(id), W = 360, l = 158, r = 40, rowH = 28, x0 = -6, x1 = 12;
      const X = v => l + (v - x0) / (x1 - x0) * (W - l - r);
      svg.setAttribute("viewBox", `0 0 360 ${rowH * list.length + 40}`);
      [-4, 0, 4, 8].forEach(v => { el("line", { x1: X(v), x2: X(v), y1: 0, y2: rowH * list.length, stroke: v === 0 ? "#333" : "#ebe8e0", "stroke-width": v === 0 ? 1.5 : 1 }, svg); tx(svg, X(v), rowH * list.length + 16, (v > 0 ? "+" : "") + v, { "text-anchor": "middle", "font-size": 11 }); });
      tx(svg, (l + W - r) / 2, rowH * list.length + 32, "change in London's share (points)", { "text-anchor": "middle", "font-size": 11, fill: "#666" });
      list.forEach((o, i) => {
        const y = i * rowH, chg = o.post - o.pre, v = Math.max(x0, Math.min(x1, chg));
        const g = el("g", {}, svg);
        tx(g, l - 6, y + 18, o.name, { "text-anchor": "end", "font-size": 11.5 });
        el("rect", { x: Math.min(X(0), X(v)), y: y + 6, width: Math.max(1, Math.abs(X(v) - X(0))), height: rowH - 12, fill: col }, g);
        tx(g, v >= 0 ? X(v) + 4 : X(v) - 4, y + 18, sgn(chg), { "text-anchor": v >= 0 ? "start" : "end", "font-size": 11 });
        el("rect", { x: 0, y, width: W, height: rowH, fill: "transparent" }, g);
        g.addEventListener("mousemove", ev => show(`<b>${o.name}</b> (SIC ${String(o.div).padStart(2, "0")})<br>London's share of Britain's jobs:<br>2015–19: ${o.pre.toFixed(1)}%<br>2022–24: ${o.post.toFixed(1)}%`, ev));
        g.addEventListener("mouseleave", hide);
      });
    };
    const R = DATA.industries.filter(o => o.group === "R").sort((a, b) => (b.post - b.pre) - (a.post - a.pre));
    const P = DATA.industries.filter(o => o.group === "P").sort((a, b) => b.size - a.size).slice(0, 16).sort((a, b) => (b.post - b.pre) - (a.post - a.pre));
    drawBars("barsR", R, OR); drawBars("barsP", P, BL);
    const up = a => a.filter(o => o.post > o.pre).length, avg = a => a.reduce((x, o) => x + o.post - o.pre, 0) / a.length;
    $("barsread").textContent = `London's share rose in ${up(R)} of ${R.length} remote-able industries (average ${sgn(avg(R))} points), and in ${up(P)} of ${P.length} large in-person industries (average ${sgn(avg(P))} points).`;
  })();

  // ================= STEP 5: year-by-year gap (event study from analysis.py)
  (function () {
    const svg = $("event"), W = 720, H = 250, l = 50, r = 14, t = 14, b = 34;
    const ys = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
    const X = y => l + (y - 2014.5) / 10 * (W - l - r), Y = v => t + (1 - (v + 15) / 40) * (H - t - b);
    el("rect", { x: X(2019.6), y: t, width: X(2021.4) - X(2019.6), height: H - t - b, fill: "#efede6" }, svg);
    [-10, 0, 10, 20].forEach(v => { el("line", { x1: l, x2: W - r, y1: Y(v), y2: Y(v), stroke: v === 0 ? "#333" : "#ebe8e0" }, svg); tx(svg, l - 6, Y(v) + 4, (v > 0 ? "+" : "") + v + "%", { "text-anchor": "end" }); });
    ys.forEach(y => tx(svg, X(y), H - 10, y, { "text-anchor": "middle" }));
    DATA.event.forEach(([y, bb, se]) => {
      if (se) el("line", { x1: X(y), x2: X(y), y1: Y(bb - 1.96 * se), y2: Y(bb + 1.96 * se), stroke: "#666", "stroke-width": 1.5 }, svg);
      const c = el("circle", { cx: X(y), cy: Y(bb), r: 6, fill: y >= 2022 ? OR : "#666" }, svg);
      c.addEventListener("mousemove", ev => show(y === 2019 ? "<b>2019</b>: the reference year" : `<b>${y}</b>: ${sgn(bb)}% (95% range ${sgn(bb - 1.96 * se)} to ${sgn(bb + 1.96 * se)})`, ev));
      c.addEventListener("mouseleave", hide);
    });
  })();

  // ================= STEP 7: boundary tiles (data from region_test.py)
  (function () {
    const pos = { "Scotland": [1, 0], "North East": [2, 1], "North West": [1, 2], "Yorkshire and The Humber": [2, 2], "Wales": [0, 3], "West Midlands": [1, 3], "East Midlands": [2, 3], "East": [3, 3], "South West": [0, 4], "South East": [1, 4], "London": [2, 4] };
    const short = { "Yorkshire and The Humber": "Yorkshire" };
    const svg = $("tiles"), S = 82, G = 6, ox = 10, oy = 10;
    const shade = v => { const a = Math.min(1, Math.abs(v) / 2.4); return v >= 0 ? `rgba(217,88,31,${0.15 + 0.85 * a})` : `rgba(42,111,201,${0.15 + 0.85 * a})`; };
    const T = DATA.boundary;
    const res = {
      L: [T.london_vs_gb, "<b>London vs the rest of Britain.</b> Remote-able jobs became more concentrated in London after 2020. Borderline significant."],
      G: [T.gse_vs_gb, "<b>London plus the South East and East vs the rest of Britain.</b> No real change. The wider London region did not gain on the rest of the country."],
      W: [T.london_within_gse, "<b>London vs its own commuter belt.</b> The strongest result in the project. The jobs London gained came from the regions around it."]
    };
    const draw = mode => {
      svg.innerHTML = "";
      const inside = mode === "L" ? ["London"] : ["London", "South East", "East"];
      Object.entries(pos).forEach(([name, [c, rw]]) => {
        const v = DATA.regions[name], x = ox + c * (S + G), y = oy + rw * (S + G), label = (short[name] || name), dark = Math.abs(v) > 1;
        const g = el("g", {}, svg);
        el("rect", { x, y, width: S, height: S, fill: shade(v), stroke: inside.includes(name) ? "#111" : "#fff", "stroke-width": inside.includes(name) ? 4 : 1 }, g);
        const words = label.split(" "); const lines = label.length > 11 ? [words[0], words.slice(1).join(" ")] : [label];
        lines.forEach((ln, k) => tx(g, x + S / 2, y + S / 2 - 4 + k * 14 - (lines.length - 1) * 7, ln, { "text-anchor": "middle", "font-size": 12, "font-weight": "bold", fill: dark ? "#fff" : "#222" }));
        tx(g, x + S / 2, y + S / 2 + 24, sgn(v), { "text-anchor": "middle", "font-size": 13, fill: dark ? "#fff" : "#222" });
        g.addEventListener("mousemove", ev => show(`<b>${name}</b><br>Share of Britain's remote-able jobs: ${sgn(v)} points after 2020`, ev));
        g.addEventListener("mouseleave", hide);
      });
      const r = res[mode][0];
      $("bdnum").textContent = sgn(r.effect) + "%";
      $("bdtxt").innerHTML = res[mode][1] + `<br><span style="color:#666">p = ${r.p.toFixed(3)}</span>`;
      $("bdnum").style.color = mode === "G" ? "#646464" : OR;
    };
    document.querySelectorAll(".bd").forEach(bn => bn.addEventListener("click", () => {
      document.querySelectorAll(".bd").forEach(x => x.setAttribute("aria-pressed", String(x === bn))); draw(bn.dataset.b);
    }));
    draw("L");
  })();

  // ================= STEP 8: pay leak (data from analysis.py)
  (function () {
    const K = DATA.leak, Yr = K.years, bill = K.bill_bn, non = K.nonres_bn, sh = K.share;
    const bar = $("leakbar"), line = $("leakline");
    const W = 720, H = 220, l = 46, r = 12, t = 12, b = 30;
    const X = y => l + (y - 2009.5) / 16 * (W - l - r), Y = v => t + (1 - (v - 22) / 10) * (H - t - b);
    el("rect", { x: X(2019.6), y: t, width: X(2021.4) - X(2019.6), height: H - t - b, fill: "#efede6" }, line);
    [22, 24, 26, 28, 30, 32].forEach(v => { el("line", { x1: l, x2: W - r, y1: Y(v), y2: Y(v), stroke: "#ebe8e0" }, line); tx(line, l - 6, Y(v) + 4, v + "%", { "text-anchor": "end" }); });
    [2010, 2013, 2016, 2019, 2022, 2025].forEach(y => tx(line, X(y), H - 8, y, { "text-anchor": "middle" }));
    el("polyline", { points: Yr.map((y, i) => X(y) + "," + Y(sh[i])).join(" "), fill: "none", stroke: "#1b1b1b", "stroke-width": 2 }, line);
    el("line", { x1: X(2015), x2: X(2019), y1: Y(K.pre), y2: Y(K.pre), stroke: "#888", "stroke-dasharray": "4 3" }, line);
    el("line", { x1: X(2022), x2: X(2025), y1: Y(K.post), y2: Y(K.post), stroke: "#888", "stroke-dasharray": "4 3" }, line);
    const dot = el("circle", { r: 6, fill: OR }, line);
    const draw = () => {
      const y = +$("yr").value, i = Yr.indexOf(y), share = non[i] / bill[i];
      $("yv").textContent = y;
      bar.innerHTML = "";
      const w1 = (W - 2) * (1 - share);
      el("rect", { x: 0, y: 20, width: w1, height: 56, fill: "#cfcabd" }, bar);
      el("rect", { x: w1 + 2, y: 20, width: W - w1 - 2, height: 56, fill: OR }, bar);
      tx(bar, 10, 54, `Paid to London residents: £${(bill[i] - non[i]).toFixed(0)}bn`, { "font-size": 15, fill: "#222" });
      tx(bar, W - 10, 54, `To non-residents: £${non[i].toFixed(0)}bn`, { "font-size": 15, fill: "#fff", "text-anchor": "end", "font-weight": "bold" });
      tx(bar, 0, 102, `London workplace pay bill ${y}: £${bill[i].toFixed(0)}bn (ASHE-based estimate, cash terms)`, { "font-size": 14, fill: "#555" });
      $("leakread").textContent = `In ${y}, ${(100 * share).toFixed(1)}% of the pay earned in London went to people living outside London.`;
      dot.setAttribute("cx", X(y)); dot.setAttribute("cy", Y(sh[i]));
    };
    $("yr").addEventListener("input", draw); draw();
  })();

