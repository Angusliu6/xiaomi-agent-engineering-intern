"""Bounded, auditable search agent with checkpoint / resume and strict tool policy.

Offline mode uses a *deterministic policy*, not an LLM. Optional model-backed
planner in `llm.py` may supply search/finish decisions. Never claim that
offline heuristics represent learned reasoning.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import Counter
import json
import sqlite3
import time
import uuid
from contextlib import closing
from typing import Protocol
from .retrieval import Corpus, Hit, tokenize


@dataclass
class Event:
    step: int
    kind: str
    payload: dict


@dataclass
class State:
    run_id: str
    query: str
    mode: str
    budget: int
    status: str = "running"
    step: int = 0
    retrieved: list[str] = field(default_factory=list)
    observations: list[dict] = field(default_factory=list)
    attempted: list[str] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    answer: str = ""
    citations: list[str] = field(default_factory=list)
    elapsed_ms: float = 0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, obj: dict):
        obj = dict(obj)
        obj["events"] = [Event(**e) for e in obj.get("events", [])]
        return cls(**obj)


class CheckpointStore:
    """SQLite single-task checkpoints; atomic writes, not exactly-once external actions."""
    def __init__(self, db: Path):
        db.parent.mkdir(parents=True, exist_ok=True)
        self.db = db
        with closing(sqlite3.connect(db)) as c:
            c.execute("CREATE TABLE IF NOT EXISTS checkpoints (run_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            c.commit()

    def save(self, state: State):
        with closing(sqlite3.connect(self.db)) as c:
            c.execute("INSERT OR REPLACE INTO checkpoints VALUES (?, ?)",
                      (state.run_id, json.dumps(state.to_dict(), ensure_ascii=False)))
            c.commit()

    def load(self, run_id: str) -> State:
        with closing(sqlite3.connect(self.db)) as c:
            row = c.execute("SELECT payload FROM checkpoints WHERE run_id=?", (run_id,)).fetchone()
        if not row:
            raise KeyError(f"unknown run_id: {run_id}")
        return State.from_dict(json.loads(row[0]))


class SearchPlanner(Protocol):
    def next_query(self, state: State) -> str | None: ...


class DeterministicPlanner:
    """Rule-based *reference* search controller for offline replay.

    Splitting a query after a failed initial search is a testable heuristic,
    not an LLM agent's tool-selection ability.
    """
    def next_query(self, state: State) -> str | None:
        if not state.attempted:
            return state.query
        parts = [t for t in tokenize(state.query) if len(t) > 3]
        # Query narrowing, guarded against repeated equivalent queries.
        for p in sorted(set(parts), key=lambda x: (-len(x), x)):
            if p not in state.attempted:
                return p
        return None


class ToolError(RuntimeError):
    pass


class PlannerError(RuntimeError):
    """Recoverable planning-provider/schema failure, not absence of evidence."""
    pass


class ReadOnlyTools:
    def __init__(self, corpus: Corpus, fail_first: bool = False):
        self.corpus = corpus
        self.fail_first = fail_first
        self.calls = 0

    def search_docs(self, query: str, top_k: int, mode: str) -> list[Hit]:
        if not isinstance(query, str) or len(query) > 1000 or not query.strip():
            raise ToolError("invalid query")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 20:
            raise ToolError("invalid top_k")
        self.calls += 1
        if self.fail_first and self.calls == 1:
            raise ToolError("injected transient search failure")
        return self.corpus.search(query, top_k, mode)


class Agent:
    def __init__(self, tools: ReadOnlyTools, *, store: CheckpointStore | None = None,
                 planner: SearchPlanner | None = None):
        self.tools = tools
        self.store = store
        self.planner = planner or DeterministicPlanner()

    def run(self, query: str, *, mode: str = "hybrid", budget: int = 3,
            resume: str | None = None) -> State:
        if not isinstance(query, str) or not query.strip() or len(query) > 1000:
            raise ValueError("query must contain 1-1000 characters")
        if mode not in ("bm25", "hybrid"):
            raise ValueError("unknown retrieval mode")
        if not 1 <= budget <= 8:
            raise ValueError("budget must be between 1 and 8")
        state = self.store.load(resume) if resume and self.store else State(str(uuid.uuid4()), query, mode, budget)
        if resume and not self.store:
            raise ValueError("resuming requires checkpoint store")
        if resume and (state.query != query or state.mode != mode or state.budget != budget):
            raise ValueError("resume config mismatch")
        if state.status != "running":
            return state
        start = time.perf_counter()
        docs = {d.id: d for d in self.tools.corpus.docs}
        # Recovery of a completed checkpoint is handled above. A crash after
        # tool_start but before tool_result is replayed ONLY because search_docs
        # is a read-only/idempotent operation. Never generalize to mutations.
        pending = bool(state.events) and state.events[-1].kind == "tool_start"
        planner_failed = False
        while state.step < state.budget or pending:
            if pending:
                q = state.events[-1].payload["query"]
                pending = False
                state.events.append(Event(state.step, "tool_replay", {"query": q, "read_only": True}))
            else:
                try:
                    q = self.planner.next_query(state)
                except PlannerError as exc:
                    # A provider failure must not be mislabeled as "no evidence".
                    state.events.append(Event(state.step, "planner_error", {"error": str(exc)[:160]}))
                    planner_failed = True
                    break
                if q is None or q in state.attempted:
                    break
                if not isinstance(q, str) or not q.strip() or len(q) > 1000:
                    state.events.append(Event(state.step, "planner_error", {"error": "invalid planner query"}))
                    planner_failed = True
                    break
                state.attempted.append(q)
                state.step += 1
                state.events.append(Event(state.step, "tool_start", {"name": "search_docs", "query": q}))
            if self.store:
                self.store.save(state)  # durable intent; idempotent read-only replay
            try:
                hits = self.tools.search_docs(q, 5, state.mode)
            except ToolError as exc:
                state.events.append(Event(state.step, "tool_error", {"error": str(exc)}))
                if self.store:
                    self.store.save(state)
                continue
            state.events.append(Event(state.step, "tool_result", {"ids": [h.id for h in hits]}))
            # Short untrusted snippets let an optional model planner adapt on
            # observations, not just opaque file IDs. Never execute source text.
            state.observations = [{"id": hit.id, "snippet": hit.text[:160]} for hit in hits[:3]]
            for hit in hits:
                if hit.id not in state.retrieved:
                    state.retrieved.append(hit.id)
            supported = [hit.id for hit in hits if self._basic_evidence_gate(state.query, hit.text)]
            state.events.append(Event(state.step, "evidence_gate", {"supported_ids": supported,
                "warning": "lexical heuristic, not claim-level grounding"}))
            if self.store:
                self.store.save(state)
            # Weak lexical evidence gate: catches some accidental noise, but
            # cannot establish factual entailment or answer correctness.
            if supported:
                state.citations = supported[:3]
                break
        state.citations = [d for d in state.citations if d in docs][:3]
        if planner_failed:
            state.answer = "规划器执行失败：未完成证据核验，请检查模型端点与调用日志。"
            state.status = "planning_failed"
        elif state.citations:
            # Conservative extractive evidence: no model synthesis, no invented diagnosis.
            state.answer = "候选证据（尚需人工判断因果关系）：\n" + "\n".join(
                f"[{doc_id}] {self._excerpt(docs[doc_id].text, query)}" for doc_id in state.citations)
            state.status = "evidence_found"
        else:
            state.answer = "证据不足：没有找到可靠的文档支持，不能据此下诊断结论。"
            state.status = "insufficient_evidence"
        state.elapsed_ms += round((time.perf_counter() - start) * 1000, 3)
        state.events.append(Event(state.step, "finish", {"status": state.status}))
        if self.store:
            self.store.save(state)
        return state

    @staticmethod
    def _basic_evidence_gate(query: str, text: str) -> bool:
        stop = {"what", "when", "where", "the", "from", "does", "with", "have",
                "about", "should", "could", "would", "after", "into", "your",
                "this", "that", "were", "there", "which", "many", "some", "other"}
        q = {t for t in tokenize(query) if len(t) >= 4 and t not in stop}
        if not q:
            return False
        match = q & set(tokenize(text))
        required = 1 if len(q) <= 2 else max(2, (len(q) + 2) // 3)
        return len(match) >= required

    @staticmethod
    def _excerpt(text: str, query: str) -> str:
        # Source treated as untrusted DATA, not system prompt. Keep short.
        q = set(tokenize(query))
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        best = max(lines, key=lambda line: len(q & set(tokenize(line))), default="")
        return best[:240]
