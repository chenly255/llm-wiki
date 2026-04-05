#!/usr/bin/env python3
"""
Knowledge Factory — Wiki Index Generator

Scans wiki/ directory and generates/updates _index.md and _graph.md.

Usage:
    python3 index.py --wiki-dir wiki/
    python3 index.py --wiki-dir wiki/ --stats-only
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def extract_title(content: str) -> str:
    """Extract the first H1 heading."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# ') and not line.startswith('##'):
            return line[2:].strip()
    return "(untitled)"


def extract_summary(content: str) -> str:
    """Extract first meaningful paragraph as summary."""
    lines = content.split('\n')
    in_frontmatter = False
    for line in lines:
        stripped = line.strip()
        if stripped == '---':
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if stripped.startswith('#'):
            continue
        if stripped.startswith('>'):
            continue
        if stripped == '':
            continue
        # Found first content line
        summary = stripped
        if len(summary) > 150:
            summary = summary[:147] + '...'
        return summary
    return "(no summary)"


def extract_links(content: str) -> list[str]:
    """Extract all [[wiki-links]] from content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def scan_wiki(wiki_dir: Path) -> dict:
    """Scan all .md files and extract metadata."""
    articles = {}

    for fpath in sorted(wiki_dir.rglob('*.md')):
        rel = str(fpath.relative_to(wiki_dir))
        # Skip meta files
        if rel.startswith('_'):
            continue

        try:
            content = fpath.read_text(encoding='utf-8')
        except Exception:
            continue

        title = extract_title(content)
        summary = extract_summary(content)
        links = extract_links(content)
        word_count = len(content.split())

        articles[rel] = {
            'path': rel,
            'title': title,
            'summary': summary,
            'links': links,
            'word_count': word_count,
        }

    return articles


def build_backlink_graph(articles: dict) -> dict:
    """Build incoming link map from articles."""
    backlinks = defaultdict(list)

    for rel_path, meta in articles.items():
        for link in meta['links']:
            # Normalize link to file path
            # [[concept-name]] -> concepts/concept-name.md
            # [[sources/source-name]] -> sources/source-name.md
            if '/' in link:
                target = link + '.md' if not link.endswith('.md') else link
            else:
                # Try to find in concepts/ first, then entities/, then sources/
                target_concept = f'concepts/{link}.md'
                target_entity = f'entities/{link}.md'
                target_source = f'sources/{link}.md'
                if target_concept in articles:
                    target = target_concept
                elif target_entity in articles:
                    target = target_entity
                elif target_source in articles:
                    target = target_source
                else:
                    target = link  # unresolved

            backlinks[target].append(rel_path)

    return dict(backlinks)


def generate_index(articles: dict, backlinks: dict) -> str:
    """Generate _index.md content."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    concepts = {k: v for k, v in articles.items() if k.startswith('concepts/')}
    entities = {k: v for k, v in articles.items() if k.startswith('entities/')}
    sources = {k: v for k, v in articles.items() if k.startswith('sources/')}
    other = {k: v for k, v in articles.items() if not k.startswith(('concepts/', 'entities/', 'sources/'))}

    total_words = sum(a['word_count'] for a in articles.values())

    lines = [
        '# Knowledge Index',
        '> Auto-maintained by llm-wiki. Do not edit manually.',
        '',
        '## Statistics',
        f'- Total articles: {len(articles)}',
        f'- Concepts: {len(concepts)}',
        f'- Entities: {len(entities)}',
        f'- Source summaries: {len(sources)}',
        f'- Total words: ~{total_words:,}',
        f'- Last updated: {now}',
        '',
    ]

    if concepts:
        lines.append('## Concepts')
        lines.append('')
        for path in sorted(concepts.keys()):
            meta = concepts[path]
            name = path.replace('concepts/', '').replace('.md', '')
            n_backlinks = len(backlinks.get(path, []))
            lines.append(f'- [[{name}]] — {meta["summary"]} ({n_backlinks} refs)')
        lines.append('')

    if entities:
        lines.append('## Entities')
        lines.append('')
        for path in sorted(entities.keys()):
            meta = entities[path]
            name = path.replace('entities/', '').replace('.md', '')
            n_backlinks = len(backlinks.get(path, []))
            lines.append(f'- [[{name}]] — {meta["summary"]} ({n_backlinks} refs)')
        lines.append('')

    if sources:
        lines.append('## Sources')
        lines.append('')
        for path in sorted(sources.keys()):
            meta = sources[path]
            name = path.replace('sources/', '').replace('.md', '')
            lines.append(f'- [[sources/{name}]] — {meta["summary"]}')
        lines.append('')

    if other:
        lines.append('## Other')
        lines.append('')
        for path in sorted(other.keys()):
            meta = other[path]
            lines.append(f'- {path} — {meta["summary"]}')
        lines.append('')

    return '\n'.join(lines)


def _mermaid_safe_id(name: str) -> str:
    """Convert a name to a Mermaid-safe node ID."""
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


def _resolve_link_target(link: str, articles: dict) -> str | None:
    """Resolve a [[wiki-link]] to an existing article path, or None."""
    if link.endswith('.md'):
        link = link[:-3]
    for prefix in ['concepts/', 'entities/', 'sources/', '']:
        candidate = f'{prefix}{link}.md'
        if candidate in articles:
            return candidate
    return None


def generate_mermaid_graph(articles: dict, backlinks: dict, max_nodes: int = 50) -> str:
    """Generate a Mermaid knowledge graph for Obsidian rendering."""
    # Only include concepts and entities as nodes (sources make it too noisy)
    node_articles = {k: v for k, v in articles.items()
                     if k.startswith(('concepts/', 'entities/'))}

    if not node_articles:
        return ''

    # If too many nodes, keep only the most connected ones
    if len(node_articles) > max_nodes:
        # Sort by total links (outgoing + incoming)
        def connectivity(path):
            out = len(node_articles[path]['links'])
            inc = len(backlinks.get(path, []))
            return out + inc
        sorted_paths = sorted(node_articles.keys(), key=connectivity, reverse=True)
        node_articles = {k: node_articles[k] for k in sorted_paths[:max_nodes]}

    node_set = set(node_articles.keys())
    edges = set()
    all_resolved = set(node_set)

    # Collect edges from outgoing links
    for path, meta in node_articles.items():
        for link in meta['links']:
            target = _resolve_link_target(link, node_articles)
            if target and target in node_set and target != path:
                edges.add((path, target))
                all_resolved.add(target)

    lines = [
        '## Knowledge Graph',
        '',
        '```mermaid',
        'graph LR',
    ]

    # Subgraphs by type
    concepts = sorted(p for p in node_articles if p.startswith('concepts/'))
    entities = sorted(p for p in node_articles if p.startswith('entities/'))

    if concepts:
        lines.append('    subgraph Concepts')
        for path in concepts:
            name = path.replace('concepts/', '').replace('.md', '')
            mid = _mermaid_safe_id(name)
            # Truncate long names for readability
            display = name[:25] + '...' if len(name) > 25 else name
            lines.append(f'        {mid}["{display}"]')
        lines.append('    end')

    if entities:
        lines.append('')
        lines.append('    subgraph Entities')
        for path in entities:
            name = path.replace('entities/', '').replace('.md', '')
            mid = _mermaid_safe_id(name)
            display = name[:25] + '...' if len(name) > 25 else name
            lines.append(f'        {mid}["{display}"]')
        lines.append('    end')

    # Edges — use short names to match node IDs
    if edges:
        lines.append('')
        for src, tgt in sorted(edges):
            src_short = src.split('/')[-1].replace('.md', '')
            tgt_short = tgt.split('/')[-1].replace('.md', '')
            src_id = _mermaid_safe_id(src_short)
            tgt_id = _mermaid_safe_id(tgt_short)
            lines.append(f'    {src_id} --> {tgt_id}')

    lines.extend(['```', ''])
    return '\n'.join(lines)


def generate_graph(articles: dict, backlinks: dict) -> str:
    """Generate _graph.md content."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines = [
        '# Backlink Graph',
        '> Auto-maintained by llm-wiki. Do not edit manually.',
        f'> Last updated: {now}',
        '',
        '## Link Map',
        '',
        '| Article | Links to | Linked from |',
        '|---------|----------|-------------|',
    ]

    for path in sorted(articles.keys()):
        meta = articles[path]
        name = path.replace('.md', '')

        outgoing = ', '.join(f'[[{l}]]' for l in meta['links'][:5]) or '—'
        incoming = ', '.join(
            f'[[{b.replace(".md", "")}]]' for b in backlinks.get(path, [])[:5]
        ) or '—'

        lines.append(f'| [[{name}]] | {outgoing} | {incoming} |')

    # Broken links
    all_paths = set(articles.keys())
    broken = []
    for path, meta in articles.items():
        for link in meta['links']:
            target = _resolve_link_target(link, articles)
            if target is None:
                broken.append((link, path))

    if broken:
        lines.extend(['', '## Broken Links', ''])
        for link, source in broken:
            lines.append(f'- `[[{link}]]` in {source}')

    # Orphans
    orphans = []
    for path in articles:
        has_outgoing = bool(articles[path]['links'])
        has_incoming = bool(backlinks.get(path, []))
        if not has_outgoing and not has_incoming:
            orphans.append(path)

    if orphans:
        lines.extend(['', '## Orphan Articles (no links in or out)', ''])
        for o in orphans:
            lines.append(f'- {o}')

    lines.append('')

    # Append Mermaid knowledge graph
    mermaid = generate_mermaid_graph(articles, backlinks)
    if mermaid:
        lines.append(mermaid)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Knowledge Factory Index Generator')
    parser.add_argument('--wiki-dir', required=True, help='Path to wiki/ directory')
    parser.add_argument('--stats-only', action='store_true', help='Print stats without writing files')
    args = parser.parse_args()

    wiki_dir = Path(args.wiki_dir)
    if not wiki_dir.exists():
        print(f"Error: {wiki_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    articles = scan_wiki(wiki_dir)
    backlinks = build_backlink_graph(articles)

    if args.stats_only:
        concepts = sum(1 for k in articles if k.startswith('concepts/'))
        entities = sum(1 for k in articles if k.startswith('entities/'))
        sources = sum(1 for k in articles if k.startswith('sources/'))
        total_words = sum(a['word_count'] for a in articles.values())
        print(json.dumps({
            'total_articles': len(articles),
            'concepts': concepts,
            'entities': entities,
            'sources': sources,
            'total_words': total_words,
        }, indent=2))
        return

    # Write _index.md
    index_content = generate_index(articles, backlinks)
    (wiki_dir / '_index.md').write_text(index_content, encoding='utf-8')
    print(f"Updated _index.md ({len(articles)} articles)")

    # Write _graph.md
    graph_content = generate_graph(articles, backlinks)
    (wiki_dir / '_graph.md').write_text(graph_content, encoding='utf-8')
    print(f"Updated _graph.md")

    # Summary
    broken_count = sum(
        1 for path, meta in articles.items()
        for link in meta['links']
        if not any(f'{p}{link}.md' in articles or f'{p}{link}' in articles for p in ['concepts/', 'entities/', 'sources/', ''])
    )
    orphan_count = sum(
        1 for path in articles
        if not articles[path]['links'] and not backlinks.get(path, [])
    )
    print(f"Broken links: {broken_count}, Orphans: {orphan_count}")


if __name__ == '__main__':
    main()
