// Reproducible Chart.js module extracted from:
// "2026 Town Meeting voter guide — The Marblehead Independent.htm"
//
// Usage:
//   import { renderOverrideChart } from "./overrideChart.js";
//   renderOverrideChart(document.getElementById("overrideChart"));

export function renderOverrideChart(canvas) {
  if (!canvas) throw new Error("renderOverrideChart: missing canvas element");
  if (typeof Chart === "undefined") throw new Error("renderOverrideChart: Chart.js not found (global Chart)");

  const ctx = canvas.getContext("2d");
  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Debt exclusions", "Operating overrides", "Capital exclusions"],
      datasets: [
        { label: "Passed", data: [68, 3, 5], backgroundColor: "#3D7A47", borderRadius: 2 },
        { label: "Failed", data: [16, 18, 5], backgroundColor: "#C2261D", borderRadius: 2 }
      ]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          max: 90,
          ticks: { font: { family: "Georgia, serif", size: 13 }, color: "#4A4A4A" },
          grid: { color: "#DDD8D0" },
        },
        y: {
          stacked: true,
          ticks: { font: { family: "Georgia, serif", size: 15, weight: "bold" }, color: "#1E1F21" },
          grid: { display: false },
        }
      },
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
            afterBody: (ctx) => {
              const passed = ctx?.[0]?.parsed?.x ?? 0;
              const failed = ctx?.[1]?.parsed?.x ?? 0;
              const total = passed + failed;
              if (!total) return "";
              return `Pass rate: ${(passed / total * 100).toFixed(0)}% (${passed}/${total})`;
            }
          }
        }
      }
    }
  });
}

