# Wiki Conventions — LLM Wiki

> Reference document for consistent wiki formatting.

## File Naming

- **Concept articles:** `wiki/concepts/{lowercase-kebab-case}.md`
  - Example: `wiki/concepts/neural-network.md`, `wiki/concepts/attention-mechanism.md`
- **Entity articles:** `wiki/entities/{lowercase-kebab-case}.md`
  - Example: `wiki/entities/andrej-karpathy.md`, `wiki/entities/obsidian.md`
- **Source summaries:** `wiki/sources/{lowercase-kebab-case}.md`
  - Example: `wiki/sources/karpathy-llm-knowledge-bases.md`
- **Meta files (auto-managed):** `wiki/_index.md`, `wiki/_graph.md`
  - Prefix with `_` to sort first and signal "don't edit manually"

## What Is a Concept vs an Entity?

| Type | What it is | Examples |
|------|-----------|---------|
| **Concept** | An idea, method, pattern, or technique | knowledge-flywheel, attention-mechanism, backpropagation |
| **Entity** | A specific person, tool, org, dataset, or product | andrej-karpathy, obsidian, openai, imagenet |

Rule of thumb: if it has a Wikipedia page as a proper noun, it's an entity. If it's an abstract idea, it's a concept.

## Article Formats

### Concept Article

```markdown
# {Concept Name in Title Case}
> Auto-compiled by llm-wiki.

## Overview
{2-5 sentences synthesizing what this concept is, drawn from all sources}

## Key Points
- {Important point 1}
- {Important point 2}

## Sources
- [[sources/{source-a}]]: {what this source says about the concept}
- [[sources/{source-b}]]: {what this source says about the concept}

## Related Concepts
- [[{related-concept}]]: {brief description of relationship}

## Related Entities
- [[{related-entity}]]: {brief description of relationship}
```

### Entity Article

```markdown
# {Entity Name}
> Auto-compiled by llm-wiki.
> Type: {person|tool|organization|dataset|product|other}

## Overview
{Who/what this is, synthesized from all sources}

## Mentioned In
- [[sources/{source-a}]]: {context of mention}

## Related Concepts
- [[{concept}]]: {how this entity relates to the concept}

## Related Entities
- [[{other-entity}]]: {relationship description}
```

### Source Summary

```markdown
# {Document Title}
> Source: `raw/sources/{filename}`
> Ingested: {YYYY-MM-DD}
> Type: {paper|article|code|dataset|other}
> Status: ingested

## Summary
{3-5 sentence summary of the entire document}

## Key Concepts
- [[{concept-a}]]: {how this document relates to the concept}
- [[{concept-b}]]: {how this document relates to the concept}

## Key Entities
- [[{entity-a}]]: {how this document relates to the entity}

## Key Facts
- {Fact 1}
- {Fact 2}

## Quotes / Key Passages
> {Notable quote or passage, with attribution if applicable}
```

## Cross-Reference Syntax

Use `[[wiki-link]]` syntax:

- `[[concept-name]]` — links to `wiki/concepts/concept-name.md`
- `[[entity-name]]` — links to `wiki/entities/entity-name.md`
- `[[sources/source-name]]` — links to `wiki/sources/source-name.md`
- Use the name only (not file path) for concept/entity links
- Always use `sources/` prefix for source links to avoid ambiguity

## Index Format (_index.md)

```markdown
# Knowledge Index
> Auto-maintained by llm-wiki. Do not edit manually.

## Statistics
- Total articles: N
- Concepts: N
- Entities: N
- Source summaries: N
- Total words: ~N
- Last updated: YYYY-MM-DD HH:MM

## Concepts
- [[concept-a]] — one-line summary (N refs)

## Entities
- [[entity-a]] — one-line summary (N refs)

## Sources
- [[sources/source-a]] — one-line summary
```

## Writing Guidelines

1. **Synthesize, don't copy.** Wiki articles should distill and connect information, not reproduce raw text.
2. **One topic per article.** If a concept is too broad, split it.
3. **Always cite sources.** Every claim should trace back to a source summary.
4. **Use consistent terminology.** If two sources use different terms for the same thing, pick one and note the alias.
5. **Update, don't duplicate.** Merge new info into existing articles rather than creating parallel ones.
6. **Keep summaries fresh.** When an article grows, update its one-line summary in `_index.md`.
7. **Concepts vs Entities.** Don't mix them — a person is an entity, their method is a concept.
