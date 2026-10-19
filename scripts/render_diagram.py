#!/usr/bin/env python3
"""Turn a verified, simplified collision layout into an editable SVG sketch.

No image upload, network call, geolocation, fault assignment, or inference.
Python 3.9+; standard library only.
"""
from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path
from typing import Any


def _txt(value: Any, limit: int = 100) -> str:
    return escape(str(value)[:limit], quote=True)


def _num(value: Any, what: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{what} must be a number")
    val = float(value)
    if not (-10000 <= val <= 10000):
        raise ValueError(f"{what} is out of supported range")
    return val


def _point(value: Any, what: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{what} must be [x, y]")
    return (_num(value[0], what + '.x'), _num(value[1], what + '.y'))


def _rect(value: Any, what: str) -> tuple[float, float, float, float]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError(f"{what} must be [x, y, width, height]")
    x, y, w, h = [_num(v, what) for v in value]
    if w <= 0 or h <= 0:
        raise ValueError(f"{what} width/height must be positive")
    return x, y, w, h


def render(config: dict[str, Any]) -> str:
    if not isinstance(config, dict):
        raise ValueError('Top-level JSON must be an object')
    width = int(_num(config.get('canvas_width', 960), 'canvas_width'))
    height = int(_num(config.get('canvas_height', 740), 'canvas_height'))
    if width < 500 or height < 500:
        raise ValueError('Canvas must be at least 500 by 500')
    vehicles = config.get('vehicles', [])
    if not isinstance(vehicles, list) or not 1 <= len(vehicles) <= 8:
        raise ValueError('Provide 1–8 vehicles')
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Schematic collision scene sketch">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<defs><marker id="arrowhead" markerWidth="12" markerHeight="12" refX="10" '
        'refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#111"/></marker></defs>',
        f'<text x="{width/2}" y="53" text-anchor="middle" font-family="Arial, sans-serif" '
        f'font-size="27" font-weight="bold">{_txt(config.get("title", "COLLISION SCENE — SKETCH"))}</text>',
        f'<text x="{width/2}" y="84" text-anchor="middle" font-family="Arial, sans-serif" '
        'font-size="17">Not to scale — approximate positions</text>',
    ]
    for idx, item in enumerate(config.get('parking_spaces', [])):
        x, y, w, h = _rect(item['rect'], f'parking_spaces[{idx}].rect')
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                     'stroke="#9a9a9a" stroke-width="2"/>')
    for idx, item in enumerate(vehicles):
        x, y, w, h = _rect(item['rect'], f'vehicles[{idx}].rect')
        front = item.get('front', 'top')
        if front not in {'top','bottom','left','right'}:
            raise ValueError(f'vehicles[{idx}].front must be top/bottom/left/right')
        cx, cy = x + w/2, y + h/2
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                     'fill="white" stroke="#111" stroke-width="4"/>')
        if front in {'top','bottom'}:
            fy, ry = (y + 34, y + h - 25) if front == 'top' else (y + h - 25, y + 34)
            lines.extend([
                f'<text x="{cx}" y="{fy}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18">FRONT</text>',
                f'<text x="{cx}" y="{ry}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18">REAR</text>',
            ])
        else:
            lines.append(f'<text x="{cx}" y="{y+32}" text-anchor="middle" font-family="Arial, sans-serif" '
                         f'font-size="16">FRONT: {front.upper()}</text>')
        lines.extend([
            f'<text x="{cx}" y="{cy-7}" text-anchor="middle" font-family="Arial, sans-serif" font-size="41" font-weight="bold">{_txt(item.get("id", "?"), 4)}</text>',
            f'<text x="{cx}" y="{cy+21}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18">{_txt(item.get("label", "Vehicle"), 35)}</text>',
            f'<text x="{cx}" y="{cy+48}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16">{_txt(item.get("state", ""), 35)}</text>',
        ])
        door = item.get('door')
        if door is not None:
            side = door.get('side')
            if side not in {'left','right','top','bottom'}:
                raise ValueError(f'vehicles[{idx}].door.side unsupported')
            at = _num(door.get('at', 0.5), f'vehicles[{idx}].door.at')
            if not 0 <= at <= 1:
                raise ValueError('door.at must be 0..1')
            if side == 'left': anchor = (x, y + h*at)
            elif side == 'right': anchor = (x + w, y + h*at)
            elif side == 'top': anchor = (x + w*at, y)
            else: anchor = (x + w*at, y + h)
            tip = _point(door['tip'], f'vehicles[{idx}].door.tip')
            lines.append(f'<line x1="{anchor[0]}" y1="{anchor[1]}" x2="{tip[0]}" y2="{tip[1]}" '
                         'stroke="#111" stroke-width="6" stroke-linecap="round"/>')
            lines.append(f'<text x="{tip[0]}" y="{tip[1]-16}" text-anchor="middle" '
                         f'font-family="Arial, sans-serif" font-size="17" font-weight="bold">{_txt(door.get("label", "DOOR OPEN"), 45)}</text>')
    for idx, arrow in enumerate(config.get('arrows', [])):
        x1, y1 = _point(arrow['from'], f'arrows[{idx}].from')
        x2, y2 = _point(arrow['to'], f'arrows[{idx}].to')
        lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                     'stroke="#111" stroke-width="5" marker-end="url(#arrowhead)"/>')
        if arrow.get('label'):
            lines.append(f'<text x="{(x1+x2)/2+43}" y="{(y1+y2)/2-4}" '
                         f'font-family="Arial, sans-serif" font-size="17">{_txt(arrow["label"], 50)}</text>')
    lines.append(f'<text x="{width/2}" y="{height-86}" text-anchor="middle" font-family="Arial, sans-serif" '
                 f'font-size="19">{_txt(config.get("area_label", "PARKING AREA"), 60)}</text>')
    notes = config.get('notes', [])
    if not isinstance(notes, list) or len(notes) > 2:
        raise ValueError('notes must be a list of at most two strings')
    for i, note in enumerate(notes):
        lines.append(f'<text x="{width/2}" y="{height-56 + i*22}" text-anchor="middle" '
                     f'font-family="Arial, sans-serif" font-size="15" fill="#333">{_txt(note, 140)}</text>')
    lines.append('</svg>')
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Input JSON scene (see examples/)')
    parser.add_argument('--output', '-o', type=Path, required=True, help='Output SVG file')
    args = parser.parse_args()
    config = json.loads(args.input.read_text(encoding='utf-8'))
    svg = render(config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding='utf-8')
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()