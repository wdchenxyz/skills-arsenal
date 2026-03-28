# tldraw Desktop Canvas API Reference

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/doc` | List open documents (sorted by focus order). Filter: `?name=` |
| GET | `/api/doc/:id/shapes` | Get all shapes on current page as JSON |
| GET | `/api/doc/:id/screenshot` | Capture shapes as JPEG. Options: `?size=small|medium|large|full` |
| POST | `/api/doc/:id/actions` | Execute structured actions |
| POST | `/api/doc/:id/exec` | Run arbitrary JS against tldraw Editor |

## Shape Types

Shapes use plain string IDs (e.g. `"box1"`) — no `shape:` prefix needed.

### Geo shapes
`{ _type, shapeId, x, y, w, h, color, fill, note, text?, textAlign? }`

**Geo sub-types** (set via `_type`): `rectangle`, `ellipse`, `triangle`, `diamond`, `hexagon`, `pill`, `cloud`, `star`, `heart`, `pentagon`, `octagon`, `x-box`, `check-box`, `trapezoid`, `parallelogram-right`, `parallelogram-left`, `fat-arrow-right`, `fat-arrow-left`, `fat-arrow-up`, `fat-arrow-down`

### Text
`{ _type: "text", shapeId, x, y, anchor, color, fontSize?, maxWidth, note, text }`

### Arrow
`{ _type: "arrow", shapeId, x1, y1, x2, y2, color, fromId?, toId?, bend?, kind?, text?, note }`
- kind: `"arc"` (default, curved) or `"elbow"` (right-angle routing)
- Use `fromId`/`toId` to connect shapes — arrow stays attached when shapes move

### Line
`{ _type: "line", shapeId, x1, y1, x2, y2, color, note }`

### Note (sticky note)
`{ _type: "note", shapeId, x, y, color, text?, note }`

### Draw/Pen (read-only; create via `pen` action)
`{ _type: "pen", shapeId, color, fill?, note }`

### Image (read-only)
`{ _type: "image", shapeId, x, y, w, h, altText, note }`

## Property Values

**Colors**: red, light-red, green, light-green, blue, light-blue, orange, yellow, black, violet, light-violet, grey, white

**Fill**: none, tint, background, solid, pattern

**Anchor** (text shapes): top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right

## Actions

POST to `/api/doc/:id/actions` with `{"actions": [...]}`. Every action has an `_type` field. All actions in one request are grouped as a single undo step.

### create
```json
{ "_type": "create", "shape": { "_type": "rectangle", "shapeId": "box1", "x": 100, "y": 100, "w": 200, "h": 150, "color": "black", "fill": "none", "text": "Hello" } }
```

### update
```json
{ "_type": "update", "shape": { "_type": "rectangle", "shapeId": "box1", "color": "red", "text": "Updated" } }
```
Provide shapeId and _type to identify shape. Only changed properties required.

### delete
```json
{ "_type": "delete", "shapeId": "box1" }
```

### clear
```json
{ "_type": "clear" }
```

### place — Position relative to another shape
```json
{ "_type": "place", "shapeId": "box2", "referenceShapeId": "box1", "side": "right", "align": "center", "sideOffset": 20 }
```
Side: top, bottom, left, right. Align: start, center, end. Optional: sideOffset, alignOffset.

### label — Set text inside a shape
```json
{ "_type": "label", "shapeId": "box1", "text": "New label" }
```

### align
```json
{ "_type": "align", "shapeIds": ["box1", "box2"], "alignment": "center-horizontal" }
```
Alignment: top, center-vertical, bottom, left, center-horizontal, right

### distribute
```json
{ "_type": "distribute", "shapeIds": ["a", "b", "c"], "direction": "horizontal" }
```

### stack
```json
{ "_type": "stack", "shapeIds": ["a", "b", "c"], "direction": "vertical", "gap": 20 }
```

### move
```json
{ "_type": "move", "shapeId": "box1", "x": 300, "y": 200, "anchor": "center" }
```
Anchor: top-left (default), top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right.

### bringToFront / sendToBack
```json
{ "_type": "bringToFront", "shapeIds": ["box1"] }
{ "_type": "sendToBack", "shapeIds": ["box1"] }
```

### resize
```json
{ "_type": "resize", "shapeIds": ["box1"], "scaleX": 2, "scaleY": 1.5, "originX": 100, "originY": 100 }
```

### rotate
```json
{ "_type": "rotate", "shapeIds": ["box1"], "degrees": 45, "originX": 200, "originY": 200 }
```

### pen — Draw freehand
```json
{ "_type": "pen", "shapeId": "path1", "points": [{"x":100,"y":100},{"x":150,"y":80},{"x":200,"y":120}], "color": "red", "style": "smooth", "closed": false, "fill": "none" }
```
Style: smooth (interpolates), straight (minimal interpolation). Closed: true connects last point to first.
