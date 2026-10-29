"""Keep the five latest public Tistory posts in the profile README."""

from html import escape
from html.parser import HTMLParser
from pathlib import Path
from collections.abc import Callable
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

FEED_URL = "https://djseo98.tistory.com/rss"
IT_TOPIC = "IT 인터넷"
START = "<!-- BLOG-POSTS:START -->"
END = "<!-- BLOG-POSTS:END -->"


def parse_topic(html: bytes) -> str:
    class TopicParser(HTMLParser):
        topic = ""

        def handle_starttag(self, tag, attrs):
            if tag == "meta":
                attributes = dict(attrs)
                if attributes.get("property") == "article:section":
                    self.topic = (attributes.get("content") or "").strip().strip("'\"").strip()

    parser = TopicParser()
    parser.feed(html.decode("utf-8"))
    if not parser.topic:
        raise ValueError("Post topic is unavailable; keeping the existing README")
    return parser.topic


def fetch_topic(url: str) -> str:
    request = Request(url, headers={"User-Agent": "eastjin616-profile-blog-sync"})
    with urlopen(request, timeout=30) as response:
        if urlsplit(response.geturl()).netloc != "djseo98.tistory.com":
            raise ValueError("Post redirected outside the blog; keeping the existing README")
        html = response.read(1_000_001)
    if len(html) > 1_000_000:
        raise ValueError("Post page is unexpectedly large; keeping the existing README")
    return parse_topic(html)


def parse_posts(xml: bytes, topic_for_url: Callable[[str], str]) -> list[tuple[str, str]]:
    try:
        items = ET.fromstring(xml).findall("./channel/item")
    except ET.ParseError as exc:
        raise ValueError("RSS is not valid XML; keeping the existing README") from exc
    posts = []
    seen = set()
    for item in items:
        title = " ".join((item.findtext("title") or "").split())
        link = urlsplit((item.findtext("link") or "").strip())
        if not title or link.scheme not in ("http", "https") or link.netloc != "djseo98.tistory.com":
            raise ValueError("RSS contains an invalid post; keeping the existing README")
        url = urlunsplit(("https", link.netloc, link.path, link.query, ""))
        if url in seen:
            continue
        seen.add(url)
        if topic_for_url(url) != IT_TOPIC:
            continue
        posts.append((title, url))
        if len(posts) == 5:
            break
    if not posts:
        raise ValueError("RSS contains no posts; keeping the existing README")
    return posts


def update_readme(readme: str, posts: list[tuple[str, str]]) -> str:
    if not posts:
        raise ValueError("Refusing to replace the post list with an empty list")
    entries = "\n".join(
        f'    <li><a href="{escape(url, quote=True)}">{escape(title)}</a></li>'
        for title, url in posts
    )
    block = (
        f'{START}\n<h3>📕 Latest Blog Posts</h3>\n<ul>\n'
        f'{entries}\n</ul>\n{END}'
    )
    if START in readme or END in readme:
        if readme.count(START) != 1 or readme.count(END) != 1:
            raise ValueError("README blog markers are incomplete or duplicated")
        start, end = readme.index(START), readme.index(END)
        if end < start:
            raise ValueError("README blog markers are in the wrong order")
        return readme[:start] + block + readme[end + len(END):]
    anchor = '<div align="center">\n  <h2>GitHub Stats</h2>'
    if anchor in readme:
        return readme.replace(anchor, block + "\n\n<br />\n\n" + anchor, 1)
    return readme.rstrip() + "\n\n" + block + "\n"


def main() -> None:
    request = Request(FEED_URL, headers={"User-Agent": "eastjin616-profile-blog-sync"})
    with urlopen(request, timeout=30) as response:
        xml = response.read(2_000_001)
    if len(xml) > 2_000_000:
        raise ValueError("RSS response is unexpectedly large")
    posts = parse_posts(xml, fetch_topic)
    path = Path("README.md")
    original = path.read_text(encoding="utf-8")
    updated = update_readme(original, posts)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        print(f"Updated README with {len(posts)} blog posts")
    else:
        print("Blog posts unchanged; no commit needed")


if __name__ == "__main__":
    main()
