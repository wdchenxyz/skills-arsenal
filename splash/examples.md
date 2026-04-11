# Example Specs

## Sparkline

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

## BarChart (single-series, horizontal bars)

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "BarChart",
        "props": {
          "data": [
            { "service": "API Gateway", "latency": 45 },
            { "service": "Web Server", "latency": 30 },
            { "service": "Database", "latency": 12 }
          ],
          "categoryKey": "service",
          "label": "Service Latency (ms)"
        },
        "children": []
      }
    }
  }
}
```

## BarChart (multi-series, vertical bars)

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "BarChart",
        "props": {
          "data": [
            { "month": "Jan", "desktop": 186, "mobile": 80 },
            { "month": "Feb", "desktop": 305, "mobile": 200 },
            { "month": "Mar", "desktop": 237, "mobile": 120 }
          ],
          "categoryKey": "month",
          "series": [
            { "dataKey": "desktop", "color": "var(--chart-1)", "label": "Desktop" },
            { "dataKey": "mobile", "color": "var(--chart-2)", "label": "Mobile" }
          ],
          "layout": "vertical",
          "label": "Monthly Traffic"
        },
        "children": []
      }
    }
  }
}
```

## Table

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

## LineChart (single series)

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

## LineChart (multi-series with xLabels)

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

## Histogram

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

## CandlestickChart (browser-only)

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "CandlestickChart",
        "props": {
          "label": "AAPL Daily",
          "data": [
            {"time": "2024-01-02", "open": 185.33, "high": 186.10, "low": 183.79, "close": 185.64},
            {"time": "2024-01-03", "open": 184.22, "high": 185.88, "low": 183.43, "close": 184.25},
            {"time": "2024-01-04", "open": 182.15, "high": 183.09, "low": 180.88, "close": 181.91},
            {"time": "2024-01-05", "open": 181.99, "high": 182.76, "low": 180.17, "close": 181.18},
            {"time": "2024-01-08", "open": 182.09, "high": 185.60, "low": 181.50, "close": 185.56}
          ],
          "width": 60, "height": 14
        },
        "children": []
      }
    }
  }
}
```

## AreaChart (simple)

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "AreaChart",
        "props": {
          "label": "Memory Usage (GB)",
          "data": [12.4, 13.1, 12.8, 14.2, 15.6, 14.8, 13.5, 14.1, 15.2, 16.8],
          "color": "#06b6d4",
          "width": 60, "height": 12
        },
        "children": []
      }
    }
  }
}
```

## AreaChart (time-series data)

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "AreaChart",
        "props": {
          "label": "Revenue ($M)",
          "data": [
            {"time": "2026-01-01", "value": 10.1},
            {"time": "2026-02-01", "value": 11.3},
            {"time": "2026-03-01", "value": 12.8}
          ],
          "color": "#3b82f6",
          "width": 60, "height": 12
        },
        "children": []
      }
    }
  }
}
```

## BaselineChart

```json
{
  "spec": {
    "root": "chart",
    "elements": {
      "chart": {
        "type": "BaselineChart",
        "props": {
          "label": "P&L ($K)",
          "data": [10, 15, 8, -2, -5, 3, 12, 7, -1, 4],
          "baseValue": 0,
          "width": 60, "height": 12
        },
        "children": []
      }
    }
  }
}
```

## Heatmap

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

## Timeline

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

## Image

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

## Image + Chart (mixed content)

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

## Multi-Widget Dashboard

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
