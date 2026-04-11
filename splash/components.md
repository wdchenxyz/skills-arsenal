# Component Props Reference

## Interactive Canvas Charts (browser — TradingView lightweight-charts)

These render with HTML5 Canvas in the browser and support **interactive crosshair**, **zoom** (mouse wheel), and **pan** (click+drag). In tmux, AreaChart and BaselineChart fall back to LineChart; CandlestickChart and Histogram have no tmux fallback.

| Component | Key Props |
|-----------|-----------|
| `LineChart` | `data?: number[], series?: {data: number[], label?: string, color?: string, fill?: boolean}[], width?, height?, label?, color?, showAxis? (default true), fill?`. Multi-series via `series` array. |
| `CandlestickChart` | `data: {time: string\|number, open: number, high: number, low: number, close: number}[], width?, height?, label?, upColor? (default "#22c55e"), downColor? (default "#ef4444")`. **Browser-only.** |
| `AreaChart` | `data: number[] \| {time: string\|number, value: number}[], width?, height?, label?, color?, lineColor?`. Gradient fill below line. Tmux: falls back to LineChart. |
| `BaselineChart` | `data: number[] \| {time: string\|number, value: number}[], width?, height?, label?, baseValue? (default: mean), topLineColor? (default "#22c55e"), bottomLineColor? (default "#ef4444")`. Green above baseline, red below. Tmux: falls back to LineChart. |
| `Histogram` | `data: number[], bins? (default 15), width?, height?, label?, color?, showValues? (default true)`. Vertical bars, interactive crosshair. **Browser-only.** |

## Recharts Charts (browser — recharts + shadcn chart primitives)

Interactive SVG charts with tooltips, rendered via recharts wrapped in shadcn `ChartContainer`. Browser-only.

| Component | Key Props |
|-----------|-----------|
| `BarChart` | `data: Record<string, unknown>[], categoryKey?: string, series?: {dataKey: string, color?: string, label?: string}[], layout? ("horizontal"\|"vertical", default "horizontal"), label?, showTooltip? (default true), width?, height?`. Multi-series auto-detected from data keys. `layout: "horizontal"` = horizontal bars, `"vertical"` = vertical bars. Colors default to `var(--chart-1)` through `var(--chart-5)`. |
| `Sparkline` | `data: number[], width?, label?, color?, min?, max?`. Compact inline chart, no axes/grid/tooltip. |

## Static SVG Charts (browser and tmux)

| Component | Key Props |
|-----------|-----------|
| `Heatmap` | `data: number[][], xLabels?: string[], yLabels?: string[], label?, color? ("green"\|"red"\|"blue"\|"yellow"\|"cyan"\|"magenta"\|"white"), showValues? (default false), cellWidth?` |

## Data Display

| Component | Key Props |
|-----------|-----------|
| `Table` | `columns: {header: string, key: string, width?, align?}[], rows: Record<string, string>[]` |
| `ProgressBar` | `progress: number (0-1), label?, width?, value? (0-100, bypasses fraction conversion), max? (default 100)`. **Browser-only** (shadcn adapter). |
| `Metric` | `label: string, value: string\|number, trend?: "up"\|"down"\|"neutral", detail?: string` |

## Images

| Component | Key Props |
|-----------|-----------|
| `Image` | `src: string (absolute path), alt?, width?, height?, background? (bg color for transparent PNGs)` |

- `src` must be an absolute file path (e.g. `/tmp/screenshot.png`). Supported: PNG, JPEG, GIF, WebP, SVG.
- **Browser**: Rewrites `src` to HTTP URL via built-in `/files/` endpoint. Renders as `<img>`.
- **Tmux**: Kitty graphics protocol with Unicode placeholders. `width`/`height` in terminal cells (default: 40x15). Requires Ghostty/Kitty + `tmux set -g allow-passthrough all`.
- Images compose freely with all other components.

## Layout

| Component | Key Props |
|-----------|-----------|
| `Box` | `flexDirection, padding, gap, borderStyle, justifyContent, alignItems, flexGrow, flexShrink, flexWrap, width, height, backgroundColor, borderColor` |
| `Card` | `title?: string, children` |
| `Heading` | `level: "h1"\|"h2"\|"h3"\|"h4", text: string` |
| `Divider` | `title?, color?` |
| `Spacer` | (no props) |
| `Newline` | `count?: number` |

## Content

| Component | Key Props |
|-----------|-----------|
| `Text` | `text: string, color?, backgroundColor?, bold?, italic?, underline?, strikethrough?, dimColor?` |
| `Badge` | `label: string, variant?: "default"\|"success"\|"warning"\|"error"` |
| `KeyValue` | `label: string, value: string\|string[], separator?, labelColor?` |
| `List` | `items: string[], ordered?, bulletChar?` |
| `ListItem` | `title: string, subtitle?, leading?, trailing?` |
| `StatusLine` | `status: "info"\|"success"\|"warning"\|"error", text: string, icon?` |
| `Link` | `url: string, label?, color?` |
| `Markdown` | `text: string` |
| `Callout` | `type?, content: string, title?` |
| `Timeline` | `items: {title, description?, date?, status?}[]`. Status: `done`/`completed` (filled), `pending`/`upcoming` (hollow), `current`/`active`/`in-progress` (blue). Browser-only. Also supports `dataFile` (see datafile.md). |
| `Spinner` | `label?: string` |

## Browser-Only: shadcn Components

The browser renderer uses `@json-render/shadcn` for Card, Heading, Badge, Table, Spinner, and ProgressBar — polished Tailwind-styled UI. Same props as tmux versions.

30 additional shadcn components are available but not yet registered. See `docs/shadcn-components.md` in the project for the full list (Tabs, Dialog, Input, Select, Accordion, Alert, etc.). To add one, register it in `src/app/index.tsx`:

```ts
Tabs: shadcnComponents.Tabs,
```

If prop names differ from Splash conventions, add an adapter in `src/app/components/shadcn-adapters.tsx`.

## Dynamic State

Use `$state` references for dynamic values. Pass a `state` object alongside `spec`:

```json
{
  "spec": {
    "root": "c",
    "elements": {
      "c": {
        "type": "Sparkline",
        "props": { "data": { "$state": "/metrics/cpu" }, "label": "CPU %" },
        "children": []
      }
    }
  },
  "state": { "metrics": { "cpu": [10, 25, 30, 45] } }
}
```
