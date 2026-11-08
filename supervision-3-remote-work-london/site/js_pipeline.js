  // ================= pipeline diagram
  (function () {
    const svg = $("pipe");
    const box = (x, y, w, h, title, sub, fill) => {
      el("rect", { x, y, width: w, height: h, fill: fill || "#fff", stroke: "#999" }, svg);
      tx(svg, x + w / 2, y + 22, title, { "text-anchor": "middle", "font-size": 13, "font-weight": "bold" });
      sub.forEach((s, k) => tx(svg, x + w / 2, y + 40 + k * 15, s, { "text-anchor": "middle", "font-size": 11.5, fill: "#555" }));
    };
    const arrow = (x1, y1, x2, y2) => { el("line", { x1, y1, x2, y2, stroke: "#777", "stroke-width": 1.5, "marker-end": "url(#pa)" }, svg); };
    const defs = el("defs", {}, svg), mk = el("marker", { id: "pa", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", fill: "#777" }, mk);
    box(4, 70, 120, 70, "Nomis API", ["ONS data,", "downloaded by code"], "#f4f2ec");
    box(170, 4, 150, 62, "BRES", ["jobs by workplace,", "88 industries × 11 regions"]);
    box(170, 144, 150, 62, "ASHE", ["pay by workplace", "and by residence"]);
    
    box(366, 4, 150, 62, "Group industries", ["remote-able vs", "in-person (ONS rates)"]);
    box(366, 74, 150, 62, "Tests", ["diff-in-diff, checks,", "boundary test"]);
    box(366, 144, 150, 62, "Pay leak", ["London pay earned", "by non-residents"]);
    box(562, 40, 154, 62, "Krugman model", ["3,780 runs with θ", "(checked vs textbook)"], "#f4f2ec");
    box(562, 112, 154, 62, "Answer", ["jobs in,", "people and pay out"], "#fbe3d6");
    arrow(124, 105, 170, 35); arrow(124, 105, 170, 175);
    arrow(320, 35, 366, 35); arrow(320, 175, 366, 175); arrow(441, 66, 441, 74);
    arrow(516, 105, 562, 143); arrow(516, 175, 562, 143); arrow(639, 102, 639, 112);
  })();
