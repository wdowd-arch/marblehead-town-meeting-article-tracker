# Chart code (reproducible)

These modules let you reproduce the interactive charts (Chart.js) in live updates instead of embedding static PNGs.

## Quick start (plain HTML)

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div style="height:400px">
  <canvas id="insuranceChart"></canvas>
</div>

<script type="module">
  import { renderInsuranceChart } from "./charts/chart-code/insuranceChart.js";
  renderInsuranceChart(document.getElementById("insuranceChart"));
</script>
```

## Available charts
- `insuranceChart.js` → `renderInsuranceChart(canvas)`
- `budgetChart.js` → `renderBudgetChart({ canvas, legendEl?, detailEl? })`
- `overrideChart.js` → `renderOverrideChart(canvas)`

