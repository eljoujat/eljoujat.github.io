#!/usr/bin/env python3
"""Publish a YouTube video as a podcast episode.

Typical usage from the repository root:

    python3 tools/podcast_publish.py "https://www.youtube.com/watch?v=VIDEO_ID"

The script can run as a dry-run first:

    python3 tools/podcast_publish.py URL --dry-run

A real publication requires:
- yt-dlp
- ffmpeg/ffprobe
- internetarchive CLI command `ia`, configured with `ia configure`
"""
from __future__ import annotations

import argparse
import email.utils
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time

try:
    import yaml
except Exception:  # pragma: no cover - friendly runtime error
    yaml = None

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
DC_NS = "http://purl.org/dc/elements/1.1/"
ATOM_NS = "http://www.w3.org/2005/Atom"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
ANCHOR_NS = "https://anchor.fm/xmlns"

ET.register_namespace("itunes", ITUNES_NS)
ET.register_namespace("dc", DC_NS)
ET.register_namespace("atom", ATOM_NS)
ET.register_namespace("content", CONTENT_NS)
ET.register_namespace("anchor", ANCHOR_NS)


class PublishError(RuntimeError):
    pass


def run(command: list[str], cwd: Path | None = None, capture: bool = True) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )
    if completed.returncode != 0:
        message = completed.stderr or completed.stdout or "command failed"
        raise PublishError(message.strip())
    return completed


def repo_root() -> Path:
    try:
        out = run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def load_config(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise PublishError("PyYAML is required. Install with: python3 -m pip install --user pyyaml")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def require_command(name: str) -> str:
    resolved = shutil.which(name)
    if resolved:
        return resolved

    # Support the repo-local virtualenv created by tools/setup_podcast_env.sh.
    local_candidate = repo_root() / ".venv-podcast" / "bin" / name
    if local_candidate.exists() and os.access(local_candidate, os.X_OK):
        return str(local_candidate)

    if name == "ia":
        config_path = Path.home() / ".config" / "internetarchive" / "ia.ini"
        config_note = f" Config exists at {config_path}," if config_path.exists() else ""
        raise PublishError(
            f"Missing required command: ia.{config_note} but the CLI is not installed. "
            "Run: bash tools/setup_podcast_env.sh, or install Debian package: sudo apt install internetarchive"
        )
    raise PublishError(f"Missing required command: {name}")


def format_duration(seconds: float | int | None) -> str:
    total = int(round(float(seconds or 0)))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def rfc2822_from_upload_date(upload_date: str | None) -> str:
    if upload_date and re.fullmatch(r"\d{8}", upload_date):
        dt = datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
    else:
        dt = datetime.now(timezone.utc)
    return email.utils.format_datetime(dt, usegmt=True)


def safe_identifier(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-._")
    return value or "episode"


def safe_filename(value: str, suffix: str = ".mp3") -> str:
    value = re.sub(r"[\\/\0]+", "-", value).strip()
    value = re.sub(r"\s+", " ", value)
    if len(value.encode("utf-8")) > 180:
        value = value[:120].strip()
    value = value.strip(" .") or "episode"
    if not value.lower().endswith(suffix):
        value += suffix
    return value


def get_youtube_metadata(url: str) -> dict[str, Any]:
    yt_dlp = require_command("yt-dlp")
    completed = run([yt_dlp, "--dump-json", "--no-playlist", url])
    return json.loads(completed.stdout)


def download_mp3(url: str, output_dir: Path) -> Path:
    yt_dlp = require_command("yt-dlp")
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        yt_dlp,
        "--no-playlist",
        "-N",
        "4",
        "--continue",
        "--retries",
        "10",
        "--fragment-retries",
        "10",
        "-f",
        "ba/b",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--embed-metadata",
        "-P",
        str(output_dir),
        "-o",
        "%(title).180B [%(id)s].%(ext)s",
        "--print",
        "after_move:filepath",
        url,
    ]
    completed = run(command)
    paths = [Path(line.strip()) for line in completed.stdout.splitlines() if line.strip().endswith(".mp3")]
    if not paths:
        paths = sorted(output_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not paths or not paths[0].exists():
        raise PublishError("yt-dlp finished but no MP3 file was found")
    return paths[-1] if len(paths) == 1 else paths[0]


def probe_audio(path: Path) -> tuple[float, int]:
    ffprobe = require_command("ffprobe")
    completed = run([
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration,size",
        "-of",
        "json",
        str(path),
    ])
    data = json.loads(completed.stdout)
    fmt = data.get("format", {})
    return float(fmt.get("duration", 0)), int(fmt.get("size") or path.stat().st_size)


def archive_download_url(identifier: str, filename: str) -> str:
    quoted_filename = urllib.parse.quote(filename)
    return f"https://archive.org/download/{identifier}/{quoted_filename}"


def archive_direct_url_from_metadata(metadata: dict[str, Any], filename: str) -> str:
    server = str(metadata.get("server") or metadata.get("d1") or "").strip()
    directory = str(metadata.get("dir") or "").strip()
    if not server or not directory:
        raise PublishError("Archive.org metadata does not include server/dir for a direct file URL")
    quoted_filename = urllib.parse.quote(filename)
    return f"https://{server}{directory.rstrip('/')}/{quoted_filename}"


def get_archive_metadata(identifier: str) -> dict[str, Any]:
    ia = require_command("ia")
    completed = run([ia, "metadata", identifier])
    return json.loads(completed.stdout)


def upload_to_archive(mp3_path: Path, identifier: str, metadata: dict[str, str], dry_run: bool = False) -> str:
    filename = safe_filename(mp3_path.name)
    if dry_run:
        return archive_download_url(identifier, filename)
    ia = require_command("ia")
    if mp3_path.name != filename:
        target = mp3_path.with_name(filename)
        mp3_path.rename(target)
        mp3_path = target
    command = [ia, "upload", identifier, str(mp3_path), "--retries", "5"]
    for key, value in metadata.items():
        if value:
            command.append(f"--metadata={key}:{value}")
    run(command, capture=False)
    url = archive_download_url(identifier, filename)
    try:
        verify_archive_url(url)
    except PublishError:
        # Some archive.org items list the uploaded file but the generic
        # /download/<identifier>/<file> URL can briefly or persistently return
        # 404. The item metadata exposes the assigned storage host/path; use it
        # as a verified fallback enclosure URL.
        url = archive_direct_url_from_metadata(get_archive_metadata(identifier), filename)
        verify_archive_url(url)
    return url


def verify_archive_url(url: str, attempts: int = 10, delay_seconds: int = 10) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "podcast-publisher/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status < 400:
                    return
                last_error = PublishError(f"Archive.org URL returned HTTP {response.status}: {url}")
        except urllib.error.HTTPError as exc:
            last_error = exc
            # Archive.org can need a short propagation window right after upload.
            if exc.code not in {404, 503}:
                raise PublishError(f"Archive.org URL check failed: HTTP {exc.code} {url}") from exc
        except Exception as exc:
            last_error = exc
        if attempt < attempts:
            time.sleep(delay_seconds)
    raise PublishError(f"Archive.org URL is not available after {attempts} attempts: {url} ({last_error})")


def text(parent: ET.Element, tag: str, value: str, attrib: dict[str, str] | None = None) -> ET.Element:
    child = ET.SubElement(parent, tag, attrib or {})
    child.text = value or ""
    return child


def build_rss_item(
    metadata: dict[str, Any],
    archive_url: str,
    file_size: int,
    duration_seconds: float,
    creator: str,
    explicit: str,
) -> ET.Element:
    title = (metadata.get("title") or "Untitled episode").strip()
    description = (metadata.get("description") or title).strip()
    webpage_url = (metadata.get("webpage_url") or metadata.get("original_url") or "").strip()
    image_url = (metadata.get("thumbnail") or "").strip()

    item = ET.Element("item")
    text(item, "title", title)
    text(item, "description", description)
    text(item, "link", webpage_url)
    text(item, "guid", webpage_url, {"isPermaLink": "false"})
    text(item, f"{{{DC_NS}}}creator", creator)
    text(item, "pubDate", rfc2822_from_upload_date(metadata.get("upload_date")))
    ET.SubElement(item, "enclosure", {"url": archive_url, "length": str(int(file_size)), "type": "audio/mpeg"})
    text(item, f"{{{ITUNES_NS}}}summary", description)
    text(item, f"{{{ITUNES_NS}}}explicit", explicit)
    text(item, f"{{{ITUNES_NS}}}duration", format_duration(duration_seconds))
    if image_url:
        ET.SubElement(item, f"{{{ITUNES_NS}}}image", {"href": image_url})
    return item


def ensure_not_duplicate(tree: ET.ElementTree, guid: str) -> None:
    normalized = guid.strip()
    for item in tree.getroot().findall("./channel/item"):
        if (item.findtext("guid") or "").strip() == normalized:
            raise ValueError(f"Episode already exists in feed: {normalized}")


def insert_item_at_top(tree: ET.ElementTree, item: ET.Element) -> None:
    channel = tree.getroot().find("channel")
    if channel is None:
        raise ValueError("feed has no channel")
    first_item_index = None
    for index, child in enumerate(list(channel)):
        if child.tag == "item":
            first_item_index = index
            break
    channel.insert(first_item_index if first_item_index is not None else len(channel), item)


def update_channel_dates_and_self_link(tree: ET.ElementTree, self_url: str | None = None) -> None:
    channel = tree.getroot().find("channel")
    if channel is None:
        raise ValueError("feed has no channel")
    now = email.utils.format_datetime(datetime.now(timezone.utc), usegmt=True)
    last = channel.find("lastBuildDate")
    if last is None:
        last = ET.Element("lastBuildDate")
        channel.insert(0, last)
    last.text = now
    if self_url:
        for link in channel.findall(f"{{{ATOM_NS}}}link"):
            if link.attrib.get("rel") == "self":
                link.set("href", self_url)
                return
        ET.SubElement(channel, f"{{{ATOM_NS}}}link", {"href": self_url, "rel": "self", "type": "application/rss+xml"})


def write_tree(tree: ET.ElementTree, path: Path) -> None:
    ET.indent(tree, space="\t")
    tree.write(path, encoding="UTF-8", xml_declaration=True, short_empty_elements=True)


def update_manifest(path: Path, record: dict[str, Any]) -> None:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"episodes": []}
    data.setdefault("episodes", [])
    if not any(ep.get("youtube_id") == record.get("youtube_id") for ep in data["episodes"]):
        data["episodes"].insert(0, record)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_publish_record(
    metadata: dict[str, Any],
    youtube_id: str,
    identifier: str,
    archive_url: str,
    feed_path: str,
    dry_run: bool,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "youtube_url": metadata.get("webpage_url"),
        "youtube_id": youtube_id,
        "title": metadata.get("title"),
        "archive_identifier": identifier,
        "feed": feed_path,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "archive_url_available": not dry_run,
    }
    if dry_run:
        record["planned_archive_file_url"] = archive_url
        record["note"] = "dry-run only: this archive.org URL is a preview and will return 404 until a real upload is executed"
    else:
        record["archive_file_url"] = archive_url
    return record


def git_commit_and_push(paths: list[Path], message: str, push: bool = True) -> None:
    run(["git", "add", *[str(p) for p in paths]], capture=True)
    status = run(["git", "status", "--short"], capture=True).stdout.strip()
    if not status:
        print("No git changes to commit.")
        return
    run(["git", "commit", "-m", message], capture=False)
    if push:
        run(["git", "push", "origin", "HEAD"], capture=False)


def main(argv: list[str] | None = None) -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(description="Publish a YouTube video into the podcast RSS feed.")
    parser.add_argument("youtube_url", help="YouTube video URL")
    parser.add_argument("--config", type=Path, default=root / "tools" / "podcast_config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Do not upload, modify files, commit, or push")
    parser.add_argument("--no-git", action="store_true", help="Modify files but do not commit/push")
    parser.add_argument("--no-push", action="store_true", help="Commit locally but do not push")
    parser.add_argument("--work-dir", type=Path, default=None, help="Temporary working directory")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    podcast = config.get("podcast", {})
    archive = config.get("archive", {})
    git_cfg = config.get("git", {})

    feed_path = root / podcast.get("feed_path", "about/podcasts/saidkamlifeed.xml")
    manifest_path = root / podcast.get("manifest_path", "about/podcasts/publish_manifest.json")
    public_feed_url = podcast.get("public_feed_url")
    creator = podcast.get("creator", podcast.get("author", "eljoujat"))
    explicit = str(podcast.get("explicit", "No"))

    metadata = get_youtube_metadata(args.youtube_url)
    youtube_id = safe_identifier(str(metadata.get("id") or "youtube"))
    identifier = safe_identifier(f"{archive.get('identifier_prefix', 'podcast')}-{youtube_id}")
    webpage_url = metadata.get("webpage_url") or args.youtube_url
    metadata["webpage_url"] = webpage_url

    tree = ET.parse(feed_path)
    ensure_not_duplicate(tree, webpage_url)

    work_base = args.work_dir or Path(tempfile.mkdtemp(prefix="podcast-publish-"))
    episode_dir = work_base / identifier
    print(f"Working directory: {episode_dir}")

    mp3_path = download_mp3(args.youtube_url, episode_dir)
    duration_seconds, file_size = probe_audio(mp3_path)

    archive_metadata = {
        "title": str(metadata.get("title") or identifier),
        "mediatype": str(archive.get("mediatype", "audio")),
        "collection": str(archive.get("collection", "opensource_audio")),
        "creator": creator,
        "language": str(archive.get("language", "ara")),
        "subject": str(archive.get("subject", "islam;podcast;said kamli")),
        "description": str(metadata.get("description") or metadata.get("title") or ""),
    }
    archive_url = upload_to_archive(mp3_path, identifier, archive_metadata, dry_run=args.dry_run)

    item = build_rss_item(metadata, archive_url, file_size, duration_seconds, creator, explicit)
    insert_item_at_top(tree, item)
    update_channel_dates_and_self_link(tree, public_feed_url)

    record = build_publish_record(
        metadata=metadata,
        youtube_id=youtube_id,
        identifier=identifier,
        archive_url=archive_url,
        feed_path=str(feed_path.relative_to(root)),
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("DRY RUN: feed was not modified and archive.org upload was skipped.")
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0

    write_tree(tree, feed_path)
    update_manifest(manifest_path, record)

    # Validate after writing.
    from podcast_validate import validate_feed

    issues = validate_feed(feed_path, check_remote=False)
    if issues:
        raise PublishError("Feed validation failed after write:\n" + "\n".join(f"- {issue}" for issue in issues))

    if not args.no_git:
        message = f"{git_cfg.get('commit_prefix', 'podcast: publish episode')} {youtube_id}"
        git_commit_and_push([feed_path, manifest_path], message, push=not args.no_push)

    print("Episode published successfully.")
    print(f"Title: {metadata.get('title')}")
    print(f"YouTube: {webpage_url}")
    print(f"Archive.org: {archive_url}")
    print(f"Feed: {public_feed_url or feed_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
