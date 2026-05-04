// Reproducible Chart.js module extracted from:
// "2026 Town Meeting voter guide — The Marblehead Independent.htm"
//
// Usage:
//   import { renderInsuranceChart } from "./insuranceChart.js";
//   renderInsuranceChart(document.getElementById("insuranceChart"));

export function renderInsuranceChart(canvas) {
  if (!canvas) throw new Error("renderInsuranceChart: missing canvas element");
  // Chart.js must already be loaded globally as `Chart`.
  if (typeof Chart === "undefined") throw new Error("renderInsuranceChart: Chart.js not found (global Chart)");

  const labels = ["FY02","FY03","FY04","FY05","FY06","FY07","FY08","FY09","FY10","FY11","FY12","FY13","FY14","FY15","FY16","FY17","FY18","FY19","FY20","FY21","FY22","FY23","FY24","FY25","FY26","FY27*"];
  const spending = [9.1, 12.0, 14.5, 16.2, 18.0, 11.8, 10.5, 9.4, 9.2, 9.4, 9.5, 9.6, 9.8, 10.0, 10.1, 10.2, 10.3, 10.5, 10.7, 11.0, 11.5, 11.8, 12.2, 12.3, 13.7, 15.8];
  const share = [17.0, 22.0, 26.0, 29.0, 33.4, 21.0, 18.0, 16.1, 14.5, 14.2, 13.8, 13.5, 13.3, 13.1, 13.0, 12.9, 12.7, 12.6, 12.4, 12.5, 12.8, 13.0, 13.3, 13.5, 14.1, 14.1];

  const eraBoundaries = [
    { start: 0, end: 4, color: "rgba(252,228,228,0.45)" },
    { start: 5, end: 7, color: "rgba(220,240,224,0.45)" },
    { start: 8, end: 17, color: "rgba(221,230,240,0.45)" },
    { start: 18, end: 25, color: "rgba(245,237,222,0.45)" },
  ];

  const bgPlugin = {
    id: "shellWhiteBg",
    beforeDraw(chart) {
      const { ctx, width, height } = chart;
      ctx.save();
      ctx.fillStyle = "#FDF9F4";
      ctx.fillRect(0, 0, width, height);
      ctx.restore();
    }
  };

  const eraPlugin = {
    id: "eraBackground",
    beforeDraw(chart) {
      const { ctx, chartArea, scales } = chart;
      if (!chartArea) return;
      eraBoundaries.forEach(era => {
        const x1 = scales.x.getPixelForValue(era.start);
        const x2 = scales.x.getPixelForValue(era.end);
        ctx.fillStyle = era.color;
        ctx.fillRect(x1, chartArea.top, x2 - x1, chartArea.bottom - chartArea.top);
      });
    }
  };

  const annotationPlugin = {
    id: "annotations",
    afterDraw(chart) {
      const { ctx, chartArea, scales } = chart;
      if (!chartArea) return;
      ctx.save();

      const peakX = scales.x.getPixelForValue(4);
      const peakY = scales.y.getPixelForValue(18.0);
      ctx.fillStyle = "#c0392b";
      ctx.font = "bold 11px Georgia, serif";
      ctx.textAlign = "center";
      ctx.fillText("$18M peak", peakX, peakY - 14);

      const gicX = scales.x.getPixelForValue(5);
      const gicY = scales.y.getPixelForValue(11.8);
      ctx.fillStyle = "#27785a";
      ctx.font = "bold 10px Georgia, serif";
      ctx.fillText("GIC", gicX, gicY - 12);

      const fy27X = scales.x.getPixelForValue(25);
      const fy27Y = scales.y.getPixelForValue(15.8);
      ctx.fillStyle = "#c0392b";
      ctx.font = "bold 12px Georgia, serif";
      ctx.textAlign = "right";
      ctx.fillText("$15.8M", fy27X + 4, fy27Y - 12);

      const fy02X = scales.x.getPixelForValue(0);
      const fy02Y = scales.y.getPixelForValue(9.1);
      ctx.fillStyle = "#9ca3af";
      ctx.font = "11px Georgia, serif";
      ctx.textAlign = "left";
      ctx.fillText("$9.1M", fy02X + 6, fy02Y - 10);

      ctx.restore();
    }
  };

  const ctx = canvas.getContext("2d");
  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Spending ($M)",
        data: spending,
        borderColor: "#c0392b",
        backgroundColor: "rgba(192,57,43,0.08)",
        borderWidth: 2.5,
        fill: true,
        tension: 0.25,
        pointRadius: function(context) {
          const i = context.dataIndex;
          if (i === 0 || i === 4 || i === 5 || i === 8 || i === 23 || i === 25) return 5;
          return 2.5;
        },
        pointBackgroundColor: function(context) {
          if (context.dataIndex === 5) return "#FFFFFF";
          return "#c0392b";
        },
        pointBorderColor: function(context) {
          if (context.dataIndex === 5) return "#27785a";
          return "#FDF9F4";
        },
        pointBorderWidth: function(context) {
          if (context.dataIndex === 5) return 2.5;
          return 1.5;
        },
        pointHoverRadius: 7,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 20,
          ticks: {
            callback: v => `$${v}M`,
            font: { family: "Georgia, serif", size: 12 },
            color: "#9ca3af",
            stepSize: 5,
          },
          grid: { color: "#e5e7eb", drawBorder: false },
          border: { color: "#1a1a2e" },
        },
        x: {
          ticks: {
            font: { family: "Georgia, serif", size: 11 },
            color: "#9ca3af",
            maxRotation: 45,
            autoSkip: true,
            maxTicksLimit: 14,
          },
          grid: { display: false },
          border: { color: "#1a1a2e" },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          titleFont: { family: "Georgia, serif", size: 14, weight: "bold" },
          bodyFont: { family: "Georgia, serif", size: 13 },
          backgroundColor: "#FDF9F4",
          titleColor: "#1a1a2e",
          bodyColor: "#4A4A4A",
          borderColor: "#D0CCC5",
          borderWidth: 1,
          displayColors: false,
          callbacks: {
            label: (ctx) => `Spending: $${ctx.parsed.y.toFixed(1)}M`,
            afterLabel: (ctx) => `Share of general fund: ~${share[ctx.dataIndex]}%`
          }
        }
      },
      interaction: { mode: "index", intersect: false },
    },
    plugins: [bgPlugin, eraPlugin, annotationPlugin],
  });
}

