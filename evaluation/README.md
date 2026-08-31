# Evaluation

Benchmark datasets, metrics, and runners for measuring ConstituteAI's
retrieval and (eventually) generation quality.

## Current structure

```
evaluation/
├── datasets/
│   └── retrieval_questions.json   # question -> expected source_ids + category
├── metrics/                       # empty for now (see below)
├── runners/
│   └── run_retrieval_eval.py      # runs questions through the real LangGraph
│                                   # retrieval path, reports Recall@K/Precision@K
├── results/                       # empty for now (see below)
└── README.md
```

`metrics/` and `results/` are placeholders — see "Planned, not yet built"
below. Nothing currently writes into `results/`; `run_retrieval_eval.py`
prints to stdout only.

## Running the retrieval eval

```bash
# Local metadata fixture (no live Pinecone call, fast, deterministic)
PYTHONPATH=. python evaluation/runners/run_retrieval_eval.py

# Against the real configured Pinecone index
PYTHONPATH=. python evaluation/runners/run_retrieval_eval.py --live

# Options
--top-k N        # default 10
--namespace NAME # default from backend.config.PINECONE_NAMESPACE
--no-rerank      # disable hosted reranking even if RERANK_ENABLED=true
```

The runner chains the same LangGraph nodes `/api/chat` actually uses
(`analyze_query` -> `build_metadata_filter` -> `retrieve`), not the raw
retriever directly — a fix to intent routing or the dual-corpus retrieval
logic in `backend/graph/nodes/retrieval.py` shows up here immediately,
rather than the benchmark silently drifting from what a live request does.

## What the metrics mean

- **Recall@K** — of the source_ids a question expects, what fraction did
  retrieval actually surface in its top K results? Misses mean the
  right answer was never even available to the generation step.
- **Precision@K** — of what retrieval surfaced, what fraction was
  actually relevant (in the expected set)? Low precision means correct
  answers are getting diluted by irrelevant retrieved context.
- Results are also broken down per question `category`
  (`explicit-article`, `conceptual`, `case-law`) — a conceptual-query
  weakness (see `KNOWN_ISSUES.md`) doesn't get masked by strong
  explicit-article numbers when averaged together.

## `evaluation/datasets/retrieval_questions.json` format

```json
{
  "id": "q01",
  "question": "What is Article 1 of the Constitution of India?",
  "expected_source_ids": ["article_1"],
  "category": "explicit-article"
}
```

`category` is one of `explicit-article`, `conceptual`, `case-law`.
`expected_source_ids` is the full set of source_ids retrieval should
surface for this question — an article number (`article_21`) or a case
slug (`maneka_gandhi_1978`), matching `backend/graph/nodes/citations.py`'s
`citation_for()` source_id convention.

## Planned, not yet built

Generation-quality evaluation (does the *answer*, not just retrieval,
hold up — faithfulness to context, no fabricated claims, citation
accuracy) is a separate, larger piece of work, deliberately not started
yet. Before building it:

1. Research whether Ragas or DeepEval integrate cleanly with this
   project's structured LangGraph output shape (summary/sections/
   key_clauses/explanation + resolved citations) — reported separately,
   not assumed.
2. `evaluation/datasets/generation_questions.json`'s format needs to be
   proposed and confirmed before any runner is built around it.
3. Once both of those are settled: `evaluation/metrics/generation_metrics.py`,
   `evaluation/metrics/hallucination_check.py`,
   `evaluation/runners/run_generation_eval.py`, and
   `evaluation/runners/run_e2e_eval.py` (full query -> graph -> scored
   answer) get built — plus `evaluation/metrics/retrieval_metrics.py` if
   it's worth extracting the Recall/Precision math out of
   `run_retrieval_eval.py` into its own reusable module at that point.
4. `evaluation/results/` will hold timestamped, versioned run outputs
   (e.g. `2026-08-31_v3_baseline.json` + a human-readable `.md` summary)
   once a runner actually writes results to disk instead of just stdout.
