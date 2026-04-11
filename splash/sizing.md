# Sizing Best Practices

## Tmux (`render-tmux`)

The tmux pane has limited width (~40-50 columns at 40% split). Use **vertical layout** (`flexDirection: "column"`) and conservative sizes:

- **Sparkline**: `width: 30`-`40`
- **LineChart**: `width: 30`-`40`, `height: 6`-`10`
- **Histogram**: `width: 25`-`35`
- **Heatmap**: `cellWidth: 2`-`3`
- **BarChart**: Keep labels short, `width: 25`-`35`
- Avoid side-by-side (`flexDirection: "row"`) layouts — they overflow in narrow panes. Stack elements vertically instead.
- **xLabels**: Keep labels short (3-4 chars like "0h", "Q1", "Mon") — long labels overlap. Fewer labels is better than crowded labels.

## Browser (`render-browser`)

Canvas charts (LineChart, CandlestickChart, AreaChart, BaselineChart) render at `width x 8` pixels and `height x 16` pixels. SVG charts are capped at their viewBox width.

### Single chart (full focus)

- **LineChart / AreaChart / BaselineChart**: `width: 60`-`80`, `height: 12`-`16`
- **CandlestickChart**: `width: 60`-`80`, `height: 14`-`18`
- **Histogram**: `width: 40`-`60`
- **Heatmap**: `cellWidth: 5`-`8`

### Multi-chart dashboard (3+ visualizations)

- **LineChart / AreaChart / BaselineChart**: `width: 40`-`50`, `height: 8`-`12`
- **CandlestickChart**: `width: 40`-`50`, `height: 10`-`14`
- **Histogram**: `width: 40`-`50`
- **Heatmap**: `cellWidth: 3`-`5`
- **Sparkline**: `width: 30`-`40`
- **BarChart**: `width: 35`-`45`
- Use `flexDirection: "column"` as the outer layout, with row sub-groups for pairing charts

## Row Pairing Rules

Only pair components with **similar visual height** in a row. Good pairs:
- LineChart + BarChart (both vertically compact)
- LineChart + AreaChart or BaselineChart (same Canvas height)
- CandlestickChart + LineChart (similar dimensions)
- Histogram + Heatmap (both medium height)
- Two LineCharts or two BarCharts

**Never** put these in a row:
- Sparklines + Table (extreme size mismatch)
- Sparklines + any full chart (sparklines are too small)
- Table + any chart (tables grow with content, unpredictable width)

**Tables** should always be in full-width column layout, never in a row with other components.

**Sparklines** work best stacked vertically as a group, or inline with Metric/KeyValue components — not paired with charts.

Match `height` props when pairing two SVG charts in a row (e.g. both `height: 10`).

## Layout Tips

- Side-by-side layouts work well with `flexDirection: "row"` and `gap: 4`
- SVG charts are capped at their maxWidth and won't stretch beyond it
- BarChart uses `width x 8` pixels (same as Canvas charts) with responsive fallback when omitted (300px height default)
- Colors use hex values (e.g. `"#22c55e"`) for best results

## Data Tips

- **BarChart**: Ensure data values have meaningful variation. If all values are near-identical (e.g. 99.7, 99.8, 99.9), bars will look identical — use a different chart or show the delta instead. For multi-series, limit to 5 series max (matches the 5-color palette). `height` prop matters more than `width` for horizontal bars.
- **xLabels**: The number of labels should match the visual density. 6 labels for 12 data points is fine; 12 labels for 12 points may crowd the axis.
