# Graph Report - cahier-pct  (2026-11-09)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 341 nodes · 781 edges · 12 communities (10 shown, 2 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 61 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 10
- Community 11

## God Nodes (most connected - your core abstractions)
1. `Corpus` - 29 edges
2. `Extract` - 18 edges
3. `generate_exercices()` - 17 edges
4. `generate_fiche()` - 17 edges
5. `compilerOptions` - 17 edges
6. `ApiError` - 15 edges
7. `generate_question()` - 15 edges
8. `LLMService` - 14 edges
9. `errorMessage()` - 14 edges
10. `register_routes()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `_register_error_handlers()` --uses--> `ApiError`  [INFERRED]
  backend/app/__init__.py → backend/app/errors.py
- `create_app()` --uses--> `Config`  [INFERRED]
  backend/app/__init__.py → backend/app/config.py
- `validate()` --uses--> `CorpusError`  [INFERRED]
  backend/scripts/corpus.py → backend/app/errors.py
- `corpus()` --uses--> `Corpus`  [INFERRED]
  backend/app/api/deps.py → backend/app/services/corpus.py
- `Corpus` --uses--> `BM25Index`  [INFERRED]
  backend/app/services/corpus.py → backend/app/services/retrieval.py

## Import Cycles
- None detected.

## Communities (12 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (57): App(), NotFoundPage(), CitationList(), TYPE_LABELS, typeLabel(), CompetenceField(), Props, Icon() (+49 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (15): corpus(), llm(), parse_body(), register_routes(), exercices(), fiche(), get_extract(), list_corpus() (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (18): LLMError, context_block(), load_prompt(), render(), system_prompt(), _citation(), _citations(), _excerpt() (+10 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (11): Config, CorpusError, Corpus, Extract, get_corpus(), _load_corpus(), TestConfig, test_corpus_loads() (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (29): dependencies, react@^19.1.1, react-dom@^19.1.1, react-markdown@^10.1.0, react-router-dom@^7.8.2, remark-gfm@^4.0.1, devDependencies, @types/react@^19.1.10 (+21 more)

### Community 5 - "Community 5"
Cohesion: 0.13
Nodes (7): create_app(), _register_error_handlers(), _register_frontend(), clear_corpus_cache(), app(), _clear_cache(), client()

### Community 6 - "Community 6"
Cohesion: 0.16
Nodes (10): BM25Index, normalize(), SearchHit, tokenize(), test_bm25_handles_empty_index(), test_bm25_ignores_empty_query(), test_bm25_ranks_relevant_document_first(), test_bm25_returns_empty_without_match() (+2 more)

### Community 7 - "Community 7"
Cohesion: 0.24
Nodes (13): build(), build_index(), clean(), load_pages(), main(), Page, page_at(), read_pdf() (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (13): discipline, expected_extracts, extracts, id, level, notes, program, edition (+5 more)

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Corpus` connect `Community 3` to `Community 1`, `Community 2`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Corpus` (e.g. with `corpus()` and `CorpusError`) actually correct?**
  _`Corpus` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07432651736449204 - nodes in this community are weakly interconnected._
- **Why does `ApiError` connect `Community 1` to `Community 2`, `Community 3`, `Community 5`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Extract` (e.g. with `context_block()` and `CorpusError`) actually correct?**
  _`Extract` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08780487804878048 - nodes in this community are weakly interconnected._
- **Why does `react` connect `Community 0` to `Community 4`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._