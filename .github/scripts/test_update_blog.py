import unittest
from update_blog import parse_posts, parse_topic, update_readme


class BlogUpdateTests(unittest.TestCase):
    def test_feed_limits_to_five_and_normalizes_links(self):
        xml = "<rss><channel>" + "".join(
            f"<item><category>Backend</category><title>글 {i}</title><link>http://djseo98.tistory.com/{i}</link></item>"
            for i in range(1, 8)
        ) + "</channel></rss>"
        self.assertEqual(parse_posts(xml.encode(), lambda url: "IT 인터넷"), [
            ("글 1", "https://djseo98.tistory.com/1"),
            ("글 2", "https://djseo98.tistory.com/2"),
            ("글 3", "https://djseo98.tistory.com/3"),
            ("글 4", "https://djseo98.tistory.com/4"),
            ("글 5", "https://djseo98.tistory.com/5"),
        ])

    def test_only_it_topic_posts_count_towards_five(self):
        xml = b'''<rss><channel>
          <item><category>ilsang</category><title>Diary</title><link>https://djseo98.tistory.com/99</link></item>
          <item><title>Docker Compose 2</title><link>https://djseo98.tistory.com/16</link></item>
          <item><category>Frontend/React</category><title>React</title><link>https://djseo98.tistory.com/8</link></item>
          <item><category>Infra/docker</category><title>Docker 1</title><link>https://djseo98.tistory.com/7</link></item>
          <item><category>Backend/Spring</category><title>Spring</title><link>https://djseo98.tistory.com/6</link></item>
          <item><category>Backend</category><title>Not IT</title><link>https://djseo98.tistory.com/5</link></item>
          <item><category>Infra</category><title>Infra</title><link>https://djseo98.tistory.com/4</link></item>
          <item><category>Infra/docker</category><title>Docker 2</title><link>https://djseo98.tistory.com/3</link></item>
          <item><category>Backend</category><title>Older</title><link>https://djseo98.tistory.com/2</link></item>
        </channel></rss>'''
        checked = []
        def topic_for_url(url):
            checked.append(url)
            return "일상" if url.endswith(("/99", "/5")) else "IT 인터넷"

        self.assertEqual(parse_posts(xml, topic_for_url), [
            ("Docker Compose 2", "https://djseo98.tistory.com/16"),
            ("React", "https://djseo98.tistory.com/8"),
            ("Docker 1", "https://djseo98.tistory.com/7"),
            ("Spring", "https://djseo98.tistory.com/6"),
            ("Infra", "https://djseo98.tistory.com/4"),
        ])
        self.assertNotIn("https://djseo98.tistory.com/3", checked)

    def test_topic_is_read_from_public_post_metadata(self):
        self.assertEqual(parse_topic(b'<meta property="article:section" content="\'IT \xec\x9d\xb8\xed\x84\xb0\xeb\x84\xb7\'">'), "IT 인터넷")
        self.assertEqual(parse_topic('<meta content="일상다반사" property="article:section">'.encode()), "일상다반사")
        with self.assertRaises(ValueError):
            parse_topic(b'<html><head></head></html>')

    def test_insertion_preserves_profile_and_is_idempotent(self):
        original = '<h1>Jin</h1>\n\n<div align="center">\n  <h2>GitHub Stats</h2>\n</div>\n'
        result = update_readme(original, [("Docker", "https://djseo98.tistory.com/1")])
        self.assertTrue(result.startswith("<h1>Jin</h1>\n\n<!-- BLOG-POSTS:START -->"))
        self.assertTrue(result.endswith('<div align="center">\n  <h2>GitHub Stats</h2>\n</div>\n'))
        self.assertIn('<a href="https://djseo98.tistory.com/1">Docker</a>', result)
        self.assertEqual(update_readme(result, [("Docker", "https://djseo98.tistory.com/1")]), result)

    def test_changed_posts_replace_old_list(self):
        before = "Header\n<!-- BLOG-POSTS:START -->\nold\n<!-- BLOG-POSTS:END -->\nFooter"
        result = update_readme(before, [("새 글", "https://djseo98.tistory.com/9")])
        self.assertNotIn("\nold\n", result)
        self.assertEqual(result.count("BLOG-POSTS:START"), 1)
        self.assertTrue(result.startswith("Header\n"))
        self.assertTrue(result.endswith("\nFooter"))

    def test_titles_are_escaped_as_text(self):
        result = update_readme("Profile", [('Docker <script> & "volume"', "https://djseo98.tistory.com/1")])
        self.assertIn('Docker &lt;script&gt; &amp; &quot;volume&quot;', result)
        self.assertNotIn("<script>", result)

    def test_empty_malformed_or_untrusted_feed_is_rejected(self):
        for xml in [
            b"<rss><channel/></rss>",
            b"not xml",
            b"<rss><channel><item><category>Infra</category><title>Bad</title><link>javascript:alert(1)</link></item></channel></rss>",
            b"<rss><channel><item><category>Infra</category><title>Bad</title><link>https://other.example/1</link></item></channel></rss>",
        ]:
            with self.subTest(xml=xml), self.assertRaises(ValueError):
                parse_posts(xml, lambda url: "IT 인터넷")

    def test_broken_markers_are_rejected(self):
        for text in [
            "<!-- BLOG-POSTS:START -->missing end",
            "<!-- BLOG-POSTS:END -->",
            "<!-- BLOG-POSTS:END --><!-- BLOG-POSTS:START -->",
            "<!-- BLOG-POSTS:START --><!-- BLOG-POSTS:START --><!-- BLOG-POSTS:END -->",
        ]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                update_readme(text, [("Docker", "https://djseo98.tistory.com/1")])


if __name__ == "__main__":
    unittest.main()
