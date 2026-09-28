#!/usr/bin/env python3
"""Validate a podcast RSS feed used by this GitHub Pages repository."""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def validate_feed(feed_path: str | Path, check_remote: bool = False, timeout: int = 10) -> list[str]:
    """Return a list of validation issues. Empty list means OK."""
    path = Path(feed_path)
    issues: list[str] = []

    if not path.exists():
        return [f"feed does not exist: {path}"]

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"]

    root = tree.getroot()
    if root.tag != "rss":
        issues.append(f"root element should be rss, got {root.tag!r}")
    channel = root.find("channel")
    if channel is None:
        issues.append("missing channel element")
        return issues

    for field in ["title", "description", "link", "language"]:
        if not (channel.findtext(field) or "").strip():
            issues.append(f"channel missing {field}")

    items = channel.findall("item")
    if not items:
        issues.append("feed contains no items")

    seen_guids: set[str] = set()
    for index, item in enumerate(items, start=1):
        prefix = f"item {index}"
        title = (item.findtext("title") or "").strip()
        guid = (item.findtext("guid") or "").strip()
        duration = (item.findtext(f"{{{ITUNES_NS}}}duration") or "").strip()
        enclosure = item.find("enclosure")

        if not title:
            issues.append(f"{prefix}: missing title")
        if not guid:
            issues.append(f"{prefix}: missing guid")
        elif guid in seen_guids:
            issues.append(f"{prefix}: duplicate guid: {guid}")
        else:
            seen_guids.add(guid)

        if enclosure is None:
            issues.append(f"{prefix}: missing enclosure")
        else:
            url = enclosure.attrib.get("url", "").strip()
            length = enclosure.attrib.get("length", "").strip()
            media_type = enclosure.attrib.get("type", "").strip()
            if not url:
                issues.append(f"{prefix}: enclosure missing url")
            if not length.isdigit() or int(length or 0) <= 0:
                issues.append(f"{prefix}: invalid enclosure length: {length!r}")
            if not media_type.startswith("audio/"):
                issues.append(f"{prefix}: enclosure type is not audio/*: {media_type!r}")
            if check_remote and url:
                try:
                    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "podcast-validator/1.0"})
                    with urllib.request.urlopen(request, timeout=timeout) as response:
                        if response.status >= 400:
                            issues.append(f"{prefix}: enclosure HTTP status {response.status}: {url}")
                except Exception as exc:  # network validators should report, not crash
                    issues.append(f"{prefix}: enclosure URL check failed: {url} ({exc})")

        if not duration:
            issues.append(f"{prefix}: missing itunes:duration")

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate podcast RSS feed structure.")
    parser.add_argument("feed", type=Path, help="Path to RSS/XML feed")
    parser.add_argument("--check-remote", action="store_true", help="HEAD-check enclosure URLs; slower and network-dependent")
    args = parser.parse_args(argv)

    issues = validate_feed(args.feed, check_remote=args.check_remote)
    if issues:
        print(f"Podcast feed validation failed: {args.feed}", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print(f"Podcast feed validation OK: {args.feed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
