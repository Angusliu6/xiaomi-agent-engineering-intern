"""CLI: offline by default, explicit opt-in to external model endpoint."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .retrieval import Corpus
from .runtime import Agent, CheckpointStore, ReadOnlyTools
from .evaluation import load_cases, measure, paired_compare
from .llm import OpenAICompatiblePlanner

ROOT = Path(__file__).resolve().parents[2]

def main(argv=None):
    parser = argparse.ArgumentParser(description="TRACE-QA engineering evidence agent")
    parser.add_argument("--corpus", type=Path, default=ROOT/"data/corpus")
    commands = parser.add_subparsers(dest="cmd", required=True)
    ask = commands.add_parser("ask", help="read-only evidence investigation")
    ask.add_argument("query")
    ask.add_argument("--mode", choices=["bm25","hybrid"], default="hybrid")
    ask.add_argument("--budget", type=int, default=3)
    ask.add_argument("--db", type=Path, default=Path(".traceqa/checkpoints.sqlite"))
    ask.add_argument("--resume", default=None, help="existing run_id")
    ask.add_argument("--llm-url", default=None, help="explicit opt-in OpenAI-compatible base URL ending in /v1")
    ask.add_argument("--model", default=None)
    ev = commands.add_parser("eval", help="retrieval-only gold-ID benchmark")
    ev.add_argument("--cases", type=Path, default=ROOT/"data/benchmark.jsonl")
    ev.add_argument("--variant", choices=["b0","b1","b2"], default="b0")
    ev.add_argument("--out", type=Path, required=True)
    cmp = commands.add_parser("compare")
    cmp.add_argument("a", type=Path); cmp.add_argument("b", type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "compare":
        print(json.dumps(paired_compare(json.loads(args.a.read_text()), json.loads(args.b.read_text())), ensure_ascii=False, indent=2)); return
    corpus = Corpus.from_dir(args.corpus)
    if args.cmd == "ask":
        planner = None
        if args.llm_url:
            if not args.model: parser.error("--model required with --llm-url")
            planner = OpenAICompatiblePlanner(base_url=args.llm_url, model=args.model)
        elif args.model:
            parser.error("--llm-url required with --model")
        state = Agent(ReadOnlyTools(corpus), store=CheckpointStore(args.db), planner=planner).run(
            args.query, mode=args.mode, budget=args.budget, resume=args.resume)
        print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    else:
        result = measure(load_cases(args.cases), corpus, variant=args.variant)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"variant":args.variant, "count":result["count"],"metrics":result["metrics"],"output":str(args.out)},ensure_ascii=False,indent=2))

if __name__ == "__main__": main()
