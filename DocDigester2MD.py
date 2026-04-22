#!/usr/bin/env python3
"""DocDigester2MD — Convert documents, audio, YouTube links and images to Markdown."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load docdigester.yaml from CWD, then script dir, falling back to defaults."""
    defaults = {
        "input_dir": "input",
        "output_dir": "output",
        "processed_dir": "processed",
        "processed_file": "processed.yaml",
    }
    for search_dir in (Path.cwd(), REPO_ROOT):
        cfg_path = search_dir / "docdigester.yaml"
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return {**defaults, **data}
    return defaults


_cfg = load_config()
INPUT_DIR = Path(_cfg["input_dir"])
OUTPUT_DIR = Path(_cfg["output_dir"])
PROCESSED_DIR = Path(_cfg["processed_dir"])
PROCESSED_FILE = Path(_cfg["processed_file"])
ERRORS_LOG = OUTPUT_DIR / "errors.log"

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xls", ".xlsx"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg"}
YOUTUBE_EXTENSIONS = {".url", ".txt"}

YOUTUBE_PATTERN = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_processed() -> dict:
    """Load processed.yaml; auto-migrate from processed.json if needed."""
    if PROCESSED_FILE.exists():
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            return {}

    # Migrate from legacy processed.json if present
    legacy = PROCESSED_FILE.parent / "processed.json"
    if legacy.exists():
        try:
            with open(legacy, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"Migrating {legacy.name} → {PROCESSED_FILE.name}")
            save_processed(data)
            return data
        except (json.JSONDecodeError, OSError):
            pass

    return {}


def save_processed(data: dict) -> None:
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def log_error(filename: str, error: str) -> None:
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with open(ERRORS_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ERROR '{filename}': {error}\n")


def build_frontmatter(original_name: str, file_type: str, size_bytes: int) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"---\n"
        f"original_file: {original_name}\n"
        f"processed_date: {now}\n"
        f"file_type: {file_type}\n"
        f"size_bytes: {size_bytes}\n"
        f"---\n\n"
    )


def file_type_label(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    if ext in YOUTUBE_EXTENSIONS:
        return "youtube"
    return ext.lstrip(".")


# ---------------------------------------------------------------------------
# YouTube helpers
# ---------------------------------------------------------------------------

def extract_youtube_url(path: Path) -> str | None:
    """Return the first YouTube URL found inside a .url/.txt file, or None."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            m = YOUTUBE_PATTERN.search(line.strip())
            if m:
                return line.strip()
    except OSError:
        pass
    return None


# ---------------------------------------------------------------------------
# Cached clients
# ---------------------------------------------------------------------------

_whisper_model = None
_markitdown = None
_whisper_model_name = "base"


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        _whisper_model = whisper.load_model(_whisper_model_name)
    return _whisper_model


def get_markitdown():
    global _markitdown
    if _markitdown is None:
        from markitdown import MarkItDown
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["AI_API_KEY"],
            base_url=os.environ["AI_BASE_URL"],
        )
        _markitdown = MarkItDown(
            llm_client=client,
            llm_model=os.environ["AI_MODEL"],
            llm_prompt=(
                "If this image contains text (printed or handwritten), transcribe it exactly as written, "
                "preserving the original structure and layout. "
                "If the image contains no text or is primarily visual, provide a detailed description of its content."
            ),
        )
    return _markitdown


# ---------------------------------------------------------------------------
# Whisper (local, CPU)
# ---------------------------------------------------------------------------

def whisper_transcribe(audio_path: Path) -> str:
    model = get_whisper_model()
    result = model.transcribe(str(audio_path), fp16=False)
    return result.get("text", "").strip()


# ---------------------------------------------------------------------------
# Converters — each returns (markdown_content, method, model_or_None)
# ---------------------------------------------------------------------------

def convert_document(path: Path) -> tuple[str, str, str | None]:
    result = get_markitdown().convert(str(path))
    return result.text_content, "markitdown", os.environ.get("AI_MODEL")


def convert_image(path: Path) -> tuple[str, str, str | None]:
    result = get_markitdown().convert(str(path))
    return result.text_content, "markitdown+llm", os.environ.get("AI_MODEL")


def convert_audio(path: Path) -> tuple[str, str, str | None]:
    text = whisper_transcribe(path)
    return f"## Audio Transcription\n\n{text}\n", "whisper", _whisper_model_name


def convert_youtube(url: str) -> tuple[str, str, str | None]:
    # Primary path: youtube_transcript_api (no download needed)
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        m = YOUTUBE_PATTERN.search(url)
        if m:
            video_id = m.group(1)
            entries = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join(e["text"] for e in entries)
            content = f"## YouTube Transcript\n\nSource: {url}\n\n{text}\n"
            return content, "youtube_transcript_api", None
    except Exception:
        pass  # fall through to yt-dlp + whisper

    # Fallback: download audio with yt-dlp and transcribe with Whisper
    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = str(Path(tmpdir) / "audio.%(ext)s")
        proc = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", out_template, url],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"yt-dlp failed:\n{proc.stderr}")

        mp3_files = list(Path(tmpdir).glob("*.mp3"))
        if not mp3_files:
            raise RuntimeError("yt-dlp produced no audio output")

        text = whisper_transcribe(mp3_files[0])
        content = f"## YouTube Transcript (via Whisper)\n\nSource: {url}\n\n{text}\n"
        return content, "yt-dlp+whisper", _whisper_model_name


def process_file(path: Path) -> tuple[str, str, str | None]:
    """Return (markdown_content, method, model)."""
    ext = path.suffix.lower()
    if ext in DOCUMENT_EXTENSIONS:
        return convert_document(path)
    if ext in IMAGE_EXTENSIONS:
        return convert_image(path)
    if ext in AUDIO_EXTENSIONS:
        return convert_audio(path)
    if ext in YOUTUBE_EXTENSIONS:
        url = extract_youtube_url(path)
        if not url:
            raise ValueError("No YouTube URL found in file")
        return convert_youtube(url)
    raise ValueError(f"Unsupported extension: {ext}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_ext = DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | YOUTUBE_EXTENSIONS
    processed = load_processed()
    newly_processed: list[str] = []

    candidates = [
        p
        for p in sorted(INPUT_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in all_ext
    ]

    if not candidates:
        print("No supported files found in input/. Nothing to do.")
        sys.exit(0)

    for path in candidates:
        name = path.name
        ext = path.suffix.lower()

        # Skip .url/.txt files that contain no YouTube URL
        if ext in YOUTUBE_EXTENSIONS and not extract_youtube_url(path):
            print(f"Skipping {name}: no YouTube URL detected")
            continue

        file_hash = sha256_file(path)
        entry = processed.get(name)

        if entry and entry.get("hash") == file_hash:
            print(f"Skipping {name}: already processed (hash unchanged)")
            continue

        size = path.stat().st_size
        ftype = file_type_label(path)
        action = "Reprocessing" if entry else "Processing"
        print(f"{action}: {name}  ({ftype}, {size:,} bytes)")

        try:
            content, method, model = process_file(path)
            fm = build_frontmatter(name, ftype, size)
            output_path = OUTPUT_DIR / (path.stem + ".md")
            output_path.write_text(fm + content, encoding="utf-8")

            record: dict = {
                "hash": file_hash,
                "processed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "output": output_path.name,
                "method": method,
            }
            if model is not None:
                record["model"] = model

            dest = PROCESSED_DIR / name
            shutil.move(str(path), dest)

            processed[name] = record
            newly_processed.append(name)
            print(f"  -> {output_path}  [{method}" + (f", {model}]" if model else "]"))
            print(f"  -> moved to {dest}")

        except Exception as exc:
            log_error(name, str(exc))
            print(f"  ERROR: {exc}", file=sys.stderr)

    if newly_processed:
        save_processed(processed)
        print(f"\nDone. Processed {len(newly_processed)} file(s): {', '.join(newly_processed)}")
    else:
        print("\nNo new files were processed.")


if __name__ == "__main__":
    main()
