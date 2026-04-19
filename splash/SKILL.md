---
name: splash
description: Use when needing to visualize data as charts, tables, dashboards, or images in terminal (tmux) or browser. Triggers on data analysis output, metrics to chart, comparisons to visualize, financial OHLC data, distributions, timelines, screenshots, or any data benefiting from visual rendering
---

# Splash

Render visualizations via the `splash` MCP server.

- **Tmux** (`render-tmux`): Braille/block characters in terminal pane. Images via Kitty graphics protocol.
- **Browser** (`render-browser`): Canvas/SVG/HTML at `localhost:3456`. Interactive charts (crosshair, zoom, pan) via TradingView lightweight-charts. Paper-theme log-stream layout: specs accumulate as time-stamped cards in a newest-first stream, with a filterable history rail and a "now rendering" panel.

Use `render-tmux` in tmux for terminal-native output. Use `render-browser` for richer visuals or outside tmux.

## Render Modes (browser)

| `mode` | Effect |
|--------|--------|
| `append` (recommended for multi-spec demos) | Adds a new card to the stream. Previous cards stay. |
| `replace` (default) | Clears all cards, adds one. Use when you want a single snapshot. |
| `clear` | Wipes the stream. No new card. |

The stream is an ephemeral debug scratchpad — pause/clear/filter live in the UI, not the spec. Let the UI handle state; don't try to "update" a prior card by resending with the same `chartId` — `replace` wipes everything, `append` duplicates. To mutate a rendered `LineChart`, use `add-series` (by `chartId`). For other component types, send a new card.

**Make `chartId` descriptive and kebab-case** (e.g. `api-latency`, `requests-by-route`) — it's shown verbatim in the history rail and card headers.

## Spec metadata in the UI

Each rendered card shows: position index · type pill · `chartId` · received time · element count ("N el"). Element count = total keys in `spec.elements`, so a single chart is `1 el` and a `Box` wrapping 4 children is `5 el`. This is useful to know when composing dashboards — if a card shows "1 el" where you expected a dashboard, your root didn't wire `children` correctly.

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
| Progress | `ProgressBar` | 0-1 fraction; paper-themed track + splash fill; percent-readout right-aligned by default |
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
