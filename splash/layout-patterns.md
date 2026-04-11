# Layout Patterns

## Insight Card

Chart on the left, Markdown narrative on the right. The narrative provides analytical commentary — key findings, trends, action items.

**Structure:**
```
Card (title)
  +-- Box (flexDirection: "row", gap: 4)
        +-- Chart (LineChart, BarChart, Histogram, Heatmap, etc.)
        +-- Markdown (analytical narrative)
```

**Browser spec pattern:**
```json
{
  "card": {
    "type": "Card",
    "props": { "title": "Revenue Trend" },
    "children": ["cardRow"]
  },
  "cardRow": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["chart", "narrative"]
  },
  "chart": {
    "type": "LineChart",
    "props": { "data": [12, 19, 25, 30, 38, 45], "width": 50, "height": 10 },
    "children": []
  },
  "narrative": {
    "type": "Markdown",
    "props": { "text": "Revenue grew **18% YoY**.\n\n### Key Drivers\n- **Q4 surge**: +26%\n- Every month outperformed prior year\n\n> On track to cross **$50M/mo** by Q1." },
    "children": []
  }
}
```

**Rules:**
- **Browser**: `flexDirection: "row"` inside Card. Charts at `width: 50, height: 10`.
- **Tmux**: Stack vertically (too narrow for side-by-side). Keep narratives short.
- **Narrative**: Write analytical commentary, not descriptions. Bold metrics, headers, bullet lists, blockquotes.
- **Chart selection**: Use full-sized charts — avoid Sparklines (too small for side-by-side pairing).
- **Multiple cards**: Stack vertically with `flexDirection: "column"` and `gap: 4`.
- **BarChart cards**: Use `flexDirection: "column"` (chart on top, narrative below) instead of row layout. BarCharts need full card width to render readable bars — side-by-side layout compresses them into an unreadable state, especially multi-series grouped bars. Set `width: 80, height: 14-16` for the chart. Keep the narrative as a single flowing paragraph below.

### BarChart Insight Card variant

BarCharts stack vertically — chart on top, narrative below — because grouped bars need full card width.

```json
{
  "card": {
    "type": "Card",
    "props": { "title": "Spend by Department" },
    "children": ["cardCol"]
  },
  "cardCol": {
    "type": "Box",
    "props": { "flexDirection": "column", "gap": 2 },
    "children": ["chart", "narrative"]
  },
  "chart": {
    "type": "BarChart",
    "props": {
      "data": [
        { "quarter": "Q1", "engineering": 820, "marketing": 450 },
        { "quarter": "Q2", "engineering": 880, "marketing": 520 }
      ],
      "categoryKey": "quarter",
      "series": [
        { "dataKey": "engineering", "color": "#3b82f6", "label": "Engineering" },
        { "dataKey": "marketing", "color": "#10b981", "label": "Marketing" }
      ],
      "layout": "vertical",
      "label": "Spend ($K)",
      "width": 80, "height": 14
    },
    "children": []
  },
  "narrative": {
    "type": "Markdown",
    "props": { "text": "Engineering spend grew **24% YoY**. Marketing up **36%** from Q4 campaign push." },
    "children": []
  }
}
```

---

## Drill-Down

Three layers of increasing detail: summary KPIs at top, trend chart in middle, detail table at bottom.

**Structure:**
```
Box (column)
  +-- Heading + subtitle Text
  +-- Box (row) -- Metric cards (3-5 KPIs in individual Cards)
  +-- Card -- full-width trend chart (LineChart, width: 80, height: 14)
  +-- Card -- full-width detail Table (sorted by severity/impact)
```

**Browser spec pattern:**
```json
{
  "dashboard": {
    "type": "Box",
    "props": { "flexDirection": "column", "gap": 4, "padding": 2 },
    "children": ["header", "metricsRow", "chartCard", "tableCard"]
  },
  "metricsRow": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["mc1", "mc2", "mc3", "mc4"]
  },
  "mc1": {
    "type": "Card",
    "props": {},
    "children": ["met1"]
  },
  "met1": {
    "type": "Metric",
    "props": { "label": "Total Requests", "value": "1.24M", "trend": "up", "detail": "+8% vs yesterday" },
    "children": []
  },
  "chartCard": {
    "type": "Card",
    "props": { "title": "Error Volume Over Time" },
    "children": ["chart"]
  },
  "chart": {
    "type": "LineChart",
    "props": { "series": [{"data": [45, 80, 185, 280, 310, 250, 180, 110], "label": "5xx", "color": "#ef4444"}], "width": 80, "height": 14 },
    "children": []
  },
  "tableCard": {
    "type": "Card",
    "props": { "title": "Error Breakdown by Endpoint" },
    "children": ["table"]
  },
  "table": {
    "type": "Table",
    "props": {
      "columns": [{"header": "Endpoint", "key": "endpoint"}, {"header": "Error Rate", "key": "rate"}, {"header": "Status", "key": "status"}],
      "rows": [{"endpoint": "/api/payments", "rate": "12.4%", "status": "Critical"}]
    },
    "children": []
  }
}
```

**Rules:**
- **Metric row**: 3-5 Metrics, each in its own Card. Use `trend` and `detail` props.
- **Trend chart**: Full-width LineChart (`width: 80, height: 14`). Multi-series to overlay related metrics. Use `xLabels` for time axis.
- **Detail table**: Full-width Table sorted by impact/severity. Include status column.
- **Tmux**: Same vertical structure. Reduce chart to `width: 35, height: 8` and trim table columns.

---

## Comparison Grid

Same chart type repeated in a 2x2 grid, each with different data but identical axes. Enables instant visual comparison across categories.

**Structure:**
```
Box (column)
  +-- Heading + subtitle Text
  +-- Box (row) -- [Card A, Card B]
  +-- Box (row) -- [Card C, Card D]
```

Each card:
```
Card (title: category name)
  +-- Chart (same type, same axes across all cards)
  +-- Box (row) -- 2-3 Metric components for key stats
```

**Browser spec pattern:**
```json
{
  "dashboard": {
    "type": "Box",
    "props": { "flexDirection": "column", "gap": 4, "padding": 2 },
    "children": ["header", "row1", "row2"]
  },
  "row1": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["cardA", "cardB"]
  },
  "cardA": {
    "type": "Card",
    "props": { "title": "North America" },
    "children": ["chartA", "metricsA"]
  },
  "chartA": {
    "type": "LineChart",
    "props": {
      "series": [{"data": [120, 145, 170, 195], "label": "MAU", "color": "#3b82f6"}, {"data": [100, 118, 138, 168], "label": "Prior Year", "color": "#3b82f644"}],
      "xLabels": ["Q1", "Q2", "Q3", "Q4"],
      "width": 45, "height": 10
    },
    "children": []
  },
  "metricsA": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["mA1", "mA2"]
  },
  "mA1": {
    "type": "Metric",
    "props": { "label": "Current", "value": "195K", "trend": "up" },
    "children": []
  },
  "mA2": {
    "type": "Metric",
    "props": { "label": "YoY Growth", "value": "+16%", "trend": "up" },
    "children": []
  }
}
```

**Rules:**
- **Consistency**: Every card uses same chart type, same axis ranges, same `xLabels`, same series structure.
- **Color coding**: Each category gets a distinct primary color. Use same color at reduced opacity (e.g. `"#3b82f644"`) for comparison/prior-year series.
- **Metrics below chart**: 2-3 Metric components in a row for key stats.
- **Grid size**: 2x2 ideal. For 3 items use 2+1. For 5+ use 3xN but reduce chart `width` to 35.
- **Tmux**: Stack all cards vertically. Keep chart `width: 35, height: 8`.

---

## Before/After

Two-state comparison showing a metric pre/post a change. Emphasizes the delta with side-by-side charts using identical axes and a verdict summary.

**Structure:**
```
Box (column)
  +-- Heading + subtitle Text (what changed and when)
  +-- Box (row) -- 3-5 Delta Metric cards ("old -> new" with % change)
  +-- Box (row) -- [Card "Before" chart, Card "After" chart]
  +-- Box (row) -- [Card "Before" distribution, Card "After" distribution] (optional)
  +-- Card "Verdict" -- Markdown summary with conclusion
```

**Browser spec pattern:**
```json
{
  "dashboard": {
    "type": "Box",
    "props": { "flexDirection": "column", "gap": 4, "padding": 2 },
    "children": ["header", "deltaRow", "chartsRow", "verdictCard"]
  },
  "deltaRow": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["dc1", "dc2", "dc3"]
  },
  "dc1": {
    "type": "Card",
    "props": {},
    "children": ["d1"]
  },
  "d1": {
    "type": "Metric",
    "props": { "label": "P99 Latency", "value": "342ms -> 85ms", "trend": "down", "detail": "-75%" },
    "children": []
  },
  "chartsRow": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["beforeCard", "afterCard"]
  },
  "beforeCard": {
    "type": "Card",
    "props": { "title": "Before -- Mar 21-27" },
    "children": ["beforeChart"]
  },
  "beforeChart": {
    "type": "LineChart",
    "props": { "data": [85, 145, 250, 342, 230, 120, 88], "width": 45, "height": 12, "color": "#ef4444" },
    "children": []
  },
  "afterCard": {
    "type": "Card",
    "props": { "title": "After -- Mar 29-Apr 4" },
    "children": ["afterChart"]
  },
  "afterChart": {
    "type": "LineChart",
    "props": { "data": [42, 55, 78, 85, 65, 48, 40], "width": 45, "height": 12, "color": "#22c55e" },
    "children": []
  },
  "verdictCard": {
    "type": "Card",
    "props": { "title": "Verdict" },
    "children": ["verdict"]
  },
  "verdict": {
    "type": "Markdown",
    "props": { "text": "### Migration: Success\n\n- **P99 dropped 75%** -- now within SLA\n- **Error rate fell 87%**\n\n> **Recommendation**: Close the project." },
    "children": []
  }
}
```

**Rules:**
- **Delta metrics**: Use `"old -> new"` in `value` with percentage in `detail`. `trend: "down"` where lower is better (latency, errors), `"up"` where higher is better (throughput).
- **Color coding**: Before = red (`#ef4444`), After = green (`#22c55e`). Universal convention.
- **Identical axes**: Same `xLabels`, time granularity, and ideally same Y scale.
- **Optional distribution row**: Side-by-side Histograms when distribution shape matters. Use matching `bins` and colors.
- **Verdict card**: Always end with Markdown verdict and recommendation.
- **Tmux**: Stack vertically. Charts `width: 35, height: 8`. Delta metrics as compact list.
