from html.parser import HTMLParser
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "destinations.html", "routes.html", "gallery.html", "planner.html"]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.images = []
        self.navigation = []
        self.in_navigation = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append(tag)
        if tag == "nav":
            self.in_navigation = True
        if tag == "a":
            href = attributes.get("href", "")
            self.links.append(href)
            if self.in_navigation:
                self.navigation.append(href)
        if tag == "img":
            self.images.append(attributes)

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_navigation = False


class SiteTests(unittest.TestCase):
    def test_pages_have_navigation_and_semantic_structure(self):
        for page in PAGES:
            with self.subTest(page=page):
                parser = PageParser()
                parser.feed((ROOT / page).read_text(encoding="utf-8"))
                self.assertEqual(parser.navigation, PAGES)
                for tag in ("header", "nav", "main", "footer", "h1"):
                    self.assertIn(tag, parser.tags)
                for href in parser.links:
                    if href.startswith(("http://", "https://", "#")):
                        continue
                    self.assertTrue((ROOT / href.split("#")[0]).is_file(), href)
                for image in parser.images:
                    self.assertTrue(image.get("alt"))
                    self.assertTrue((ROOT / image["src"]).is_file())

    def test_required_elements_and_assets(self):
        routes = PageParser()
        routes.feed((ROOT / "routes.html").read_text(encoding="utf-8"))
        planner = PageParser()
        planner.feed((ROOT / "planner.html").read_text(encoding="utf-8"))
        self.assertIn("table", routes.tags)
        self.assertIn("form", planner.tags)
        self.assertIn("fieldset", planner.tags)
        self.assertTrue((ROOT / "vendor/bootstrap.min.css").is_file())
        for asset in (ROOT / "assets").glob("*.svg"):
            ET.parse(asset)

    def test_responsive_styles(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("display: flex", css)
        self.assertIn("display: grid", css)
        self.assertIn("@media (max-width: 991px)", css)
        self.assertIn("@media (max-width: 639px)", css)


if __name__ == "__main__":
    unittest.main()
