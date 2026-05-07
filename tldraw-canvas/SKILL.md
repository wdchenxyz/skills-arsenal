---
name: tldraw-canvas
description: Draw and manipulate shapes on tldraw Desktop canvases via its local HTTP API (default port 7236). Use when the user asks to draw, diagram, sketch, illustrate, or create visual content on a tldraw canvas - including flowcharts, architecture diagrams, wireframes, illustrations, or freehand drawings. Triggers on mentions of "tldraw", "draw on canvas", "sketch this", "create a diagram", or requests to visually represent ideas.
---

# tldraw Desktop Canvas API

Interact with tldraw Desktop's local HTTP server to programmatically read and
modify canvases.

Base URL: `http://localhost:7236`

## Default Workflow

Use this sequence for every non-trivial canvas task:

```
1. GET /api/doc
   Pick the focused doc, or a doc whose name matches the user's request.

2. GET /api/doc/{id}/shapes
   Inspect existing content before writing. If the canvas contains user work,
   preserve it unless the user explicitly asked to replace or clean it.

3. Plan the diagram shape.
   Decide the lane/column model, major boxes, dependencies, and arrow flow
   before creating shapes.

4. POST /api/doc/{id}/actions
   Send one batched action list. This keeps the work in one undo step.

5. GET /api/doc/{id}/screenshot?size=large
   Verify visually. If it is messy, run a deliberate cleanup/re-layout pass.
```

For substantial diagrams, prefer the harness in `scripts/tldraw_harness.py`
over ad hoc curl.

## Harness

Use the local Python harness for reliable drawing and verification. It uses
only the Python standard library.

Common commands:

```bash
# List open tldraw documents.
python3 /Users/wdchen/.agents/skills/tldraw-canvas/scripts/tldraw_harness.py list

# Capture a verification screenshot.
python3 /Users/wdchen/.agents/skills/tldraw-canvas/scripts/tldraw_harness.py screenshot \
  --name "Vellum" \
  --out /tmp/tldraw-vellum.jpg

# Draw a tiny demo without clearing existing work.
python3 /Users/wdchen/.agents/skills/tldraw-canvas/scripts/tldraw_harness.py demo \
  --name "Vellum" \
  --out /tmp/tldraw-demo.jpg

# Replace the current page with the demo. Use only when safe.
python3 /Users/wdchen/.agents/skills/tldraw-canvas/scripts/tldraw_harness.py demo \
  --name "Vellum" \
  --replace \
  --out /tmp/tldraw-demo.jpg
```

Use it as an importable helper for real diagrams:

```python
from pathlib import Path
import sys

sys.path.insert(0, "/Users/wdchen/.agents/skills/tldraw-canvas/scripts")
from tldraw_harness import DiagramBuilder, TldrawClient

client = TldrawClient()
doc = client.get_doc(name="Vellum")

b = DiagramBuilder()
b.clear()  # Only when replacing your own draft or user requested cleanup.
b.text("title", 80, 40, "Architecture", max_width=800, font_size=34)
b.rect("client", 100, 160, 320, 130, color="blue", fill="background",
       text="Client UI")
b.rect("api", 560, 160, 320, 130, color="violet", fill="background",
       text="API routes")
b.arrow("client_to_api", "client", "api", color="blue")

client.post_actions(doc["id"], b.actions, allow_clear=True)
client.screenshot(doc["id"], Path("/tmp/tldraw-check.jpg"))
```

Harness safety:

- `post_actions(..., allow_clear=False)` rejects any `clear` action.
- Pass `allow_clear=True` only when the user asked for replacement/cleanup or
  when replacing a draft you just generated.
- Shape helpers remember geometry so connected arrows can be created from
  shape IDs without hand-computing centers.

## Cleanup / Re-layout Strategy

When a generated diagram looks messy in the screenshot, do not try to rescue it
by nudging individual shapes one at a time. Prefer a deliberate re-layout pass.

Use this workflow for diagrams you just created, or when the user explicitly
asks you to clean up or rewire an existing canvas:

```
1. Capture a screenshot and name the concrete readability problems:
   crossing arrows, dense connector labels, text overflow, cramped groups,
   too many boxes, unclear flow direction, or weak grouping.

2. Redesign around 2-4 high-level lanes or columns.
   Common choices:
   - left-to-right pipeline
   - horizontal swimlanes by workflow
   - columns such as Client / API / Domain / Data / External

3. Merge low-level nodes into grouped boxes when arrows cross heavily.
   Example: replace separate quote-cache/history-cache/provider boxes with
   one "Local and external dependencies" box when exact wiring is secondary.

4. Remove most arrow labels.
   Put explanations inside boxes or in short note pills. Arrows should mainly
   communicate direction.

5. Recreate the diagram in one batch.
   Start with `{ "_type": "clear" }` only when replacing your own draft or
   when the user asked for cleanup. Then create boxes, text, and arrows, and
   send large lane backgrounds to the back.

6. Verify again with a screenshot.
   If text is cramped, expand row/box height and shorten labels. Iterate until
   the canvas is legible at a glance.
```

Practical heuristics:

- Prefer fewer, larger boxes over many exact implementation boxes in a
  high-level diagram.
- Keep each lane's arrows mostly left-to-right or top-to-bottom.
- Avoid arrows that pass through unrelated boxes; group dependencies instead.
- Budget extra space for tldraw's handwritten font. It needs more room than
  normal UI text.
- Use large tinted rectangles as lane backgrounds, then `sendToBack`.
- Aim for the smallest shape count that still preserves the architecture.
- If the canvas contains user-created work that should be preserved, do not
  clear it. Draw the cleaned version beside it or ask before replacing it.

## Layout Patterns

Choose the simplest pattern that matches the task:

- Pipeline: best for request/response, data processing, or build/deploy flows.
- Swimlanes: best when the same system has multiple workflows, such as ingest,
  analytics, and assistant paths.
- Columns: best for high-level architecture, such as UI, API, services, data,
  and external systems.
- Hub-and-spoke: best for one central service with several integrations.
- Before/after: best for refactors, migrations, or cleanup explanations.

For architecture diagrams, start with coarse groups. Add precise file/module
names only when they help the user understand ownership or data flow.

## API Quick Reference

Endpoints:

```text
GET  /api/doc
GET  /api/doc/:id/shapes
GET  /api/doc/:id/screenshot?size=small|medium|large|full
POST /api/doc/:id/actions
POST /api/doc/:id/exec
```

Shape IDs are plain strings such as `"box1"`. Do not add a `shape:` prefix.

Create example:

```json
{
  "actions": [
    {
      "_type": "create",
      "shape": {
        "_type": "rectangle",
        "shapeId": "box1",
        "x": 100,
        "y": 100,
        "w": 300,
        "h": 160,
        "color": "blue",
        "fill": "background",
        "text": "Client UI"
      }
    }
  ]
}
```

Arrow example:

```json
{
  "_type": "create",
  "shape": {
    "_type": "arrow",
    "shapeId": "a1",
    "fromId": "box1",
    "toId": "box2",
    "x1": 250,
    "y1": 180,
    "x2": 650,
    "y2": 180,
    "color": "black",
    "kind": "elbow"
  }
}
```

## Key Rules

- Geo sub-types go in `_type`: use `"_type": "rectangle"`, not `"_type":
  "geo"` with a separate geo field.
- Batch actions in one `POST /actions` call. This creates one undo step.
- Connect arrows with `fromId` and `toId` so they stay attached when shapes
  move.
- Use `place`, `stack`, `align`, and `distribute` for simple arrangements.
  For complex diagrams, use the harness so coordinates and arrows remain
  consistent.
- Prefer defaults and restrained styling. Use color to encode groups, not to
  decorate.
- Verify with screenshots before finishing.

## Full API Reference

See `references/api-docs.md` for complete shape types, properties, colors,
fills, and available actions.
