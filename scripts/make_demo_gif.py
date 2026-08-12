#!/usr/bin/env python3
"""Render the AnyLover demo GIF from *real* CLI output.

This script runs the actual `anylover` commands against a throwaway
ANYLOVER_HOME, captures their real stdout, and animates it as a terminal
session. Nothing shown in the GIF is hand-written output.

Long blocks are elided, never rewritten: an omitted region is marked with a
literal `…` line so the frame stays an honest excerpt.

Usage:
    python scripts/make_demo_gif.py [-o docs/assets/demo.gif]

Requires: Pillow, ffmpeg, and an `anylover` executable on PATH.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- terminal look -----------------------------------------------------------

WIDTH, HEIGHT = 1000, 396
PAD_X, PAD_Y = 22, 56
LINE_H = 20
FONT_SIZE = 14
COLS = 92
FPS = 20

BG = "#0d1117"
CHROME = "#161b22"
BORDER = "#30363d"
FG = "#e6edf3"
GRAY = "#8b949e"
GREEN = "#3fb950"
BLUE = "#79c0ff"
CYAN = "#a5d6ff"
PURPLE = "#d2a8ff"
TITLE = "#8b949e"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]

Span = tuple[str, str]  # (text, color)


@dataclass
class Line:
    spans: list[Span] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(s for s, _ in self.spans)

    def truncated(self, n: int) -> "Line":
        """Return this line revealed up to n characters (for typing)."""
        out: list[Span] = []
        left = n
        for text, color in self.spans:
            if left <= 0:
                break
            out.append((text[:left], color))
            left -= len(text)
        return Line(out)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    raise SystemExit("No monospace font found; install DejaVu Sans Mono.")


# --- running the real commands ----------------------------------------------


def run(cmd: list[str], env: dict[str, str]) -> list[str]:
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}\n{proc.stderr}")
    return proc.stdout.rstrip("\n").split("\n")


def elide(lines: list[str], keep: list[str], *, tail: int = 0) -> list[str]:
    """Keep lines whose stripped form starts with any prefix in `keep`.

    Omitted runs collapse into a single literal `…` marker so the viewer can
    see that something was cut rather than being shown a doctored excerpt.
    """
    out: list[str] = []
    gap = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        keeping = any(stripped.startswith(p) for p in keep)
        if tail and i >= len(lines) - tail:
            keeping = True
        if keeping:
            out.append(raw)
            gap = False
        elif not gap:
            out.append("  …")
            gap = True
    return out


def wrap(text: str, width: int, indent: str = "    ") -> list[str]:
    if len(text) <= width:
        return [text]
    out, cur = [], text
    first = True
    while len(cur) > width:
        cut = cur.rfind(" ", 0, width)
        if cut <= 0:
            cut = width
        out.append(cur[:cut])
        cur = (indent if first else indent) + cur[cut:].lstrip()
        first = False
    out.append(cur)
    return out


# --- colorizing --------------------------------------------------------------


def color_json(raw: str) -> Line:
    stripped = raw.strip()
    if stripped == "…":
        return Line([(raw, GRAY)])
    if ":" in stripped and stripped.startswith('"'):
        key, _, rest = raw.partition(":")
        return Line([(key, BLUE), (":", GRAY), (rest, CYAN)])
    return Line([(raw, GRAY)])


def color_context(raw: str, highlight: str) -> Line:
    stripped = raw.strip()
    if stripped == "…":
        return Line([(raw, GRAY)])
    if raw.startswith("#"):
        return Line([(raw, PURPLE)])
    if highlight and highlight in raw:
        return Line([(raw, GREEN)])
    return Line([(raw, GRAY)])


def color_command(raw: str) -> Line:
    spans: list[Span] = [("$ ", GREEN)]
    for token in raw.split(" "):
        color = BLUE if token.startswith("--") else FG
        spans.append((token + " ", color))
    return Line(spans)


# --- frame rendering ---------------------------------------------------------


class Renderer:
    def __init__(self, outdir: Path) -> None:
        self.outdir = outdir
        self.font = load_font(FONT_SIZE)
        self.bold = load_font(FONT_SIZE)
        self.n = 0

    def frame(self, lines: list[Line]) -> None:
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, WIDTH - 1, 38], fill=CHROME)
        d.line([0, 38, WIDTH, 38], fill=BORDER)
        for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            d.ellipse([20 + i * 20, 14, 30 + i * 20, 24], fill=c)
        d.text((WIDTH // 2 - 96, 12), "AnyLover — memory layer", font=self.font, fill=TITLE)

        y = PAD_Y
        for line in lines:
            x = PAD_X
            for text, color in line.spans:
                d.text((x, y), text, font=self.font, fill=color)
                x += int(d.textlength(text, font=self.font))
            y += LINE_H
        img.save(self.outdir / f"f{self.n:05d}.png")
        self.n += 1

    def hold(self, lines: list[Line], frames: int) -> None:
        for _ in range(frames):
            self.frame(lines)

    def type_line(self, base: list[Line], line: Line, cps: int, pause: int) -> None:
        total = len(line.text)
        i = 0
        while i < total:
            i = min(total, i + cps)
            self.frame(base + [line.truncated(i)])
        self.hold(base + [line], pause)

    def reveal(self, base: list[Line], lines: list[Line], every: int, pause: int) -> None:
        shown: list[Line] = []
        for ln in lines:
            shown.append(ln)
            for _ in range(every):
                self.frame(base + shown)
        self.hold(base + shown, pause)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="docs/assets/demo.gif")
    args = ap.parse_args()

    if not shutil.which("anylover"):
        raise SystemExit("anylover not on PATH; install it first.")
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found; brew install ffmpeg")

    home = Path(tempfile.mkdtemp(prefix="anylover-demo-"))
    env = {**os.environ, "ANYLOVER_HOME": str(home)}
    pref = "I don't like back-to-back follow-up questions; give me room to think."

    run(["anylover", "init", "--name", "Any"], env)
    cmd1 = [
        "anylover", "remember", pref,
        "--kind", "preference", "--consent", "explicit", "--surface", "codex",
    ]
    out1 = run(cmd1, env)
    cmd2 = ["anylover", "context", "--query", "how should we talk?"]
    out2 = run(cmd2, env)
    shutil.rmtree(home, ignore_errors=True)

    json_lines = elide(
        out1,
        ['"consent_basis"', '"content"', '"kind"', '"source_surface"', '"status"', "{", "}"],
    )
    ctx_lines = elide(
        out2,
        ["# AnyLover", "## Companion identity", "- Name:", "## Preferences", "- (remembered)"],
    )

    frames_dir = Path(tempfile.mkdtemp(prefix="anylover-frames-"))
    r = Renderer(frames_dir)

    # Act 1 — a memory is written from one surface, with explicit consent.
    c1 = Line([("# Codex writes one preference — with explicit consent", GRAY)])
    r.hold([], 6)
    r.type_line([], c1, 4, 6)
    base = [c1]
    typed = color_command(
        'anylover remember "…give me room to think." '
        "--kind preference --consent explicit --surface codex"
    )
    r.type_line(base, typed, 3, 8)
    base = base + [typed, Line([("", FG)])]
    body = [color_json(x) for x in json_lines]
    r.reveal(base, body, 2, 34)

    # Act 2 — a different tool, a new session, the same memory.
    c2 = Line([("# Claude Code. Different tool, new session. Same memory.", GRAY)])
    r.hold([], 4)
    r.type_line([], c2, 4, 6)
    base2 = [c2]
    typed2 = color_command('anylover context --query "how should we talk?"')
    r.type_line(base2, typed2, 3, 8)
    base2 = base2 + [typed2, Line([("", FG)])]
    body2: list[Line] = []
    for raw in ctx_lines:
        for piece in wrap(raw, COLS):
            body2.append(color_context(piece, "(remembered)"))
    r.reveal(base2, body2, 2, 20)

    tail = Line([("↑ written by one tool. recalled by another. stored on your machine.", GREEN)])
    r.hold(base2 + body2 + [Line([("", FG)]), tail], 62)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    palette = frames_dir / "palette.png"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
         "-i", str(frames_dir / "f%05d.png"),
         "-vf", "palettegen=max_colors=64:stats_mode=diff", str(palette)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
         "-i", str(frames_dir / "f%05d.png"), "-i", str(palette),
         "-lavfi", "paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
         "-loop", "0", str(out)],
        check=True,
    )
    shutil.rmtree(frames_dir, ignore_errors=True)

    size = out.stat().st_size / 1024
    print(f"{out}  {r.n} frames  {r.n / FPS:.1f}s  {size:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
