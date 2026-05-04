// Reproducible Chart.js module extracted from:
// "2026 Town Meeting voter guide — The Marblehead Independent.htm"
//
// Usage:
//   import { renderBudgetChart } from "./budgetChart.js";
//   renderBudgetChart({
//     canvas: document.getElementById("budgetChart"),
//     legendEl: document.getElementById("legend"),   // optional
//     detailEl: document.getElementById("detail"),   // optional
//   });

export function renderBudgetChart({ canvas, legendEl, detailEl }) {
  if (!canvas) throw new Error("renderBudgetChart: missing canvas element");
  if (typeof Chart === "undefined") throw new Error("renderBudgetChart: Chart.js not found (global Chart)");

  const segments = [
    { name: "Schools", value: 47.62, color: "#1E1F21", detail: "$47.62M · 43% of general fund; ~63% of functional spending once shared benefits are allocated" },
    { name: "Health insurance", value: 15.83, color: "#C2261D", detail: "$15.83M · 11.17% GIC rate hike for active employees; 5.1% for retirees" },
    { name: "Pension", value: 8.2, color: "#B85C1F", detail: "~$8.2M · Rising 8.6% annually; will not level off until 2036" },
    { name: "Debt service", value: 11.1, color: "#6B7280", detail: "$11.1M · Includes school construction bonds" },
    { name: "Town departments", value: 21.92, color: "#375E97", detail: "~$21.9M · Town-side operating (police, fire, DPW, library, etc.) after cuts" },
    { name: "Curbside collection", value: 2.19, color: "#3D7A47", detail: "$2.19M · New line item; Republic Services contract" },
    { name: "Other general fund", value: 2.92, color: "#7B5EA7", detail: "~$2.9M · Remaining general fund items" },
    { name: "Sewer enterprise", value: 4.8, color: "#2A7A6B", detail: "$4.8M enterprise fund" },
    { name: "Water enterprise", value: 6.87, color: "#2E6E9E", detail: "$6.87M enterprise fund" },
    { name: "Harbor enterprise", value: 1.32, color: "#5A6577", detail: "$1.32M enterprise fund" },
  ];
  const total = segments.reduce((s, d) => s + d.value, 0);

  const ctx = canvas.getContext("2d");
  const chart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: segments.map(s => s.name),
      datasets: [{
        data: segments.map(s => s.value),
        backgroundColor: segments.map(s => s.color),
        borderColor: "#FDF9F4",
        borderWidth: 2,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "50%",
      plugins: {
        legend: { display: false },
        tooltip: {
          titleFont: { family: "Georgia, serif", size: 14, weight: "bold" },
          bodyFont: { family: "Georgia, serif", size: 13 },
          backgroundColor: "#FDF9F4",
          titleColor: "#1E1F21",
          bodyColor: "#4A4A4A",
          borderColor: "#D0CCC5",
          borderWidth: 1,
          callbacks: {
            label: (ctx) => {
              const seg = segments[ctx.dataIndex];
              return ` $${seg.value.toFixed(2)}M (${(seg.value / total * 100).toFixed(1)}%)`;
            }
          }
        }
      },
      onHover: (_evt, elements) => {
        if (elements.length) showDetail(elements[0].index);
      }
    }
  });

  function showDetail(i) {
    if (!detailEl) return;
    detailEl.style.borderLeftColor = segments[i].color;
    detailEl.textContent = segments[i].detail;
  }

  if (legendEl) {
    legendEl.innerHTML = "";
    segments.forEach((seg, i) => {
      const item = document.createElement("div");
      item.className = "legend-item";
      item.innerHTML = `<span class="swatch" style="background:${seg.color}"></span><span class="legend-label"><strong>${seg.name}</strong> <span class="pct">$${seg.value.toFixed(seg.value % 1 === 0 ? 1 : 2)}M (${(seg.value / total * 100).toFixed(1)}%)</span></span>`;
      item.addEventListener("mouseenter", () => showDetail(i));
      legendEl.appendChild(item);
    });
  }

  // Initialize detail panel to first segment if present
  if (detailEl) showDetail(0);
  return chart;
}

