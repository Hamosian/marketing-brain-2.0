---
name: podcast-transcript
description: Get a transcript (and optional summary) of a podcast episode from a Spotify, Apple Podcasts, or any podcast link - even though Spotify itself is DRM-locked and exposes no transcript. Finds the show's open RSS feed, downloads the undRM'd episode MP3, and transcribes it locally and for free with faster-whisper (open-source Whisper, no account, offline). Use whenever the user pastes a Spotify/Apple/podcast episode URL and asks to "summarize this podcast", "transcribe this episode", "get the transcript", "what does this episode say", "TL;DR this pod", or shares an open.spotify.com/episode or podcasts.apple.com link for content, competitive-intel, or research. Also handles YouTube-hosted episodes (yt-dlp captions, no transcription needed).
---

# Podcast Transcript

Turn a podcast episode link into a full transcript, then (if asked) a summary. Works for Spotify links even though Spotify's audio is DRM-locked and its auto-transcripts live only inside the Spotify app - the trick is to never pull "from Spotify," but to find the same episode in an open source.

## The core idea

Every podcast, including one hosted on Spotify, is also published via a public **RSS feed** with an undRM'd MP3 enclosure. Find the feed, grab the episode's MP3, transcribe it. That path works for any episode. Faster shortcuts (a YouTube version, a publisher transcript) are tried first when they exist.

## Tooling (one-time, free, no account)

Transcription uses **faster-whisper** - open-source Whisper (MIT), runs locally on the user's machine, no API key, no cost, offline. It bundles its own audio decoding (the `av` package), so **no ffmpeg or Homebrew is needed**.

Check it, and install into the user's site if missing (no sudo/password required):

```bash
python3 -c "import faster_whisper; print('ok', faster_whisper.__version__)" 2>/dev/null \
  || python3 -m pip install --user --quiet faster-whisper
```

If pip is blocked by an externally-managed environment, fall back to a `--break-system-packages` user install or a venv, and say so.

## Workflow

Do all identification steps, confirm the matched episode, then transcribe.

### 1. Identify the show and episode
From the pasted URL, get the **podcast name** and **episode title**:
- Spotify / Apple links: `WebFetch` the URL asking for podcast name, episode title, host, guest, and description. (Spotify episode pages expose this metadata even though they hide audio.)
- Note the title text - it is the key you match against the RSS feed.

### 2. Find the open RSS feed
- `WebSearch` for the show on Apple Podcasts to get its numeric id (e.g. `id1837922764`), or search for the show's RSS/Substack feed directly.
- Resolve the feed URL from an Apple id with the iTunes Lookup API (no key):
  ```bash
  curl -s "https://itunes.apple.com/lookup?id=<APPLE_ID>&entity=podcast" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['results'][0].get('feedUrl'))"
  ```
- Beware: several shows can share a similar name. Confirm the feed's episode titles look like the right show before trusting it. Substack-hosted shows usually feed at `https://<name>.substack.com/feed`.

### 3. Locate the episode MP3 and download it
Use the bundled helper - it parses the feed, fuzzy-matches the episode title, prints the enclosure URL + duration, and downloads to the scratchpad:
```bash
python3 .claude/skills/podcast-transcript/scripts/fetch_from_feed.py \
  "<FEED_URL>" "<episode title fragment>" "<OUT_DIR>/episode.mp3"
```
If no match prints, widen the title fragment or list the feed's recent titles (`--list`) and pick by hand.

### 4. Transcribe locally
```bash
python3 .claude/skills/podcast-transcript/scripts/transcribe.py \
  "<OUT_DIR>/episode.mp3" "<OUT_DIR>/episode" base.en
```
- Writes `<out>.txt` (plain) and `<out>.timestamped.txt` (with `[HH:MM:SS]` markers).
- Model choice: **`base.en`** is the default - fast, solid for clear English podcast audio (~6-7 min for a 68-min episode on Apple Silicon CPU). Use **`small.en`** for higher accuracy on tricky names or crosstalk (slower). Use **`base`/`small`** (no `.en`) for non-English audio. The first run of a model downloads it once (~145 MB for base).
- For long episodes, run it with `run_in_background: true` and read the output file when it completes.

### 5. Read and deliver
Read the timestamped transcript, then give the user what they asked for - a summary, key quotes with timestamps, or the raw text. Tie takeaways to the Q2 priorities (awareness, activation, pipeline) when it's a strategy/competitive listen. The transcript files stay in the scratchpad; offer them if the user wants the raw text.

## Shortcuts (try before the RSS path when they clearly apply)

- **YouTube version** - if the show is on YouTube, captions are instant, no transcription: `yt-dlp --write-subs --write-auto-subs --sub-lang "en.*" --skip-download --convert-subs srt <youtube-url>` (see the `yt-dlp-transcription-recipe` memory). yt-dlp is not installed by default; install with `python3 -m pip install --user yt-dlp` if the user wants this path.
- **Publisher transcript / show notes** - many shows (Substack especially) post a transcript or detailed timestamped notes on their site. `WebFetch` the episode's web page first; if a full transcript is there, skip audio entirely.

## Failure modes

- **Wrong show matched** - similarly named podcasts are common. Always confirm the feed's episodes match the guest/title before downloading.
- **Episode not in feed** - some feeds only carry recent episodes; older ones may need the publisher's site or a paged feed.
- **Bare Spotify metadata only** - if `WebFetch` returns only Spotify's short description, do not present it as a transcript; say so and proceed to the feed path.
- **Transcript looks rough** - flag it and offer a `small.en` re-run for accuracy.

## Boundaries

Transcribe only publicly published episodes for the user's own research, summarization, or competitive intel. Respect copyright when quoting: short attributed excerpts, not wholesale reproduction of the episode.
