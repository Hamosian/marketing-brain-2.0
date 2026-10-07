#!/usr/bin/env python3
"""Transcribe an audio file locally with faster-whisper (free, offline, no key).

Usage:  transcribe.py <audio> [out_basename] [model]
  model: base.en (default, fast) | small.en (accurate) | base/small (non-English)

Writes <out>.txt (plain) and <out>.timestamped.txt ([HH:MM:SS] per segment).
Prints a one-line summary (runtime, duration, word count) when done.
faster-whisper bundles its own audio decoding, so ffmpeg is NOT required.
"""
import sys
import time

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit("faster-whisper not installed. Run: python3 -m pip install --user faster-whisper")

audio = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
out = sys.argv[2] if len(sys.argv) > 2 else "transcript"
model_size = sys.argv[3] if len(sys.argv) > 3 else "base.en"


def ts(s):
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


t0 = time.time()
model = WhisperModel(model_size, device="cpu", compute_type="int8")
segments, info = model.transcribe(audio, beam_size=5, vad_filter=True)

plain, stamped = [], []
for seg in segments:
    text = seg.text.strip()
    plain.append(text)
    stamped.append(f"[{ts(seg.start)}] {text}")

with open(f"{out}.txt", "w") as f:
    f.write(" ".join(plain))
with open(f"{out}.timestamped.txt", "w") as f:
    f.write("\n".join(stamped))

words = sum(len(p.split()) for p in plain)
print(f"DONE in {time.time() - t0:.0f}s | duration {ts(info.duration)} | {words} words | model {model_size}")
print(f"wrote {out}.txt and {out}.timestamped.txt")
