"""Indexes WordPress posts (from the REST API JSON) and answers questions with source links."""
import html
import math
import re
from collections import Counter

W = re.compile(r"[a-z0-9]+")


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


class SiteIndex:
    def __init__(self):
        self.docs: list[dict] = []

    def load_posts(self, posts: list[dict]) -> int:
        """posts: WP REST shape {'link', 'title': {'rendered'}, 'content': {'rendered'}}."""
        for p in posts:
            title, body = strip_html(p["title"]["rendered"]), strip_html(p["content"]["rendered"])
            toks = W.findall((title + " " + title + " " + body).lower())
            self.docs.append({"title": title, "link": p["link"], "body": body, "tf": Counter(toks)})
        return len(self.docs)

    def search(self, q: str, k: int = 3):
        n, qt = len(self.docs), W.findall(q.lower())
        df = {t: sum(1 for d in self.docs if t in d["tf"]) for t in qt}
        scored = []
        for d in self.docs:
            s = sum(math.log(1 + n / df[t]) * (1 + math.log(d["tf"][t])) for t in qt if df.get(t) and t in d["tf"])
            if s > 0:
                scored.append((s, d))
        return [d for _, d in sorted(scored, key=lambda x: -x[0])[:k]]

    def answer(self, q: str) -> dict:
        hits = self.search(q)
        if not hits:
            return {"answer": "I could not find that on this site.", "sources": []}
        return {
            "answer": hits[0]["body"][:280],
            "sources": [{"title": h["title"], "url": h["link"]} for h in hits],
        }
