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
| `Image` | `src: string (absolute path to local file), alt?: string, width?: number, height?: number` |

**Image rendering details:**
- `src` must be an absolute file path (e.g. `/tmp/screenshot.png`). Supported formats: PNG, JPEG, GIF, WebP, SVG.
- **Browser:** The MCP server rewrites `src` to an HTTP URL served by a built-in `/files/` endpoint. Renders as `<img>`.
- **Tmux:** Uses Kitty graphics protocol with Unicode placeholders. `width`/`height` are in terminal cell units (default: 40x15). Requires Ghostty or Kitty terminal with `tmux set -g allow-passthrough all`.
- Images compose freely with all other components in the same spec.

### Data Visualization
| Component | Key Props |
|-----------|-----------|
| `Sparkline` | `data: number[], width?: number, label?: string, color?: string, min?: number, max?: number` |
| `LineChart` | `data?: number[], series?: {data: number[], label?: string, color?: string, fill?: boolean}[], width?: number, height?: number, label?: string, color?: string, showAxis?: boolean (default true), fill?: boolean` |
| `Histogram` | `data: number[], bins?: number (default 15), width?: number, label?: string, color?: string, showValues?: boolean (default true)` |
| `Heatmap` | `data: number[][], xLabels?: string[], yLabels?: string[], label?: string, color?: string ("green"\|"red"\|"blue"\|"yellow"\|"cyan"\|"magenta"\|"white"), showValues?: boolean (default false), cellWidth?: number` |
| `BarChart` | `data: {label: string, value: number}[], width?: number` |
| `Table` | `columns: {header: string, key: string, width?: number, align?: string}[], rows: Record<string, string>[]` |
| `ProgressBar` | `progress: number (0-1), label?: string, width?: number` |
| `Metric` | `label: string, value: string\|number, trend?: "up"\|"down", detail?: string` |

### Layout
| Component | Key Props |
|-----------|-----------|
| `Box` | `flexDirection, padding, gap, borderStyle` |
| `Card` | `title?: string, children` |
| `Heading` | `level: "h1"\|"h2"\|"h3"\|"h4", text: string` |
| `Divider` | `title?: string` |
| `Spacer` | (no props) |
| `Newline` | (no props) |

### Content
| Component | Key Props |
|-----------|-----------|
| `Text` | `text: string` |
| `Badge` | `label: string, variant?: "default"\|"success"\|"warning"\|"error"` |
| `KeyValue` | `label: string, value: string, separator?: string` |
| `List` | `items: string[], ordered?: boolean` |
| `ListItem` | `title: string, subtitle?: string` |
| `StatusLine` | `status: "info"\|"success"\|"warning"\|"error", text: string` |
| `Link` | `url: string, label?: string` |
| `Markdown` | `text: string` |
| `Callout` | `type?: string, content: string, title?: string` |
| `Timeline` | `items: {title, description?, date?, status?}[]` |
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

### Line Chart (multi-series)
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

### Browser (`render-browser`)
The browser page is full-width. SVG charts scale to fill available space automatically. Use larger sizes:
- **LineChart**: `width: 60`–`80`, `height: 12`–`16`
- **Histogram**: `width: 40`–`60`
- **Heatmap**: `cellWidth: 5`–`8`
- Side-by-side layouts work well with `flexDirection: "row"` and `gap: 4`.
- Colors use hex values (e.g. `"#22c55e"`) for best results.

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
