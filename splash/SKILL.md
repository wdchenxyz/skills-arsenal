---
name: splash
description: Use when needing to visualize data as charts, tables, dashboards, or images in terminal (tmux) or browser. Triggers on data analysis output, metrics to chart, comparisons to visualize, financial OHLC data, distributions, timelines, screenshots, or any data benefiting from visual rendering
---

# Splash

Render visualizations via the `splash` MCP server.

- **Tmux** (`render-tmux`): Braille/block characters in terminal pane. Images via Kitty graphics protocol.
- **Browser** (`render-browser`): Canvas/SVG/HTML at `localhost:3456`. Interactive charts (crosshair, zoom, pan) via TradingView lightweight-charts.

Use `render-tmux` in tmux for terminal-native output. Use `render-browser` for richer visuals or outside tmux.

## Spec Format

Flat element map with root pointer. Compose layouts with `Box` containers (`flexDirection`, `gap`, `padding`) using `children` arrays referencing element IDs.

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "Sparkline",
        "props": { "data": [1, 4, 2, 8, 5], "label": "CPU %" },
        "children": []
      }
    }
  }
}
```

## Component Selection

| Data Type | Component | Notes |
|-----------|-----------|-------|
| Time series (quick) | `Sparkline` | recharts, inline, responsive |
| Time series (detailed) | `LineChart` | Canvas, multi-series, interactive |
| Financial OHLC | `CandlestickChart` | Browser-only |
| Cumulative/utilization | `AreaChart` | Gradient fill, Canvas |
| Deviation/P&L | `BaselineChart` | Green above/red below baseline |
| Distribution | `Histogram` | Canvas, interactive, stats overlay |
| 2D grid/correlation | `Heatmap` | Color matrix |
| Categorical comparison | `BarChart` | recharts, multi-series, horizontal/vertical, tooltips |
| Tabular data | `Table` | columns + rows |
| Single metric | `Metric` | Trend arrow + detail |
| Progress | `ProgressBar` | 0-1 fraction, browser-only |
| Rich text | `Markdown` | Full markdown |
| Image/screenshot | `Image` | Absolute file path |
| Milestones/events | `Timeline` | Browser-only |

See `components.md` for full props reference (also covers KeyValue, Badge, StatusLine, Callout, Link, List, Spinner, and more).

## Additional Tools

- **`add-series`**: Append a data series to an existing `LineChart` (by `chartId` or last rendered). Params: `data` (number[]), `label?`, `color?`, `fill?`.
- **`close-tmux`** / **`close-browser`**: Tear down renderers.

## Reference Files

- **components.md** — Full component props reference
- **examples.md** — Complete JSON spec examples for every component
- **sizing.md** — Sizing guidelines for tmux and browser, row pairing rules
- **layout-patterns.md** — Composite layouts: Insight Card, Drill-Down, Comparison Grid, Before/After
- **datafile.md** — Load data from JSON/CSV/TSV files instead of inline data
