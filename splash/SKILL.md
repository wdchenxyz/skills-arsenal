---
name: splash
description: Render data visualizations (charts, tables, dashboards) and images in a tmux pane or browser page using json-render specs via MCP
---

# Splash

Render data visualizations using the `splash` MCP server. Two rendering targets:

- **Terminal (tmux):** Braille/block character rendering in a tmux split pane. Requires tmux session. Images rendered via Kitty graphics protocol with Unicode placeholders (works in Ghostty/Kitty + tmux).
- **Browser:** SVG/HTML rendering at `localhost:3456`. Works in any environment. Local images served via built-in file endpoint.

## MCP Tools

### `render-tmux`
Renders a json-render spec in a tmux pane.

Parameters:
- `spec` (required): `{ root: string, elements: Record<string, Element> }`
- `state` (optional): Dynamic state values referenced by `$state` in the spec
- `title` (optional): Display title for the pane
- `position` (optional): `"right"` (default) or `"bottom"`
- `size` (optional): Pane size as percentage (default: 40)
- `mode` (optional): `"replace"` (default), `"append"`, or `"clear"`
- `chartId` (optional): ID for targeting with `add-series` later

### `render-browser`
Renders a json-render spec in a browser page at `localhost:3456`. Auto-opens the browser on first call. Supports page refresh (replays last spec).

Parameters:
- `spec` (required): `{ root: string, elements: Record<string, Element> }`
- `state` (optional): Dynamic state values referenced by `$state` in the spec
- `title` (optional): Title for the visualization
- `mode` (optional): `"replace"` (default), `"append"`, or `"clear"`
- `chartId` (optional): ID for targeting with `add-series` later

### `add-series`
Adds a data series to an existing LineChart. Broadcasts to **all active renderers** (tmux and browser simultaneously).

Parameters:
- `chartId` (optional): Element ID of the LineChart. If omitted, targets the last rendered chart.
- `data` (required): `number[]` — data points for the new series
- `label` (optional): Legend label
- `color` (optional): Series color (e.g. `"cyan"`, `"#ef4444"`)
- `fill` (optional): Whether to fill below the line

### `close-tmux`
Closes the tmux rendering pane. No parameters.

### `close-browser`
Stops the browser rendering server. No parameters.

## Choosing a Renderer

| Scenario | Use |
|----------|-----|
| Running in tmux, want terminal-native rendering | `render-tmux` |
| Not in tmux, or want richer SVG visuals | `render-browser` |
| Want to display on both simultaneously | Call both, then use `add-series` to update both at once |

## Spec Format

A flat map of elements with a root pointer:

```json
{
  "root": "dashboard",
  "elements": {
    "dashboard": {
      "type": "Box",
      "props": { "flexDirection": "column" },
      "children": ["title", "chart"]
    },
    "title": {
      "type": "Heading",
      "props": { "text": "My Dashboard", "level": "h1" },
      "children": []
    },
    "chart": {
      "type": "Sparkline",
      "props": { "data": [1, 4, 2, 8, 5, 3, 7], "label": "Requests/sec" },
      "children": []
    }
  }
}
```

## Available Components

### Browser-Only: shadcn Components

The browser renderer uses `@json-render/shadcn` for Card, Heading, Badge, Table, Spinner, and ProgressBar — providing polished Tailwind-styled UI. These render identically to the tmux versions from the spec's perspective (same props), but look better in the browser.

30 additional shadcn components are available but not yet registered. See `docs/shadcn-components.md` in the project for the full list (Tabs, Dialog, Input, Select, Accordion, Alert, etc.). To add one, register it in `src/app/index.tsx`:

```ts
Tabs: shadcnComponents.Tabs,
```

If prop names differ from Splash conventions, add an adapter in `src/app/components/shadcn-adapters.tsx`.

### Images
| Component | Key Props |
|-----------|-----------|
| `Image` | `src: string (absolute path to local file), alt?: string, width?: number, height?: number, background?: string (wraps image with bg color, useful for transparent PNGs on dark themes)` |

**Image rendering details:**
- `src` must be an absolute file path (e.g. `/tmp/screenshot.png`). Supported formats: PNG, JPEG, GIF, WebP, SVG.
- **Browser:** The MCP server rewrites `src` to an HTTP URL served by a built-in `/files/` endpoint. Renders as `<img>`.
- **Tmux:** Uses Kitty graphics protocol with Unicode placeholders. `width`/`height` are in terminal cell units (default: 40x15). Requires Ghostty or Kitty terminal with `tmux set -g allow-passthrough all`.
- Images compose freely with all other components in the same spec.

### Data Visualization
| Component | Key Props |
|-----------|-----------|
| `Sparkline` | `data: number[], width?: number, label?: string, color?: string, min?: number, max?: number` |
| `LineChart` | `data?: number[], series?: {data: number[], label?: string, color?: string, fill?: boolean}[], width?: number, height?: number, label?: string, color?: string, showAxis?: boolean (default true), fill?: boolean, xLabels?: string[]` |
| `Histogram` | `data: number[], bins?: number (default 15), width?: number, height?: number, label?: string, color?: string, showValues?: boolean (default true)` |
| `Heatmap` | `data: number[][], xLabels?: string[], yLabels?: string[], label?: string, color?: string ("green"\|"red"\|"blue"\|"yellow"\|"cyan"\|"magenta"\|"white"), showValues?: boolean (default false), cellWidth?: number` |
| `BarChart` | `data: {label: string, value: number, color?: string}[], width?: number, showValues?: boolean (default true), showPercentage?: boolean (default false)` |
| `Table` | `columns: {header: string, key: string, width?: number, align?: string}[], rows: Record<string, string>[]` |
| `ProgressBar` | `progress: number (0-1), label?: string, width?: number, value?: number (0-100, bypasses fraction conversion), max?: number (default 100)` |
| `Metric` | `label: string, value: string\|number, trend?: "up"\|"down"\|"neutral", detail?: string` |

### Layout
| Component | Key Props |
|-----------|-----------|
| `Box` | `flexDirection, padding, gap, borderStyle, justifyContent, alignItems, flexGrow, flexShrink, flexWrap, width, height, backgroundColor, borderColor` |
| `Card` | `title?: string, children` |
| `Heading` | `level: "h1"\|"h2"\|"h3"\|"h4", text: string` |
| `Divider` | `title?: string, color?: string` |
| `Spacer` | (no props) |
| `Newline` | `count?: number` |

### Content
| Component | Key Props |
|-----------|-----------|
| `Text` | `text: string, color?: string, backgroundColor?: string, bold?: boolean, italic?: boolean, underline?: boolean, strikethrough?: boolean, dimColor?: boolean` |
| `Badge` | `label: string, variant?: "default"\|"success"\|"warning"\|"error"` |
| `KeyValue` | `label: string, value: string\|string[], separator?: string, labelColor?: string` |
| `List` | `items: string[], ordered?: boolean, bulletChar?: string` |
| `ListItem` | `title: string, subtitle?: string, leading?: string, trailing?: string` |
| `StatusLine` | `status: "info"\|"success"\|"warning"\|"error", text: string, icon?: string` |
| `Link` | `url: string, label?: string, color?: string` |
| `Markdown` | `text: string` |
| `Callout` | `type?: string, content: string, title?: string` |
| `Timeline` | `items: {title, description?, date?, status?}[]` — or use `dataFile` with column hints (see dataFile section). Status values: `done`/`completed` (filled circle), `pending`/`upcoming` (hollow circle), `current`/`active`/`in-progress` (blue). Browser only. |
| `Spinner` | `label?: string` |

## Example Specs

### Sparkline
```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "Sparkline",
        "props": { "data": [1, 4, 2, 8, 5, 3, 7], "label": "CPU %" },
        "children": []
      }
    }
  }
}
```

### Bar Chart
```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "BarChart",
        "props": {
          "data": [
            { "label": "api", "value": 45 },
            { "label": "web", "value": 30 },
            { "label": "worker", "value": 78 }
          ]
        },
        "children": []
      }
    }
  }
}
```

### Table
```json
{
  "spec": {
    "root": "table",
    "elements": {
      "table": {
        "type": "Table",
        "props": {
          "columns": [
            { "header": "Service", "key": "service" },
            { "header": "Status", "key": "status" },
            { "header": "Latency", "key": "latency" }
          ],
          "rows": [
            { "service": "api", "status": "healthy", "latency": "45ms" },
            { "service": "web", "status": "degraded", "latency": "120ms" },
            { "service": "db", "status": "healthy", "latency": "12ms" }
          ]
        },
        "children": []
      }
    }
  }
}
```

### Line Chart (single series)
```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "LineChart",
        "props": { "data": [10, 25, 18, 30, 22, 35, 28, 40], "label": "Latency (ms)", "width": 35, "height": 8 },
        "children": []
      }
    }
  }
}
```

### Line Chart (multi-series with xLabels)
```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "LineChart",
        "props": {
          "label": "CPU vs Memory",
          "series": [
            { "data": [10, 25, 30, 45, 38, 42], "label": "CPU %", "color": "green" },
            { "data": [55, 50, 60, 58, 65, 70], "label": "Memory %", "color": "cyan" }
          ],
          "xLabels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          "width": 35,
          "height": 8
        },
        "children": []
      }
    }
  }
}
```

### Histogram
```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "Histogram",
        "props": {
          "data": [12, 15, 14, 18, 22, 19, 25, 30, 28, 35, 33, 40, 38, 42, 45],
          "label": "Response Time Distribution",
          "bins": 10,
          "width": 30
        },
        "children": []
      }
    }
  }
}
```

### Heatmap
```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "Heatmap",
        "props": {
          "data": [
            [1, 3, 5, 7, 9],
            [2, 4, 6, 8, 10],
            [9, 7, 5, 3, 1]
          ],
          "xLabels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
          "yLabels": ["Morning", "Afternoon", "Evening"],
          "label": "Request Volume",
          "color": "green",
          "showValues": true
        },
        "children": []
      }
    }
  }
}
```

### Timeline (inline)
```json
{
  "spec": {
    "root": "timeline",
    "elements": {
      "timeline": {
        "type": "Timeline",
        "props": {
          "items": [
            { "title": "Project Kickoff", "date": "2026-01-15", "status": "done", "description": "Team aligned on goals" },
            { "title": "Alpha Release", "date": "2026-03-01", "status": "done", "description": "Internal testing" },
            { "title": "Beta Release", "date": "2026-04-01", "status": "current", "description": "External testers" },
            { "title": "GA Launch", "date": "2026-05-15", "status": "pending" }
          ]
        },
        "children": []
      }
    }
  }
}
```

### Image
```json
{
  "spec": {
    "root": "img",
    "elements": {
      "img": {
        "type": "Image",
        "props": { "src": "/path/to/screenshot.png", "alt": "Screenshot" },
        "children": []
      }
    }
  }
}
```

### Image + Chart (mixed content)
```json
{
  "spec": {
    "root": "layout",
    "elements": {
      "layout": {
        "type": "Box",
        "props": { "flexDirection": "column" },
        "children": ["img", "chart"]
      },
      "img": {
        "type": "Image",
        "props": { "src": "/tmp/debug-screenshot.png", "alt": "Debug capture", "width": 30, "height": 8 },
        "children": []
      },
      "chart": {
        "type": "LineChart",
        "props": { "data": [3, 7, 2, 9, 4, 6], "label": "Errors/min" },
        "children": []
      }
    }
  }
}
```

### Multi-Widget Dashboard
```json
{
  "spec": {
    "root": "dashboard",
    "elements": {
      "dashboard": {
        "type": "Box",
        "props": { "flexDirection": "column" },
        "children": ["header", "chart", "status"]
      },
      "header": {
        "type": "Heading",
        "props": { "text": "Service Dashboard", "level": "h1" },
        "children": []
      },
      "chart": {
        "type": "LineChart",
        "props": {
          "data": [10, 15, 12, 18, 22, 19, 25, 30],
          "label": "Requests/min",
          "width": 35,
          "height": 8
        },
        "children": []
      },
      "status": {
        "type": "Box",
        "props": { "flexDirection": "column" },
        "children": ["s1", "s2"]
      },
      "s1": {
        "type": "StatusLine",
        "props": { "status": "success", "text": "API: healthy" },
        "children": []
      },
      "s2": {
        "type": "StatusLine",
        "props": { "status": "warning", "text": "Cache: high latency" },
        "children": []
      }
    }
  }
}
```

## Sizing Best Practices

### tmux (`render-tmux`)
The tmux pane has limited width (~40-50 columns at 40% split). Use **vertical layout** (`flexDirection: "column"`) and conservative sizes:
- **Sparkline**: `width: 30`–`40`
- **LineChart**: `width: 30`–`40`, `height: 6`–`10`
- **Histogram**: `width: 25`–`35`
- **Heatmap**: `cellWidth: 2`–`3`
- **BarChart**: Keep labels short, `width: 25`–`35`
- Avoid side-by-side (`flexDirection: "row"`) layouts — they overflow in narrow panes. Stack elements vertically instead.
- **xLabels in tmux**: Keep labels short (3-4 chars like "0h", "Q1", "Mon") — long labels overlap in narrow panes. Fewer labels is better than crowded labels.

### Browser (`render-browser`)
SVG charts are capped at their viewBox width (`width` prop × 8 pixels) and scale down responsively. The `width` prop controls the maximum rendered size — use it to control chart proportions.

**Single chart (full focus):**
- **LineChart**: `width: 60`–`80`, `height: 12`–`16`
- **Histogram**: `width: 40`–`60`
- **Heatmap**: `cellWidth: 5`–`8`

**Multi-chart dashboard (3+ visualizations):**
- **LineChart**: `width: 40`–`50`, `height: 8`–`12`
- **Histogram**: `width: 40`–`50`
- **Heatmap**: `cellWidth: 3`–`5`
- **Sparkline**: `width: 30`–`40`
- **BarChart**: `width: 35`–`45`
- Use `flexDirection: "column"` as the outer layout, with row sub-groups for pairing charts

**Row pairing rules (IMPORTANT):**
- Only pair components with **similar visual height** in a row. Good pairs:
  - LineChart + BarChart (both vertically compact)
  - Histogram + Heatmap (both medium height)
  - Two LineCharts or two BarCharts
- **Never** put these in a row:
  - Sparklines + Table (extreme size mismatch)
  - Sparklines + any full chart (sparklines are too small)
  - Table + any chart (tables grow with content, unpredictable width)
- **Tables** should always be in full-width column layout, never in a row with other components
- **Sparklines** work best stacked vertically as a group, or inline with Metric/KeyValue components — not paired with charts
- Match `height` props when pairing two SVG charts in a row (e.g. both `height: 10`)

**Layout tips:**
- Side-by-side layouts work well with `flexDirection: "row"` and `gap: 4`
- SVG charts are capped at their maxWidth and won't stretch beyond it
- BarChart is also capped — its `width` prop × 6 = max pixels
- Colors use hex values (e.g. `"#22c55e"`) for best results

**Data tips:**
- **BarChart**: Ensure data values have meaningful variation. If all values are near-identical (e.g. 99.7, 99.8, 99.9), bars will look identical — use a different chart or show the delta instead
- **xLabels**: The number of labels should match the visual density. 6 labels for 12 data points is fine; 12 labels for 12 points may crowd the axis

## When to Use Which Component

| Data Type | Best Component |
|-----------|---------------|
| Time series (quick, inline) | `Sparkline` |
| Time series (detailed, multi-series) | `LineChart` |
| Distribution of values | `Histogram` |
| 2D grid / correlation matrix | `Heatmap` |
| Categorical comparisons | `BarChart` |
| Tabular data (object rows) | `Table` |
| Key-value pairs | `KeyValue` |
| Single metric | `Metric` |
| Progress/percentage | `ProgressBar` |
| Status overview | `StatusLine` |
| Rich text | `Markdown` |
| Local image / screenshot | `Image` |
| Milestones / events / changelog | `Timeline` |

## `dataFile` Support

Instead of inline data, components can load data from JSON, CSV, or TSV files using the `dataFile` prop. The resolver parses the file and injects the appropriate props.

### Supported Components

| Component | `dataFile` produces | Column hint props |
|-----------|--------------------|--------------------|
| `LineChart`, `Sparkline`, `Histogram` | `data: number[]` | `dataColumn` (which numeric column), `xLabelsColumn` |
| `BarChart` | `data: [{label, value}]` | `labelColumn`, `valueColumn` |
| `Table` | `columns` + `rows` | (auto-detected from headers) |
| `Heatmap` | `data: number[][]` | (JSON 2D array only) |
| `Timeline` | `items: [{title, description?, date?, status?}]` | `titleColumn`, `descriptionColumn`, `dateColumn`, `statusColumn` |

### Auto-detection
- **Numeric columns**: Auto-detected from both JSON numbers and numeric strings in CSV/TSV (e.g. `"45"` is treated as numeric)
- **BarChart**: Auto-detects the first string column as label, first numeric column as value
- **Timeline**: Auto-detects the first string column as title; other columns require explicit hints

### Example — Timeline from CSV
```json
{
  "spec": {
    "root": "t",
    "elements": {
      "t": {
        "type": "Timeline",
        "props": {
          "dataFile": "/tmp/milestones.csv",
          "dateColumn": "date",
          "statusColumn": "status",
          "descriptionColumn": "description"
        },
        "children": []
      }
    }
  }
}
```

Where `/tmp/milestones.csv`:
```
title,date,status,description
Project Kickoff,2026-01-15,done,Initial team alignment
Design Review,2026-02-01,done,UI/UX approval
Beta Release,2026-04-01,pending,External testers
```

### Example — LineChart from CSV
```json
{
  "spec": {
    "root": "c",
    "elements": {
      "c": {
        "type": "LineChart",
        "props": { "dataFile": "/tmp/metrics.csv", "dataColumn": "latency", "xLabelsColumn": "date" },
        "children": []
      }
    }
  }
}
```

## Layout Patterns

### Insight Card

When the user requests an "Insight Card" layout, render each visualization inside a Card with a two-column layout: chart on the left, Markdown narrative on the right. The narrative should provide analytical commentary — key findings, trends, action items — using rich Markdown (headers, bold metrics, bullet lists, blockquotes).

**Structure per card:**
```
Card (title)
  └── Box (flexDirection: "row", gap: 4)
        ├── Chart (LineChart, BarChart, Histogram, Heatmap, etc.)
        └── Markdown (analytical narrative)
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
- **Browser**: Use `flexDirection: "row"` inside the Card to place chart and narrative side-by-side. Size charts at `width: 50, height: 10` for good proportions.
- **Tmux**: Stack chart and narrative vertically (tmux is too narrow for side-by-side). Keep narratives short (1-2 sentences).
- **Narrative content**: Write analytical commentary, not descriptions. Include bold metrics, headers for sections, bullet lists for breakdowns, and blockquotes for recommendations/actions.
- **Chart selection**: Use full-sized charts (LineChart, BarChart, Histogram, Heatmap) — avoid Sparklines which are too small for side-by-side pairing with text.
- **Multiple Insight Cards**: Stack cards vertically with `flexDirection: "column"` and `gap: 4` on the outer container.

### Drill-Down

When the user requests a "Drill-Down" layout, render three layers of increasing detail stacked vertically: summary metrics at the top, a trend chart in the middle, and a detailed table at the bottom. The flow guides the eye from glanceable KPIs → shape of the problem → root cause data.

**Structure:**
```
Box (column)
  ├── Heading + subtitle Text
  ├── Box (row) — Metric cards (3-5 KPIs in individual Cards)
  ├── Card — full-width trend chart (LineChart, width: 80, height: 14)
  └── Card — full-width detail Table (sorted by severity/impact)
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
- **Metric row**: 3-5 Metric components, each wrapped in its own Card. Use `trend` and `detail` props to show direction and context (e.g. "Target: <1%").
- **Trend chart**: Full-width LineChart (`width: 80, height: 14`). Use multi-series to overlay related metrics (e.g. 5xx + 4xx + total). Use `xLabels` for time axis.
- **Detail table**: Full-width Table sorted by impact/severity. Include a status column with visual indicators (e.g. "⚠ Critical", "△ Medium", "✓ OK").
- **Tmux**: Same vertical structure works naturally. Reduce chart to `width: 35, height: 8` and trim table columns to fit.

### Comparison Grid

When the user requests a "Comparison Grid" layout, render the same chart type repeated in a 2×2 (or 2×N) grid, each with different data but identical axes and structure. This enables instant visual comparison across categories.

**Structure:**
```
Box (column)
  ├── Heading + subtitle Text
  ├── Box (row) — [Card A, Card B]
  └── Box (row) — [Card C, Card D]
```

Each card contains:
```
Card (title: category name)
  ├── Chart (same type, same axes across all cards)
  └── Box (row) — 2-3 Metric components for key stats
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
- **Consistency is key**: Every card must use the same chart type, same axis ranges, same `xLabels`, and same series structure (e.g. current + prior year). This allows the eye to compare shapes, not decode different formats.
- **Color coding**: Assign each category a distinct primary color. Use the same color at reduced opacity (e.g. `"#3b82f644"`) for the comparison/prior-year series.
- **Metrics below chart**: 2-3 Metric components in a row below each chart for key stats (e.g. current value, growth rate, churn).
- **Grid size**: 2×2 is ideal. For 3 items use a 2+1 layout. For 5+ consider 3×N but reduce chart `width` to 35.
- **Tmux**: Stack all cards vertically. Keep chart `width: 35, height: 8` and abbreviate labels.

### Before/After

When the user requests a "Before/After" layout, render a focused two-state comparison showing a metric pre/post a change (deploy, migration, experiment). The layout emphasizes the delta with side-by-side charts using identical axes and a verdict summary.

**Structure:**
```
Box (column)
  ├── Heading + subtitle Text (what changed and when)
  ├── Box (row) — 3-5 Delta Metric cards (showing "old → new" with % change)
  ├── Box (row) — [Card "Before" chart, Card "After" chart] (same chart type, same axes)
  ├── Box (row) — [Card "Before" distribution, Card "After" distribution] (optional, for shape comparison)
  └── Card "Verdict" — Markdown summary with conclusion and recommendation
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
    "props": { "label": "P99 Latency", "value": "342ms → 85ms", "trend": "down", "detail": "-75%" },
    "children": []
  },
  "chartsRow": {
    "type": "Box",
    "props": { "flexDirection": "row", "gap": 4 },
    "children": ["beforeCard", "afterCard"]
  },
  "beforeCard": {
    "type": "Card",
    "props": { "title": "Before — Mar 21–27" },
    "children": ["beforeChart"]
  },
  "beforeChart": {
    "type": "LineChart",
    "props": { "data": [85, 145, 250, 342, 230, 120, 88], "width": 45, "height": 12, "color": "#ef4444" },
    "children": []
  },
  "afterCard": {
    "type": "Card",
    "props": { "title": "After — Mar 29–Apr 4" },
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
    "props": { "text": "### Migration: Success\n\n- **P99 dropped 75%** — now within SLA\n- **Error rate fell 87%**\n\n> **Recommendation**: Close the project." },
    "children": []
  }
}
```

**Rules:**
- **Delta metrics**: Use `"old → new"` format in the `value` prop with percentage change in `detail`. Use `trend: "down"` for metrics where lower is better (latency, errors) and `trend: "up"` where higher is better (throughput).
- **Color coding**: Before = red/warm (`#ef4444`), After = green/cool (`#22c55e`). This convention is universal — don't swap it.
- **Identical axes**: Both charts must use the same `xLabels`, same time granularity, and ideally the same Y scale so shapes are directly comparable.
- **Optional distribution row**: Add side-by-side Histograms when the *shape* of the distribution matters (e.g. long tail elimination). Use matching `bins` count and colors.
- **Verdict card**: Always end with a Markdown verdict — was the change a success? Include a recommendation for next steps.
- **Tmux**: Stack all sections vertically. Use `width: 35, height: 8` for charts. Keep delta metrics as a compact list instead of a row of cards.

## Dynamic State

Use `$state` references for dynamic values:

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "Sparkline",
        "props": {
          "data": { "$state": "/metrics/cpu" },
          "label": "CPU %"
        },
        "children": []
      }
    }
  },
  "state": {
    "metrics": {
      "cpu": [10, 25, 30, 45, 38, 42]
    }
  }
}
```
