"""CLI-level smoke contracts without external model/network access."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import json
import tempfile
import unittest
from traceqa.cli import main
ROOT=Path(__file__).resolve().parents[1]

def invoke(args):
    buffer=StringIO()
    with redirect_stdout(buffer), redirect_stderr(StringIO()): main(args)
    return json.loads(buffer.getvalue())

class CliContracts(unittest.TestCase):
    def test_ask_trace(self):
        with tempfile.TemporaryDirectory() as d:
            r=invoke(['ask','RRF fusion','--db',str(Path(d)/'store.db')])
        self.assertEqual(r['status'],'evidence_found')
        self.assertTrue(r['citations'])
        self.assertTrue(any(e['kind']=='tool_start' for e in r['events']))
    def test_resume(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'store.db')
            a=invoke(['ask','RRF fusion','--db',db])
            b=invoke(['ask','RRF fusion','--db',db,'--resume',a['run_id']])
        self.assertEqual(a['events'],b['events'])
    def test_eval_compare(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=str(Path(d)/'a.json'),str(Path(d)/'b.json')
            self.assertEqual(invoke(['eval','--variant','b0','--out',a])['count'],23)
            self.assertEqual(invoke(['eval','--variant','b1','--out',b])['count'],23)
            self.assertEqual(invoke(['compare',a,b])['gain_case_ids'],['q008'])
    def test_stress(self):
        with tempfile.TemporaryDirectory() as d:
            r=invoke(['eval','--cases',str(ROOT/'data/stress_hard_negative.jsonl'),
                      '--variant','b2','--out',str(Path(d)/'stress.json')])
        self.assertEqual(r['count'],16)
        self.assertEqual(r['metrics']['correct_abstention_unanswerable'],0.4)
    def test_missing_model_url(self):
        with self.assertRaises(SystemExit): invoke(['ask','RRF','--model','test'])
    def test_invalid_variant(self):
        with self.assertRaises(SystemExit): invoke(['eval','--variant','invalid','--out','x.json'])
    def test_custom_corpus_option(self):
        with tempfile.TemporaryDirectory() as d:
            r=invoke(['--corpus',str(ROOT/'data/corpus'),'ask','RRF fusion','--db',str(Path(d)/'x.db')])
        self.assertEqual(r['status'],'evidence_found')
