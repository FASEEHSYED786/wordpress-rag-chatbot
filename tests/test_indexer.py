from wp_rag import SiteIndex, strip_html

POSTS = [
    {"link": "https://x/a", "title": {"rendered": "Shipping &amp; Returns"}, "content": {"rendered": "<p>We ship within <b>3 days</b>. Returns accepted for 30 days.</p>"}},
    {"link": "https://x/b", "title": {"rendered": "About us"}, "content": {"rendered": "<p>We are a small team in Cambridge.</p>"}},
]


def test_strip():
    assert strip_html("<p>a &amp; b</p>") == "a & b"


def test_answer_links_source():
    i = SiteIndex()
    assert i.load_posts(POSTS) == 2
    assert i.answer("how long do returns take")["sources"][0]["url"] == "https://x/a"


def test_no_hit():
    i = SiteIndex()
    i.load_posts(POSTS)
    assert i.answer("quantum physics")["sources"] == []
