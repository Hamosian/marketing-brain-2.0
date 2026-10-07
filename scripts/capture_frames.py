#!/usr/bin/env python3
"""Render a time-driven HTML animation to video frames (and optionally an MP4) with headless Chrome.

usage:
  python3 scripts/capture_frames.py <page.html|url> <outDir> --duration SECONDS
          [--fps 30] [--width 1920] [--height 1080] [--audio] [--mp4 out.mp4]

The page contract (see "Video (MP4)" in .claude/skills/riverside-brand-guidelines/SKILL.md):
  window.__frame(t)       required. Draw the frame for video time t (seconds), synchronously.
                          Every element's state must be a pure function of t: CSS transitions
                          and animations run on wall-clock time and will not capture.
  window.__audio(dur)     optional, used with --audio. Render the soundtrack (an
                          OfflineAudioContext is the way) and resolve to {len}, having stored a
                          base64 16-bit PCM WAV in window.__wav. Read back in 4 MB chunks.

Writes <outDir>/f00000.jpg ... and <outDir>/audio.wav. With --mp4 it compiles
scripts/frames_to_mp4.swift and encodes. Uses the installed Google Chrome through Playwright
(`pip3 install playwright`; no browser download needed). Speed on a 2026 MacBook: about
35 ms a frame at 1920x1080, so 2,760 frames took 95 s, and the encode took 30 s.
"""
import argparse
import base64
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("page")
    ap.add_argument("out_dir")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--audio", action="store_true")
    ap.add_argument("--mp4")
    a = ap.parse_args()

    # Check the timing before anything touches the disk: a zero fps or a NaN duration
    # would otherwise clear out_dir and then capture nothing.
    if a.fps <= 0:
        sys.exit("--fps must be a positive whole number")
    if not math.isfinite(a.duration) or a.duration <= 0:
        sys.exit("--duration must be a positive number of seconds")
    if a.width <= 0 or a.height <= 0:
        sys.exit("--width and --height must be positive")
    n = int(round(a.duration * a.fps))
    if n < 1:
        sys.exit(f"--duration {a.duration} at {a.fps} fps is less than one frame")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright is not installed: pip3 install playwright")
    if not os.path.exists(CHROME):
        sys.exit(f"Google Chrome not found at {CHROME}")

    url = a.page if "://" in a.page else "file://" + os.path.abspath(a.page)

    # out_dir is wiped before capture, so refuse anything that is not clearly this tool's
    # own output folder: the repo root or a folder above it, a folder holding the page,
    # or an existing folder with files this script did not write.
    raw_out = os.path.abspath(a.out_dir)
    if os.path.islink(raw_out):
        sys.exit(f"refusing to clear {raw_out}: it is a symlink; pass the real folder instead")
    out_dir = os.path.realpath(raw_out)
    repo_root = os.path.realpath(os.path.dirname(HERE))
    page_path = None if "://" in a.page else os.path.realpath(a.page)
    existing = os.listdir(out_dir) if os.path.isdir(out_dir) else []
    if os.path.commonpath([out_dir, repo_root]) == out_dir:
        sys.exit(f"refusing to clear {out_dir}: it is the repo root or a folder above it")
    if page_path and os.path.commonpath([out_dir, page_path]) == out_dir:
        sys.exit(f"refusing to clear {out_dir}: the page being captured lives inside it")
    foreign = [f for f in existing if not re.fullmatch(r"f\d+\.jpg|audio\.wav", f)]
    if foreign:
        sys.exit(f"refusing to clear {out_dir}: it holds files this script did not write, e.g. {foreign[0]}")
    # Clear the path as given (now known not to be a symlink), never a resolved target.
    a.out_dir = raw_out
    shutil.rmtree(raw_out, ignore_errors=True)
    os.makedirs(raw_out)
    wav = os.path.join(a.out_dir, "audio.wav") if a.audio else None

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True,
                                    args=["--hide-scrollbars", "--force-color-profile=srgb"])
        page = browser.new_page(viewport={"width": a.width, "height": a.height}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url)
        page.evaluate("document.fonts.ready.then(() => 1)")
        page.wait_for_timeout(1000)
        if not page.evaluate("typeof window.__frame === 'function'"):
            sys.exit("the page does not define window.__frame(t); see the contract at the top of this file")

        if wav:
            info = page.evaluate(f"window.__audio({a.duration})")
            step = 4_000_000
            parts = [page.evaluate(f"window.__wav.slice({o}, {o + step})") for o in range(0, info["len"], step)]
            with open(wav, "wb") as f:
                f.write(base64.b64decode("".join(parts)))
            print(f"audio: {os.path.getsize(wav) / 1e6:.1f} MB", flush=True)

        t0 = time.time()
        for k in range(n):
            page.evaluate(f"window.__frame({k / a.fps})")
            page.screenshot(path=os.path.join(a.out_dir, f"f{k:05d}.jpg"), type="jpeg", quality=94)
            if k and k % 300 == 0:
                print(f"frame {k}/{n}, {time.time() - t0:.0f} s", flush=True)
        browser.close()

    print(f"{n} frames in {time.time() - t0:.0f} s", flush=True)
    if errors:
        # A page error mid-run usually means one scene's renderer threw, and every frame
        # after it is frozen on the last good state. Fail loudly rather than encode it.
        sys.exit("page errors during capture: " + " | ".join(errors[:3]))

    if a.mp4:
        binary = os.path.join(tempfile.gettempdir(), "frames_to_mp4")
        src = os.path.join(HERE, "frames_to_mp4.swift")
        if not os.path.exists(binary) or os.path.getmtime(binary) < os.path.getmtime(src):
            subprocess.run(["swiftc", "-swift-version", "5", "-O", src, "-o", binary], check=True,
                           stderr=subprocess.DEVNULL)
        cmd = [binary, a.out_dir, str(a.fps), a.mp4] + ([wav] if wav else [])
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
