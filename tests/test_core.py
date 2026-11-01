import json
import tempfile
import unittest
from pathlib import Path
from traceqa.retrieval import Corpus, Document, tokenize
from traceqa.runtime import Agent, ReadOnlyTools, CheckpointStore, ToolError
from traceqa.evaluation import measure, paired_compare, load_cases
from traceqa.llm import OpenAICompatiblePlanner

ROOT = Path(__file__).resolve().parents[1]

class TestRetrieval(unittest.TestCase):
    def setUp(self): self.corpus=Corpus.from_dir(ROOT/'data/corpus')
    def test_corpus(self): self.assertEqual(len(self.corpus.docs), 12)
    def test_exact_error_retrieval(self):
        self.assertIn('context-budget.md',[h.id for h in self.corpus.search('max_output_tokens equals max_model_len',5)])
    def test_hybrid(self): self.assertTrue(self.corpus.search('idempotency key',5,'hybrid'))
    def test_determinism(self):
        self.assertEqual(self.corpus.search('search_docs timeout',5,'hybrid'),self.corpus.search('search_docs timeout',5,'hybrid'))
    def test_no_matches(self): self.assertEqual(self.corpus.search('nonsensezzzzz',5),[])
    def test_invalid_k(self):
        with self.assertRaises(ValueError): self.corpus.search('test',0)
    def test_invalid_mode(self):
        with self.assertRaises(ValueError): self.corpus.search('test',3,'embedding')
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError): Corpus([Document('x','a'),Document('x','b')])
    def test_empty_root(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): Corpus.from_dir(Path(d))
    def test_cjk_tokens(self): self.assertTrue(tokenize('事件日志'))

class TestRuntime(unittest.TestCase):
    def setUp(self): self.corpus=Corpus.from_dir(ROOT/'data/corpus')
    def test_agent_evidence(self):
        s=Agent(ReadOnlyTools(self.corpus)).run('QueuePool size 5 overflow 10')
        self.assertEqual(s.status,'evidence_found')
        self.assertTrue(s.citations)
    def test_refuse_unknown(self):
        s=Agent(ReadOnlyTools(self.corpus)).run('nonsensezzzzzzzzzzz')
        self.assertEqual(s.status,'insufficient_evidence')
    def test_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            store=CheckpointStore(Path(d)/'x.db')
            s=Agent(ReadOnlyTools(self.corpus),store=store).run('RRF fusion')
            self.assertEqual(store.load(s.run_id).answer,s.answer)
            self.assertEqual(Agent(ReadOnlyTools(self.corpus),store=store).run('RRF fusion',resume=s.run_id).run_id,s.run_id)
    def test_config_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            store=CheckpointStore(Path(d)/'x.db')
            s=Agent(ReadOnlyTools(self.corpus),store=store).run('RRF fusion')
            with self.assertRaises(ValueError): Agent(ReadOnlyTools(self.corpus),store=store).run('wrong',resume=s.run_id)
    def test_invalid_tool_args(self):
        tool=ReadOnlyTools(self.corpus)
        for n in [-1,0,21,True]:
            with self.assertRaises(ToolError): tool.search_docs('test',n,'bm25')
    def test_fault(self):
        s=Agent(ReadOnlyTools(self.corpus,fail_first=True)).run('MCP timeout',budget=3)
        self.assertTrue(any(e.kind=='tool_error' for e in s.events))
    def test_budget(self):
        with self.assertRaises(ValueError): Agent(ReadOnlyTools(self.corpus)).run('any',budget=100)
    def test_prompt_injection_not_executed(self):
        s=Agent(ReadOnlyTools(self.corpus)).run('API_KEY leaked external instruction')
        self.assertTrue(s.citations)
        self.assertTrue(all(e.kind != 'shell_execution' for e in s.events))
    def test_endpoint_security(self):
        with self.assertRaises(ValueError): OpenAICompatiblePlanner(base_url='http://arbitrary-host:8000/v1',model='test')

class TestEvaluation(unittest.TestCase):
    def setUp(self): self.corpus=Corpus.from_dir(ROOT/'data/corpus');self.cases=load_cases(ROOT/'data/benchmark.jsonl')
    def test_metrics(self):
        r=measure(self.cases,self.corpus,variant='b0')
        self.assertEqual(r['count'],23)
        self.assertTrue(0<=r['metrics']['hit_at_5_answerable']<=1)
    def test_pairing(self):
        a=measure(self.cases,self.corpus,variant='b0');b=measure(self.cases,self.corpus,variant='b1')
        c=paired_compare(a,b,iterations=200)
        self.assertEqual(c['paired_n'],20)
    def test_mismatched_cases(self):
        a=measure(self.cases,self.corpus,variant='b0');b=measure(self.cases[1:],self.corpus,variant='b1')
        with self.assertRaises(ValueError): paired_compare(a,b)
    def test_duplicate_cases(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cases.jsonl';p.write_text('\n'.join([json.dumps(self.cases[0])]*2))
            with self.assertRaises(ValueError):load_cases(p)

if __name__=='__main__': unittest.main()
