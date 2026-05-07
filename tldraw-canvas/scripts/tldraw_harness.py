#!/usr/bin/env python3
"""Small stdlib harness for tldraw Desktop's local HTTP API.

The harness is intentionally lightweight:
- no third-party dependencies;
- guarded clear actions;
- reusable shape helpers;
- screenshot verification.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


Json = dict[str, Any]


class TldrawError(RuntimeError):
    """Raised when the tldraw local API cannot satisfy a request."""


def _read_json(response: Any) -> Json:
    raw = response.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _has_clear_action(actions: list[Json]) -> bool:
    return any(action.get("_type") == "clear" for action in actions)


class TldrawClient:
    """Client wrapper around tldraw Desktop's local HTTP API."""

    def __init__(self, base_url: str = "http://localhost:7236", timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _url(self, path: str, query: dict[str, str] | None = None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        return url

    def _get_json(self, path: str, query: dict[str, str] | None = None) -> Json:
        try:
            with urllib.request.urlopen(
                self._url(path, query), timeout=self.timeout
            ) as response:
                return _read_json(response)
        except urllib.error.URLError as exc:
            raise TldrawError(f"Unable to reach tldraw API: {exc}") from exc

    def docs(self, name: str | None = None) -> list[Json]:
        query = {"name": name} if name else None
        payload = self._get_json("/api/doc", query)
        docs = payload.get("docs", [])
        if not isinstance(docs, list):
            raise TldrawError("tldraw returned an invalid document list.")
        return docs

    def get_doc(self, name: str | None = None) -> Json:
        docs = self.docs(name=name)
        if not docs:
            target = f' named "{name}"' if name else ""
            raise TldrawError(f"No open tldraw document{target} was found.")

        if name:
            exact = [doc for doc in docs if doc.get("name") == name]
            if exact:
                return exact[0]

        return docs[0]

    def shapes(self, doc_id: str) -> Json:
        return self._get_json(f"/api/doc/{doc_id}/shapes")

    def post_actions(
        self,
        doc_id: str,
        actions: list[Json],
        *,
        allow_clear: bool = False,
    ) -> Json:
        if not actions:
            raise TldrawError("No actions were provided.")

        if _has_clear_action(actions) and not allow_clear:
            raise TldrawError(
                "Refusing to post a clear action without allow_clear=True."
            )

        request = urllib.request.Request(
            self._url(f"/api/doc/{doc_id}/actions"),
            data=json.dumps({"actions": actions}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return _read_json(response)
        except urllib.error.URLError as exc:
            raise TldrawError(f"Unable to post tldraw actions: {exc}") from exc

    def screenshot(self, doc_id: str, out: Path, *, size: str = "large") -> Path:
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(
                self._url(f"/api/doc/{doc_id}/screenshot", {"size": size}),
                timeout=self.timeout,
            ) as response:
                out.write_bytes(response.read())
        except urllib.error.URLError as exc:
            raise TldrawError(f"Unable to capture tldraw screenshot: {exc}") from exc

        return out


@dataclass
class ShapeBox:
    x: float
    y: float
    w: float
    h: float

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.w / 2, self.y + self.h / 2)


@dataclass
class DiagramBuilder:
    """Builds a safe batched tldraw actions payload."""

    actions: list[Json] = field(default_factory=list)
    boxes: dict[str, ShapeBox] = field(default_factory=dict)

    def clear(self) -> None:
        self.actions.append({"_type": "clear"})

    def create(self, shape: Json) -> None:
        self.actions.append({"_type": "create", "shape": shape})

    def _remember_box(self, shape_id: str, x: float, y: float, w: float, h: float) -> None:
        self.boxes[shape_id] = ShapeBox(x=x, y=y, w=w, h=h)

    def rect(
        self,
        shape_id: str,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        color: str = "black",
        fill: str = "none",
        text: str | None = None,
    ) -> None:
        shape: Json = {
            "_type": "rectangle",
            "shapeId": shape_id,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "color": color,
            "fill": fill,
        }
        if text is not None:
            shape["text"] = text
        self.create(shape)
        self._remember_box(shape_id, x, y, w, h)

    def pill(
        self,
        shape_id: str,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        color: str = "black",
        fill: str = "none",
        text: str | None = None,
    ) -> None:
        shape: Json = {
            "_type": "pill",
            "shapeId": shape_id,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "color": color,
            "fill": fill,
        }
        if text is not None:
            shape["text"] = text
        self.create(shape)
        self._remember_box(shape_id, x, y, w, h)

    def ellipse(
        self,
        shape_id: str,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        color: str = "black",
        fill: str = "none",
        text: str | None = None,
    ) -> None:
        shape: Json = {
            "_type": "ellipse",
            "shapeId": shape_id,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "color": color,
            "fill": fill,
        }
        if text is not None:
            shape["text"] = text
        self.create(shape)
        self._remember_box(shape_id, x, y, w, h)

    def text(
        self,
        shape_id: str,
        x: float,
        y: float,
        text: str,
        *,
        max_width: float = 360,
        font_size: int = 22,
        color: str = "black",
        anchor: str = "top-left",
    ) -> None:
        self.create(
            {
                "_type": "text",
                "shapeId": shape_id,
                "x": x,
                "y": y,
                "anchor": anchor,
                "color": color,
                "fontSize": font_size,
                "maxWidth": max_width,
                "text": text,
            }
        )

    def arrow(
        self,
        shape_id: str,
        from_id: str,
        to_id: str,
        *,
        color: str = "black",
        kind: str = "elbow",
        text: str | None = None,
    ) -> None:
        if from_id not in self.boxes:
            raise TldrawError(f"Unknown arrow source shape: {from_id}")
        if to_id not in self.boxes:
            raise TldrawError(f"Unknown arrow target shape: {to_id}")

        x1, y1 = self.boxes[from_id].center
        x2, y2 = self.boxes[to_id].center
        shape: Json = {
            "_type": "arrow",
            "shapeId": shape_id,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color,
            "fromId": from_id,
            "toId": to_id,
            "kind": kind,
        }
        if text:
            shape["text"] = text
        self.create(shape)

    def send_to_back(self, shape_ids: list[str]) -> None:
        self.actions.append({"_type": "sendToBack", "shapeIds": shape_ids})

    def bring_to_front(self, shape_ids: list[str]) -> None:
        self.actions.append({"_type": "bringToFront", "shapeIds": shape_ids})


def _demo_actions(*, replace: bool) -> list[Json]:
    suffix = "" if replace else f"_{int(time.time())}"
    b = DiagramBuilder()
    if replace:
        b.clear()

    b.text(f"title{suffix}", 80, 40, "tldraw harness demo", max_width=720, font_size=34)
    b.rect(
        f"client{suffix}",
        100,
        160,
        300,
        130,
        color="blue",
        fill="background",
        text="Client UI",
    )
    b.rect(
        f"api{suffix}",
        540,
        160,
        300,
        130,
        color="violet",
        fill="background",
        text="API route",
    )
    b.rect(
        f"service{suffix}",
        980,
        160,
        300,
        130,
        color="green",
        fill="background",
        text="Domain service",
    )
    b.arrow(f"a_client_api{suffix}", f"client{suffix}", f"api{suffix}", color="blue")
    b.arrow(f"a_api_service{suffix}", f"api{suffix}", f"service{suffix}", color="violet")
    return b.actions


def _cmd_list(args: argparse.Namespace) -> None:
    client = TldrawClient(args.base_url)
    docs = client.docs(name=args.name)
    print(json.dumps({"docs": docs}, indent=2))


def _cmd_screenshot(args: argparse.Namespace) -> None:
    client = TldrawClient(args.base_url)
    doc = client.get_doc(name=args.name)
    out = client.screenshot(doc["id"], Path(args.out), size=args.size)
    print(json.dumps({"doc": doc.get("name"), "doc_id": doc["id"], "out": str(out)}))


def _cmd_demo(args: argparse.Namespace) -> None:
    client = TldrawClient(args.base_url)
    doc = client.get_doc(name=args.name)
    actions = _demo_actions(replace=args.replace)
    client.post_actions(doc["id"], actions, allow_clear=args.replace)
    out = client.screenshot(doc["id"], Path(args.out), size=args.size)
    print(
        json.dumps(
            {
                "doc": doc.get("name"),
                "doc_id": doc["id"],
                "actions": len(actions),
                "out": str(out),
                "replaced": args.replace,
            }
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:7236")
    subparsers = parser.add_subparsers(required=True)

    list_parser = subparsers.add_parser("list", help="List open documents")
    list_parser.add_argument("--name", help="Optional document name filter")
    list_parser.set_defaults(func=_cmd_list)

    screenshot_parser = subparsers.add_parser(
        "screenshot", help="Capture a document screenshot"
    )
    screenshot_parser.add_argument("--name", help="Document name")
    screenshot_parser.add_argument("--out", required=True, help="Output image path")
    screenshot_parser.add_argument(
        "--size",
        default="large",
        choices=("small", "medium", "large", "full"),
        help="Screenshot size",
    )
    screenshot_parser.set_defaults(func=_cmd_screenshot)

    demo_parser = subparsers.add_parser("demo", help="Draw a small demo diagram")
    demo_parser.add_argument("--name", help="Document name")
    demo_parser.add_argument(
        "--replace",
        action="store_true",
        help="Clear the current page before drawing",
    )
    demo_parser.add_argument("--out", required=True, help="Output screenshot path")
    demo_parser.add_argument(
        "--size",
        default="large",
        choices=("small", "medium", "large", "full"),
        help="Screenshot size",
    )
    demo_parser.set_defaults(func=_cmd_demo)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
