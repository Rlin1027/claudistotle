#!/usr/bin/env python3
"""Extract philosopher and concept entities from a BibTeX file.

Pass 1 of the two-pass ingest pipeline. Deterministically parses BibTeX
structured fields (author, keywords, note annotations) and outputs a JSON
summary of significant entities for the LLM agent (Pass 2) to enrich.

Usage:
    python extract_entities.py <path-to-literature-all.bib>

Output:
    JSON to stdout with "philosophers" and "concepts" arrays.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def slugify(name: str) -> str:
    """Convert a name to a lowercase-hyphenated slug."""
    slug = name.strip().lower()
    slug = re.sub(r"[''`]", "", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def parse_bib_entries(content: str) -> list[dict]:
    """Parse BibTeX entries using brace-depth counting for robustness."""
    entries = []
    i = 0
    while i < len(content):
        # Find the start of an entry: @type{
        match = re.search(r"@(\w+)\{", content[i:])
        if not match:
            break
        entry_start = i + match.start()
        brace_start = i + match.end() - 1  # position of the opening {
        # Count braces to find the matching close
        depth = 0
        j = brace_start
        while j < len(content):
            if content[j] == "{":
                depth += 1
            elif content[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            # Unmatched braces — skip this entry
            i = brace_start + 1
            continue

        body = content[brace_start + 1 : j]
        i = j + 1

        # Extract the citation key (everything before the first comma)
        comma_pos = body.find(",")
        if comma_pos == -1:
            continue
        key = body[:comma_pos].strip()
        fields_text = body[comma_pos + 1 :]

        entry = {"_key": key}
        # Extract fields: fieldname = {value} (with nested braces support)
        field_pattern = re.compile(
            r"(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}",
            re.DOTALL,
        )
        for fm in field_pattern.finditer(fields_text):
            fname = fm.group(1).lower()
            fval = fm.group(2).strip()
            entry[fname] = fval

        entries.append(entry)
    return entries


def extract_authors(entries: list[dict]) -> dict:
    """Extract unique authors with their paper counts and bib keys."""
    authors = defaultdict(
        lambda: {"paper_count": 0, "bib_keys": [], "annotations": [], "is_high": False}
    )
    for entry in entries:
        author_str = entry.get("author", "")
        if not author_str:
            continue
        # Check if this entry is High importance via keywords
        keywords_str = entry.get("keywords", "")
        entry_is_high = any(
            k.strip().lower() == "high" for k in keywords_str.split(",")
        )
        # Split by " and " (BibTeX convention)
        names = re.split(r"\s+and\s+", author_str)
        for name in names:
            name = name.strip()
            if not name:
                continue
            # Normalize: "Last, First" -> "First Last"
            if "," in name:
                parts = name.split(",", 1)
                name = f"{parts[1].strip()} {parts[0].strip()}"
            authors[name]["paper_count"] += 1
            authors[name]["bib_keys"].append(entry["_key"])
            if entry_is_high:
                authors[name]["is_high"] = True

            # Collect note annotations
            note = entry.get("note", "")
            if note:
                for label in ["CORE ARGUMENT:", "RELEVANCE:", "POSITION:"]:
                    idx = note.find(label)
                    if idx != -1:
                        end = len(note)
                        for other in ["CORE ARGUMENT:", "RELEVANCE:", "POSITION:"]:
                            if other != label:
                                oidx = note.find(other, idx + len(label))
                                if oidx != -1:
                                    end = min(end, oidx)
                        snippet = note[idx:end].strip()
                        if snippet and snippet not in authors[name]["annotations"]:
                            authors[name]["annotations"].append(snippet)
    return authors


def extract_concepts(entries: list[dict]) -> dict:
    """Extract concepts from keywords and note annotations."""
    concepts = defaultdict(
        lambda: {"paper_count": 0, "bib_keys": [], "annotations": [], "is_high": False}
    )

    for entry in entries:
        keywords_str = entry.get("keywords", "")
        # Check if this entry is High importance
        entry_is_high = any(
            k.strip().lower() == "high" for k in keywords_str.split(",")
        ) if keywords_str else False

        # From keywords field
        if keywords_str:
            keywords = [k.strip() for k in keywords_str.split(",")]
            for kw in keywords:
                if kw.lower() in ("high", "medium", "low", "") or len(kw) < 3:
                    continue
                concepts[kw]["paper_count"] += 1
                concepts[kw]["bib_keys"].append(entry["_key"])
                if entry_is_high:
                    concepts[kw]["is_high"] = True

        # From note field — look for philosophical concepts (capitalized multi-word terms)
        note = entry.get("note", "")
        if note:
            concept_matches = re.findall(
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", note
            )
            for cm in concept_matches:
                if len(cm.split()) <= 4 and cm not in (
                    "Core Argument",
                    "Related Papers",
                    "Cross Project",
                ):
                    concepts[cm]["paper_count"] += 1
                    concepts[cm]["bib_keys"].append(entry["_key"])

            # Collect relevant annotations for concepts from keywords
            if keywords_str:
                for label in ["CORE ARGUMENT:", "RELEVANCE:"]:
                    idx = note.find(label)
                    if idx != -1:
                        end = len(note)
                        for other in ["CORE ARGUMENT:", "RELEVANCE:", "POSITION:"]:
                            if other != label:
                                oidx = note.find(other, idx + len(label))
                                if oidx != -1:
                                    end = min(end, oidx)
                        snippet = note[idx:end].strip()
                        for kw in keywords_str.split(","):
                            kw = kw.strip()
                            if kw and kw.lower() not in ("high", "medium", "low"):
                                if snippet not in concepts[kw]["annotations"]:
                                    concepts[kw]["annotations"].append(snippet)

    return concepts


def filter_significant(entities: dict, min_papers: int = 2) -> list[dict]:
    """Keep entities appearing in 2+ papers or with High importance."""
    result = []
    for name, data in entities.items():
        if data["paper_count"] >= min_papers or data.get("is_high", False):
            result.append(
                {
                    "name": name,
                    "slug": slugify(name),
                    "paper_count": data["paper_count"],
                    "bib_keys": list(set(data["bib_keys"])),
                    "annotations": data["annotations"][:10],
                }
            )
    result.sort(key=lambda x: x["paper_count"], reverse=True)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_entities.py <path-to-bib-file>", file=sys.stderr)
        sys.exit(1)

    bib_path = Path(sys.argv[1])
    if not bib_path.exists():
        print(f"Error: File not found: {bib_path}", file=sys.stderr)
        sys.exit(1)

    content = bib_path.read_text(encoding="utf-8")
    entries = parse_bib_entries(content)

    if not entries:
        print(
            json.dumps({"philosophers": [], "concepts": [], "entry_count": 0}),
        )
        sys.exit(0)

    authors = extract_authors(entries)
    concepts = extract_concepts(entries)

    result = {
        "entry_count": len(entries),
        "philosophers": filter_significant(authors),
        "concepts": filter_significant(concepts),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
