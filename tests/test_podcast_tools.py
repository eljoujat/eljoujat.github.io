import email.utils
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def load_module(name):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PodcastToolTests(unittest.TestCase):
    def setUp(self):
        self.publish = load_module("podcast_publish")
        self.validate = load_module("podcast_validate")

    def minimal_feed(self):
        return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\" xmlns:atom=\"http://www.w3.org/2005/Atom\" version=\"2.0\">
  <channel>
    <title>Test Podcast</title>
    <atom:link href=\"https://example.com/feed.xml\" rel=\"self\" type=\"application/rss+xml\"/>
    <link>https://example.com</link>
    <description>Desc</description>
    <language>ar</language>
    <itunes:author>eljoujat</itunes:author>
    <itunes:explicit>No</itunes:explicit>
    <itunes:image href=\"https://example.com/cover.jpg\"/>
    <item>
      <title>Old</title>
      <guid isPermaLink=\"false\">https://www.youtube.com/watch?v=OLD123</guid>
      <enclosure url=\"https://archive.org/download/old/old.mp3\" length=\"123\" type=\"audio/mpeg\"/>
      <itunes:duration>00:01:00</itunes:duration>
    </item>
  </channel>
</rss>
"""

    def test_build_rss_item_contains_required_podcast_fields(self):
        metadata = {
            "title": "عنوان عربي & test",
            "description": "وصف الحلقة",
            "webpage_url": "https://www.youtube.com/watch?v=ABC123xyz00",
            "thumbnail": "https://img.youtube.com/vi/ABC123xyz00/hqdefault.jpg",
            "upload_date": "20260928",
        }
        item = self.publish.build_rss_item(
            metadata=metadata,
            archive_url="https://archive.org/download/saidkamli-ABC123xyz00/episode.mp3",
            file_size=987654,
            duration_seconds=3723.2,
            creator="eljoujat",
            explicit="No",
        )
        self.assertEqual(item.findtext("title"), "عنوان عربي & test")
        self.assertEqual(item.findtext("guid"), metadata["webpage_url"])
        self.assertEqual(item.find("guid").attrib["isPermaLink"], "false")
        self.assertEqual(item.find("enclosure").attrib["type"], "audio/mpeg")
        self.assertEqual(item.find("enclosure").attrib["length"], "987654")
        self.assertEqual(item.findtext("{http://www.itunes.com/dtds/podcast-1.0.dtd}duration"), "01:02:03")
        self.assertEqual(item.find("{http://www.itunes.com/dtds/podcast-1.0.dtd}image").attrib["href"], metadata["thumbnail"])
        email.utils.parsedate_to_datetime(item.findtext("pubDate"))

    def test_insert_item_at_top_and_prevent_duplicate_guid(self):
        with tempfile.TemporaryDirectory() as tmp:
            feed = Path(tmp) / "feed.xml"
            feed.write_text(self.minimal_feed(), encoding="utf-8")
            tree = ET.parse(feed)
            item = self.publish.build_rss_item(
                metadata={
                    "title": "New",
                    "description": "New desc",
                    "webpage_url": "https://www.youtube.com/watch?v=NEW123xyz00",
                    "upload_date": "20260928",
                },
                archive_url="https://archive.org/download/new/new.mp3",
                file_size=42,
                duration_seconds=61,
                creator="eljoujat",
                explicit="No",
            )
            self.publish.ensure_not_duplicate(tree, "https://www.youtube.com/watch?v=NEW123xyz00")
            self.publish.insert_item_at_top(tree, item)
            channel = tree.getroot().find("channel")
            self.assertEqual(channel.findall("item")[0].findtext("title"), "New")
            with self.assertRaises(ValueError):
                self.publish.ensure_not_duplicate(tree, "https://www.youtube.com/watch?v=NEW123xyz00")

    def test_archive_download_url_quotes_arabic_filename(self):
        url = self.publish.archive_download_url("saidkamli-abc", "عنوان الحلقة test.mp3")
        self.assertEqual(url, "https://archive.org/download/saidkamli-abc/%D8%B9%D9%86%D9%88%D8%A7%D9%86%20%D8%A7%D9%84%D8%AD%D9%84%D9%82%D8%A9%20test.mp3")

    def test_dry_run_record_does_not_claim_archive_url_is_published(self):
        record = self.publish.build_publish_record(
            metadata={"title": "Test", "webpage_url": "https://www.youtube.com/watch?v=ABC123xyz00"},
            youtube_id="ABC123xyz00",
            identifier="saidkamli-abc123xyz00",
            archive_url="https://archive.org/download/saidkamli-abc123xyz00/episode.mp3",
            feed_path="about/podcasts/saidkamlifeed.xml",
            dry_run=True,
        )
        self.assertNotIn("archive_file_url", record)
        self.assertEqual(record["planned_archive_file_url"], "https://archive.org/download/saidkamli-abc123xyz00/episode.mp3")
        self.assertFalse(record["archive_url_available"])

    def test_real_publish_record_contains_archive_file_url(self):
        record = self.publish.build_publish_record(
            metadata={"title": "Test", "webpage_url": "https://www.youtube.com/watch?v=ABC123xyz00"},
            youtube_id="ABC123xyz00",
            identifier="saidkamli-abc123xyz00",
            archive_url="https://archive.org/download/saidkamli-abc123xyz00/episode.mp3",
            feed_path="about/podcasts/saidkamlifeed.xml",
            dry_run=False,
        )
        self.assertEqual(record["archive_file_url"], "https://archive.org/download/saidkamli-abc123xyz00/episode.mp3")
        self.assertNotIn("planned_archive_file_url", record)
        self.assertTrue(record["archive_url_available"])

    def test_verify_archive_url_retries_transient_404(self):
        class FakeResponse:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False

        calls = {"count": 0}

        def fake_urlopen(request, timeout):
            calls["count"] += 1
            if calls["count"] < 3:
                raise self.publish.urllib.error.HTTPError(
                    url="https://archive.org/download/example/file.mp3",
                    code=404,
                    msg="Not Found",
                    hdrs=None,
                    fp=None,
                )
            return FakeResponse()

        with mock.patch.object(self.publish.urllib.request, "urlopen", side_effect=fake_urlopen), \
             mock.patch.object(self.publish.time, "sleep"):
            self.publish.verify_archive_url("https://archive.org/download/example/file.mp3", attempts=3, delay_seconds=0)

        self.assertEqual(calls["count"], 3)

    def test_validate_feed_reports_duplicate_guid_and_bad_enclosure_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            feed = Path(tmp) / "feed.xml"
            content = self.minimal_feed().replace("length=\"123\"", "length=\"abc\"")
            content = content.replace("</channel>", """
    <item>
      <title>Duplicate</title>
      <guid isPermaLink=\"false\">https://www.youtube.com/watch?v=OLD123</guid>
      <enclosure url=\"https://archive.org/download/dup/dup.mp3\" length=\"456\" type=\"audio/mpeg\"/>
      <itunes:duration>00:02:00</itunes:duration>
    </item>
  </channel>""")
            feed.write_text(content, encoding="utf-8")
            issues = self.validate.validate_feed(feed, check_remote=False)
            self.assertTrue(any("duplicate guid" in issue.lower() for issue in issues))
            self.assertTrue(any("invalid enclosure length" in issue.lower() for issue in issues))


if __name__ == "__main__":
    unittest.main()
