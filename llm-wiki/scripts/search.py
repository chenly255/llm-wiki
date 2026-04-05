#!/usr/bin/env python3
"""
Knowledge Factory — Wiki Search Engine

BM25-based search over a wiki directory of .md files.
Returns ranked results with file paths, scores, and context snippets.

Usage:
    python3 search.py --wiki-dir wiki/ --query "your search terms" --top-k 10
    python3 search.py --wiki-dir wiki/ --query "concept" --top-k 5 --json
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path


def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer, lowercased."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if len(w) > 1]


def extract_title(content: str) -> str:
    """Extract the first H1 heading as the document title."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# ') and not line.startswith('##'):
            return line[2:].strip()
    return "(untitled)"


def extract_snippet(content: str, query_tokens: set[str], context_chars: int = 200) -> str:
    """Find the best snippet containing query terms."""
    lines = content.split('\n')
    best_score = 0
    best_line_idx = 0

    for i, line in enumerate(lines):
        line_lower = line.lower()
        score = sum(1 for t in query_tokens if t in line_lower)
        if score > best_score:
            best_score = score
            best_line_idx = i

    # Grab surrounding lines for context
    start = max(0, best_line_idx - 1)
    end = min(len(lines), best_line_idx + 3)
    snippet = '\n'.join(lines[start:end]).strip()

    if len(snippet) > context_chars:
        snippet = snippet[:context_chars] + '...'

    return snippet


class BM25:
    """Simple BM25 implementation for wiki search."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: list[dict] = []       # [{path, title, content, tokens}]
        self.doc_freqs: Counter = Counter()
        self.avg_dl: float = 0
        self.n_docs: int = 0

    def index(self, wiki_dir: str) -> int:
        """Index all .md files in wiki_dir. Returns count of indexed docs."""
        wiki_path = Path(wiki_dir)
        if not wiki_path.exists():
            return 0

        md_files = sorted(wiki_path.rglob('*.md'))
        self.docs = []

        for fpath in md_files:
            # Skip index/graph meta files from search ranking
            fname = fpath.name
            try:
                content = fpath.read_text(encoding='utf-8')
            except Exception:
                continue

            tokens = tokenize(content)
            title = extract_title(content)

            self.docs.append({
                'path': str(fpath),
                'relative_path': str(fpath.relative_to(wiki_path)),
                'title': title,
                'content': content,
                'tokens': tokens,
                'tf': Counter(tokens),
            })

        self.n_docs = len(self.docs)
        if self.n_docs == 0:
            return 0

        self.avg_dl = sum(len(d['tokens']) for d in self.docs) / self.n_docs

        # Document frequency
        self.doc_freqs = Counter()
        for doc in self.docs:
            unique_tokens = set(doc['tokens'])
            for token in unique_tokens:
                self.doc_freqs[token] += 1

        return self.n_docs

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Search the index. Returns list of {path, title, score, snippet}."""
        if self.n_docs == 0:
            return []

        query_tokens = tokenize(query)
        query_token_set = set(query_tokens)
        scores = []

        for doc in self.docs:
            score = 0.0
            dl = len(doc['tokens'])

            for qt in query_tokens:
                if qt not in self.doc_freqs:
                    continue

                df = self.doc_freqs[qt]
                idf = math.log((self.n_docs - df + 0.5) / (df + 0.5) + 1)

                tf = doc['tf'].get(qt, 0)
                tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl))

                score += idf * tf_norm

            if score > 0:
                snippet = extract_snippet(doc['content'], query_token_set)
                scores.append({
                    'path': doc['path'],
                    'relative_path': doc['relative_path'],
                    'title': doc['title'],
                    'score': round(score, 4),
                    'snippet': snippet,
                })

        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_k]


def main():
    parser = argparse.ArgumentParser(description='Knowledge Factory Wiki Search')
    parser.add_argument('--wiki-dir', required=True, help='Path to wiki/ directory')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--top-k', type=int, default=10, help='Number of results (default: 10)')
    parser.add_argument('--json', action='store_true', help='Output as JSON (default: human-readable)')
    args = parser.parse_args()

    bm25 = BM25()
    n_indexed = bm25.index(args.wiki_dir)

    if n_indexed == 0:
        if args.json:
            print(json.dumps({'results': [], 'indexed': 0, 'query': args.query}))
        else:
            print(f"No .md files found in {args.wiki_dir}")
        sys.exit(0)

    results = bm25.search(args.query, top_k=args.top_k)

    if args.json:
        print(json.dumps({
            'results': results,
            'indexed': n_indexed,
            'query': args.query,
            'hits': len(results),
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Searched {n_indexed} documents for: \"{args.query}\"")
        print(f"Found {len(results)} results:\n")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['score']:.2f}] {r['title']}")
            print(f"     {r['relative_path']}")
            # Indent snippet
            for line in r['snippet'].split('\n'):
                print(f"     > {line}")
            print()


if __name__ == '__main__':
    main()
