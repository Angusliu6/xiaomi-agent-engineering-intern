"""OPTIONAL MCP SDK v2 integration example.

Requires `pip install mcp` (not a core dependency). This example follows the
official v2 `MCPServer` decorator API and is *not* part of offline CI.
Run from repository root: `mcp dev integrations/mcp_server.py`.
"""
from pathlib import Path
from mcp.server import MCPServer  # intentionally optional, see docs/HR_REVIEW.md
from traceqa.retrieval import Corpus
from traceqa.runtime import ReadOnlyTools, ToolError

mcp = MCPServer('traceqa-read-only')
corpus = Corpus.from_dir(Path(__file__).resolve().parents[1] / 'data/corpus')
tools = ReadOnlyTools(corpus)

@mcp.tool()
def search_docs(query: str, top_k: int = 5) -> dict:
    """Search public synthetic incident notes. Read-only; no shell access."""
    try:
        hits = tools.search_docs(query, top_k, mode='hybrid')
    except ToolError as exc:
        return {'ok': False, 'error': str(exc), 'hits': []}
    return {'ok': True, 'hits': [{'id': h.id, 'score': h.score, 'excerpt': h.text[:240]} for h in hits]}
