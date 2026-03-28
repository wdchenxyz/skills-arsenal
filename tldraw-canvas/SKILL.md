---
name: tldraw-canvas
description: Draw and manipulate shapes on tldraw Desktop canvases via its local HTTP API (default port 7236). Use when the user asks to draw, diagram, sketch, illustrate, or create visual content on a tldraw canvas — including flowcharts, architecture diagrams, wireframes, illustrations, or freehand drawings. Triggers on mentions of "tldraw", "draw on canvas", "sketch this", "create a diagram", or requests to visually represent ideas.
---

# tldraw Desktop Canvas API

Interact with tldraw Desktop's local HTTP server to programmatically read and modify canvases.

**Base URL**: `http://localhost:7236` (default port)

## Workflow

```
1. GET /api/doc                     → get doc ID
2. GET /api/doc/{id}/shapes         → get existing shapes
3. POST /api/doc/{id}/actions       → create/modify shapes
4. GET /api/doc/{id}/screenshot     → verify result visually
```

## Quick Example

```bash
# Get doc ID
DOC=$(curl -s http://localhost:7236/api/doc | python3 -c "import sys,json; print(json.load(sys.stdin)['docs'][0]['id'])")

# Create shapes
curl -s -X POST "http://localhost:7236/api/doc/${DOC}/actions" \
  -H "Content-Type: application/json" \
  -d '{"actions": [
    {"_type": "create", "shape": {"_type": "rectangle", "shapeId": "box1", "x": 100, "y": 100, "w": 300, "h": 200, "color": "blue", "fill": "solid", "text": "Hello"}},
    {"_type": "create", "shape": {"_type": "arrow", "shapeId": "arr1", "fromId": "box1", "toId": "box2"}}
  ]}'

# Verify
curl -s "http://localhost:7236/api/doc/${DOC}/screenshot?size=large" -o /tmp/tldraw.jpg
```

## Key Rules

- **Geo sub-types go in `_type`**: Use `"_type": "rectangle"`, not `"_type": "geo"` with a separate geo field.
- **Batch actions**: Send multiple actions in one POST — they group as a single undo step.
- **Use `place`/`stack`/`align`** over manual coordinate math when positioning shapes relative to each other.
- **Connect arrows with `fromId`/`toId`**: Arrows snap to shapes and stay attached when shapes move.
- **Default shape size**: ~300x200 for shapes with text. Standard gap between shapes: ~200.
- **Prefer defaults**: Use black color, medium size, no fill unless there's a reason for styling.
- **Verify with screenshots**: After drawing, fetch a screenshot to confirm the result looks correct.

## Full API Reference

See [references/api-docs.md](references/api-docs.md) for complete shape types, properties, colors, fills, and all available actions.
