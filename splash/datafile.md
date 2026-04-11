# dataFile Support

Instead of inline data, components can load data from JSON, CSV, or TSV files using the `dataFile` prop. The resolver parses the file and injects the appropriate props.

## Supported Components

| Component | `dataFile` produces | Column hint props |
|-----------|--------------------|--------------------|
| `LineChart`, `AreaChart`, `BaselineChart`, `Sparkline`, `Histogram` | `data: number[]` | `dataColumn` (which numeric column), `xLabelsColumn` |
| `CandlestickChart` | `data: [{time, open, high, low, close}]` | Auto-detects OHLC columns; first non-OHLC column used as `time` |
| `BarChart` | `data: [{categoryKey: ..., series1: N, ...}], categoryKey, series[]` | `categoryKey` (explicit category column). Auto-detects first string column as category, all numeric columns as series. |
| `Table` | `columns` + `rows` | (auto-detected from headers) |
| `Heatmap` | `data: number[][]` | (JSON 2D array only) |
| `Timeline` | `items: [{title, description?, date?, status?}]` | `titleColumn`, `descriptionColumn`, `dateColumn`, `statusColumn` |

## Auto-detection

- **Numeric columns**: Auto-detected from both JSON numbers and numeric strings in CSV/TSV (e.g. `"45"` is treated as numeric).
- **BarChart**: Auto-detects first string column as `categoryKey`, ALL numeric columns as `series` (multi-series). Colors assigned from `var(--chart-1)` through `var(--chart-5)`.
- **Timeline**: Auto-detects first string column as title; other columns require explicit hints.

## Example: Timeline from CSV

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

## Example: LineChart from CSV

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
