#!/usr/bin/env python3
"""Split a paper markdown file into per-section files.

Usage:
    python3 split_paper.py --input full.md --output sections/

Splits on top-level headings (# or ##) and writes each section
to a kebab-case named file. Also generates a README.md with TOC.
"""
import argparse
import re
from pathlib import Path


def slugify(text: str, max_len: int = 50) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len]


CANONICAL_SECTIONS = {
    "abstract": "abstract",
    "introduction": "introduction",
    "background": "background",
    "related work": "related-work",
    "related works": "related-work",
    "literature review": "literature-review",
    "methods": "methods",
    "method": "methods",
    "materials and methods": "methods",
    "methodology": "methods",
    "experimental setup": "experimental-setup",
    "experiments": "experiments",
    "results": "results",
    "results and discussion": "results-and-discussion",
    "discussion": "discussion",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "acknowledgements": "acknowledgements",
    "acknowledgments": "acknowledgements",
    "references": "references",
    "bibliography": "references",
    "supplementary": "supplementary",
    "supplementary materials": "supplementary",
    "appendix": "appendix",
    "data availability": "data-availability",
    "code availability": "code-availability",
}


def normalize_section_name(heading: str) -> str:
    clean = re.sub(r"^\d+[\.\)]\s*", "", heading.strip())
    lower = clean.lower().strip()
    if lower in CANONICAL_SECTIONS:
        return CANONICAL_SECTIONS[lower]
    return slugify(clean)


def split_markdown(text: str) -> list[tuple[str, str]]:
    """Split markdown into (heading, content) pairs."""
    pattern = re.compile(r"^(#{1,2})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))

    if not matches:
        return [("full-text", text)]

    sections = []

    # Content before first heading (if any, treat as preamble/abstract)
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if len(preamble) > 100:
            sections.append(("preamble", preamble))

    for i, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            name = normalize_section_name(heading)
            sections.append((name, f"# {heading}\n\n{content}"))

    return sections


def main():
    parser = argparse.ArgumentParser(description="Split paper markdown into sections")
    parser.add_argument("--input", required=True, help="Path to full markdown file")
    parser.add_argument("--output", required=True, help="Output directory for sections")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    text = input_path.read_text(encoding="utf-8")
    sections = split_markdown(text)

    # Deduplicate names
    seen: dict[str, int] = {}
    toc = []
    for name, content in sections:
        if name in seen:
            seen[name] += 1
            fname = f"{name}-{seen[name]}"
        else:
            seen[name] = 1
            fname = name

        fpath = output_dir / f"{fname}.md"
        fpath.write_text(content, encoding="utf-8")

        # Extract heading for TOC
        first_line = content.split("\n")[0].strip("# ").strip()
        toc.append((fname, first_line))

    # Generate README
    readme_lines = ["# Sections\n"]
    for fname, title in toc:
        readme_lines.append(f"- [{title}](sections/{fname}.md)")

    readme_path = output_dir.parent / "README.md"
    # Only write section TOC if README doesn't exist yet (it may be created by read-paper later)
    if not readme_path.exists():
        readme_path.write_text("\n".join(readme_lines) + "\n", encoding="utf-8")

    print(f"Split into {len(sections)} sections: {', '.join(n for n, _ in toc)}")


if __name__ == "__main__":
    main()
