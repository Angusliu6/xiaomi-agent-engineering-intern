"""Auditable keyword retrieval and rank fusion; intentionally dependency-free.

Not a neural embedding implementation. This deliberate constraint makes offline
benchmarks deterministic and exposes an honest B0/B1 comparison baseline.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import math
import re

TOKEN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_.-]*|\d+(?:\.\d+)?|[\u4e00-\u9fff]", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


@dataclass(frozen=True)
class Document:
    id: str
    text: str


@dataclass(frozen=True)
class Hit:
    id: str
    score: float
    text: str


class Corpus:
    def __init__(self, docs: list[Document]):
        if len({d.id for d in docs}) != len(docs):
            raise ValueError("duplicate document IDs")
        self.docs = sorted(docs, key=lambda d: d.id)
        self.tf = {d.id: Counter(tokenize(d.text)) for d in self.docs}
        self.length = {d.id: sum(self.tf[d.id].values()) for d in self.docs}
        self.avgdl = sum(self.length.values()) / max(len(docs), 1)
        self.df = Counter(t for d in self.docs for t in self.tf[d.id])

    @classmethod
    def from_dir(cls, root: Path) -> "Corpus":
        if not root.is_dir():
            raise ValueError(f"missing corpus directory: {root}")
        docs = []
        for p in sorted(root.rglob("*.md")):
            if p.is_symlink():
                continue
            docs.append(Document(p.relative_to(root).as_posix(), p.read_text(encoding="utf-8")))
        if not docs:
            raise ValueError("empty corpus")
        return cls(docs)

    def search(self, query: str, k: int = 5, mode: str = "bm25") -> list[Hit]:
        if not 1 <= k <= 50:
            raise ValueError("k must be between 1 and 50")
        if mode not in ("bm25", "hybrid"):
            raise ValueError("mode must be bm25 or hybrid")
        if not query.strip():
            return []
        bm = self._bm25(query)
        if mode == "bm25":
            scores = bm
        else:
            # Character overlap complements BM25 on identifiers, stack traces
            # and camel-case fragments. This is NOT an embedding model.
            chars = self._char_overlap(query)
            scores = Counter()
            for ranking in (bm, chars):
                ranked = sorted(ranking, key=lambda d: (-ranking[d], d))
                for rank, doc_id in enumerate(ranked, 1):
                    if ranking[doc_id] > 0:
                        scores[doc_id] += 1 / (60 + rank)
        index = {d.id: d.text for d in self.docs}
        return [Hit(doc_id, round(score, 8), index[doc_id])
                for doc_id, score in sorted(scores.items(), key=lambda x: (-x[1], x[0]))[:k]
                if score > 0]

    def _bm25(self, query: str) -> dict[str, float]:
        q = set(tokenize(query)); n = len(self.docs); scores = {}
        for d in self.docs:
            s = 0.0
            for t in q:
                if not (freq := self.tf[d.id].get(t, 0)):
                    continue
                idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * freq * 2.2 / (freq + 1.2 * (0.25 + 0.75 * self.length[d.id] / max(self.avgdl, 1)))
            scores[d.id] = s
        return scores

    def _char_overlap(self, query: str) -> dict[str, float]:
        def grams(t: str):
            return set(t[i:i+3] for i in range(max(0, len(t)-2)))
        # Avoid O(N) giant raw-text comparisons in production; demonstration only.
        q = grams(query.lower())
        return {d.id: (v if v >= 0.35 else 0.0) for d in self.docs for v in [float(len(q & grams(d.text.lower()))) / max(len(q), 1)]}
