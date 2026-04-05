# Wiki Conventions — Knowledge Factory

> Reference document for consistent wiki formatting.

## File Naming

- **Concept articles:** `wiki/concepts/{lowercase-kebab-case}.md`
  - Example: `wiki/concepts/neural-network.md`, `wiki/concepts/attention-mechanism.md`
- **Source summaries:** `wiki/sources/{lowercase-kebab-case}.md`
  - Example: `wiki/sources/karpathy-llm-knowledge-bases.md`
- **Meta files (auto-managed):** `wiki/_index.md`, `wiki/_graph.md`
  - Prefix with `_` to sort first and signal "don't edit manually"

## Article Format

### Concept Article

```markdown
# {Concept Name in Title Case}
> Auto-compiled by llm-wiki.

## Overview
{2-5 sentences synthesizing what this concept is, drawn from all sources}

## Key Points
- {Important point 1}
- {Important point 2}
- ...

## Sources
- [[sources/{source-a}]]: {what this source says about the concept}
- [[sources/{source-b}]]: {what this source says about the concept}

## Related Concepts
- [[{related-concept-a}]]: {brief description of relationship}
- [[{related-concept-b}]]: {brief description of relationship}
```

### Source Summary

```markdown
# {Document Title}
> Source: `raw/{relative-path}`
> Ingested: {YYYY-MM-DD}
> Type: {paper|article|code|dataset|other}

## Summary
{3-5 sentence summary of the entire document}

## Key Concepts
- [[{concept-a}]]: {how this document relates to the concept}
- [[{concept-b}]]: {how this document relates to the concept}

## Key Facts
- {Fact 1}
- {Fact 2}

## Quotes / Key Passages
> {Notable quote or passage, with attribution if applicable}
```

## Cross-Reference Syntax

Use Obsidian-compatible `[[wiki-link]]` syntax:

- `[[concept-name]]` — links to `wiki/concepts/concept-name.md`
- `[[sources/source-name]]` — links to `wiki/sources/source-name.md`
- Use the concept name (not the file path) for concept links
- Always use the `sources/` prefix for source links to avoid ambiguity

## Index Format (_index.md)

```markdown
# Knowledge Index
> Auto-maintained by llm-wiki. Do not edit manually.

## Statistics
- Total articles: N
- Concept articles: N
- Source summaries: N
- Total words: ~N
- Last updated: YYYY-MM-DD HH:MM

## Concepts
- [[concept-a]] — one-line summary (N refs)
- [[concept-b]] — one-line summary (N refs)

## Sources
- [[sources/source-a]] — one-line summary
- [[sources/source-b]] — one-line summary
```

## Graph Format (_graph.md)

```markdown
# Backlink Graph
> Auto-maintained by llm-wiki. Do not edit manually.

## Link Map
| Article | Links to | Linked from |
|---------|----------|-------------|
| [[concept-a]] | [[concept-b]], [[concept-c]] | [[sources/source-x]] |

## Broken Links
- `[[missing]]` in sources/source-y.md

## Orphan Articles
- concepts/lonely-concept.md
```

## Writing Guidelines

1. **Synthesize, don't copy.** Wiki articles should distill and connect information, not reproduce raw text.
2. **One concept per article.** If a concept is too broad, split it.
3. **Always cite sources.** Every claim in a concept article should trace back to a source.
4. **Use consistent terminology.** If two sources use different terms for the same concept, pick one and note the alias.
5. **Update, don't duplicate.** When new information arrives, merge it into existing articles rather than creating parallel ones.
6. **Keep summaries fresh.** When an article grows significantly, update its one-line summary in `_index.md`.
