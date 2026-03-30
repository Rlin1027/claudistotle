#!/usr/bin/env python3
"""
Generate INDEX.md for a research project workspace.

Scans the project directory and builds a lightweight index covering:
  1. Literature (BibTeX entries) — one line per paper
  2. Full-text sources (sources/secondary/) — downloaded PDFs/MDs
  3. Commentaries (commentary-*.md) — primary text analyses
  4. Reports (reports/) — quality gate and review reports

This index allows Claude to understand what's available without loading
entire files into context. Skills read INDEX.md first, then selectively
load specific entries as needed via Grep or Read.

Usage:
    python generate_index.py reviews/my-thesis/
    python generate_index.py reviews/my-thesis/ --output custom-index.md

Output:
    reviews/[project-name]/INDEX.md (default)

Exit Codes:
    0: Success
    1: Project directory not found
    2: No indexable content found
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def log_progress(message: str) -> None:
    """Emit progress to stderr."""
    print(f"[generate_index.py] {message}", file=sys.stderr, flush=True)


# =============================================================================
# BibTeX Parsing
# =============================================================================

def parse_bib_entries(bib_path: Path) -> list[dict]:
    """Parse BibTeX file and extract compact metadata per entry.

    Extracts: key, type, author, title, year, keywords, position, relevance,
    has_abstract, abstract_source.
    """
    if not bib_path.exists():
        return []

    content = bib_path.read_text(encoding='utf-8')
    entries = []

    # Split into individual entries
    entry_pattern = re.compile(
        r'@(\w+)\s*\{([^,]+),\s*(.*?)\n\}',
        re.DOTALL
    )

    for match in entry_pattern.finditer(content):
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        body = match.group(3)

        entry = {
            'key': key,
            'type': entry_type,
            'author': '',
            'title': '',
            'year': '',
            'keywords': '',
            'position': '',
            'relevance': '',
            'has_abstract': False,
            'abstract_source': '',
        }

        # Extract fields
        entry['author'] = _extract_field(body, 'author')
        entry['title'] = _extract_field(body, 'title')
        entry['year'] = _extract_field(body, 'year')
        entry['keywords'] = _extract_field(body, 'keywords')
        entry['abstract_source'] = _extract_field(body, 'abstract_source')

        # Check for abstract
        abstract = _extract_field(body, 'abstract')
        entry['has_abstract'] = bool(abstract and abstract.strip())

        # Extract position and relevance from note field
        note = _extract_field(body, 'note')
        if note:
            pos_match = re.search(r'POSITION:\s*(.+?)(?:\n|$)', note)
            rel_match = re.search(r'RELEVANCE:\s*(.+?)(?:\n|$)', note)
            if pos_match:
                entry['position'] = pos_match.group(1).strip()
            if rel_match:
                entry['relevance'] = rel_match.group(1).strip()

        entries.append(entry)

    return entries


def _extract_field(body: str, field_name: str) -> str:
    """Extract a BibTeX field value, handling braces and quotes.

    Handles both mid-entry fields (followed by comma) and last fields
    (followed by newline or end of entry).
    """
    # Match field = {value} or field = "value" (multi-line aware)
    # The closing brace/quote may be followed by comma, newline, or end of string
    pattern = re.compile(
        rf'{field_name}\s*=\s*[\{{"](.*?)[\}}"]',
        re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(body)
    if match:
        value = match.group(1).strip()
        # Collapse internal whitespace
        value = re.sub(r'\s+', ' ', value)
        return value
    return ''


def shorten_author(author: str, max_len: int = 30) -> str:
    """Shorten author string: 'Last, First and Last2, First2' -> 'Last & Last2'."""
    if not author:
        return '—'
    # Split by ' and '
    parts = re.split(r'\s+and\s+', author)
    lastnames = []
    for p in parts:
        # Take last name (before comma, or first word)
        if ',' in p:
            lastnames.append(p.split(',')[0].strip())
        else:
            words = p.strip().split()
            if words:
                lastnames.append(words[-1])

    if len(lastnames) <= 2:
        result = ' & '.join(lastnames)
    else:
        result = f"{lastnames[0]} et al."

    if len(result) > max_len:
        result = result[:max_len - 1] + '…'
    return result


def shorten_title(title: str, max_len: int = 60) -> str:
    """Truncate title if too long."""
    if not title:
        return '—'
    if len(title) > max_len:
        return title[:max_len - 1] + '…'
    return title


# =============================================================================
# Directory Scanners
# =============================================================================

def scan_sources_secondary(sources_dir: Path) -> list[dict]:
    """Scan sources/secondary/ for downloaded full-text files."""
    secondary = sources_dir / 'secondary'
    if not secondary.exists():
        return []

    results = []
    for f in sorted(secondary.iterdir()):
        if f.is_file() and not f.name.startswith('.') and f.suffix in ('.md', '.pdf', '.txt'):
            stat = f.stat()
            size_kb = stat.st_size / 1024
            word_count = 0
            if f.suffix == '.md':
                try:
                    text = f.read_text(encoding='utf-8')
                    word_count = len(text.split())
                except Exception:
                    pass

            results.append({
                'filename': f.name,
                'format': f.suffix[1:].upper(),
                'size_kb': round(size_kb, 1),
                'word_count': word_count,
            })
    return results


def scan_sources_primary(sources_dir: Path) -> list[dict]:
    """Scan sources/primary/ for user-provided primary texts."""
    primary = sources_dir / 'primary'
    if not primary.exists():
        return []

    results = []
    for f in sorted(primary.iterdir()):
        if f.is_file() and not f.name.startswith('.'):
            stat = f.stat()
            size_kb = stat.st_size / 1024
            results.append({
                'filename': f.name,
                'format': f.suffix[1:].upper() if f.suffix else '?',
                'size_kb': round(size_kb, 1),
            })
    return results


def scan_commentaries(project_dir: Path) -> list[dict]:
    """Scan commentary-*.md files and extract metadata."""
    results = []
    for f in sorted(project_dir.glob('commentary-*.md')):
        info = {
            'filename': f.name,
            'slug': f.stem.replace('commentary-', ''),
            'subject': '',
            'concepts': '',
            'word_count': 0,
        }
        try:
            text = f.read_text(encoding='utf-8')
            info['word_count'] = len(text.split())

            # Try to extract subject from first heading or Subject line
            subj_match = re.search(r'(?:\*\*(?:主題|Subject)[：:]\*\*|(?:主題|Subject)[：:])\s*(.+)', text)
            if subj_match:
                info['subject'] = subj_match.group(1).strip()

            # Try to extract concepts — look for keywords or key terms
            # Also check for the preliminary textual analysis section
            purpose_match = re.search(r'(?:\*\*(?:目的|Purpose)[：:]\*\*|(?:目的|Purpose)[：:])\s*(.+)', text)
            if purpose_match:
                info['concepts'] = purpose_match.group(1).strip()[:80]
        except Exception:
            pass

        results.append(info)
    return results


def scan_reports(reports_dir: Path) -> list[dict]:
    """Scan reports/ directory for quality reports."""
    if not reports_dir.exists():
        return []

    results = []
    for f in sorted(reports_dir.glob('*.md')):
        info = {
            'filename': f.name,
            'type': '',
            'date': '',
            'summary': '',
        }

        # Parse type from filename pattern
        name = f.stem
        if name.startswith('validate-coverage'):
            info['type'] = 'Validate Mode A'
        elif name.startswith('validate-citation'):
            info['type'] = 'Validate Mode B'
        elif name.startswith('validate-record'):
            info['type'] = 'Validate Mode C'
        elif name.startswith('refine-analysis'):
            info['type'] = 'Refine Analysis'
        elif name.startswith('review-round'):
            round_match = re.search(r'round(\d)', name)
            rn = round_match.group(1) if round_match else '?'
            info['type'] = f'Peer Review R{rn}'
        elif name.startswith('feedback-session'):
            info['type'] = 'Feedback Session'
        else:
            info['type'] = 'Other'

        # Extract date from filename
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', name)
        if date_match:
            info['date'] = date_match.group(1)

        # Try to extract recommendation/result from file content
        try:
            text = f.read_text(encoding='utf-8')
            rec_match = re.search(
                r'(?:RECOMMENDATION|VERDICT|RECOMMENDATION:)\s*\n?\s*\[?[xX ]\]?\s*(.+)',
                text
            )
            if rec_match:
                info['summary'] = rec_match.group(1).strip()[:60]
        except Exception:
            pass

        results.append(info)
    return results


# =============================================================================
# INDEX.md Generation
# =============================================================================

def generate_index(project_dir: Path) -> str:
    """Generate the complete INDEX.md content."""
    lines = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines.append('# Research Data Index')
    lines.append('')
    lines.append(f'> Auto-generated: {now}')
    lines.append('> This file is generated by `generate_index.py` for quick lookup by Claude.')
    lines.append('> For full content of specific sources, use Grep or Read to search by bib key.')
    lines.append('')

    # ── Section 1: Literature Index ──
    bib_path = project_dir / 'literature-all.bib'
    bib_entries = parse_bib_entries(bib_path)

    lines.append('---')
    lines.append('')
    lines.append('## Literature Index (literature-all.bib)')
    lines.append('')

    if bib_entries:
        lines.append(f'{len(bib_entries)} total sources.')
        lines.append('')
        lines.append('| Key | Author | Year | Title | Type | Position | Has Abstract |')
        lines.append('|-----|--------|------|-------|------|----------|--------------|')
        for e in bib_entries:
            author = shorten_author(e['author'])
            title = shorten_title(e['title'])
            pos = e['position'][:20] if e['position'] else '—'
            has_abs = '✅' if e['has_abstract'] else '❌'
            etype = e['type']
            lines.append(
                f"| `{e['key']}` | {author} | {e['year'] or '—'} "
                f"| {title} | {etype} | {pos} | {has_abs} |"
            )
    else:
        lines.append('No literature entries yet.')

    lines.append('')

    # ── Section 2: Full-Text Sources ──
    sources_dir = project_dir / 'sources'

    lines.append('---')
    lines.append('')
    lines.append('## Full-Text Index (sources/)')
    lines.append('')

    # Secondary
    secondary = scan_sources_secondary(sources_dir)
    lines.append('### Secondary Sources (secondary/)')
    lines.append('')
    if secondary:
        lines.append(f'{len(secondary)} file(s).')
        lines.append('')
        lines.append('| Filename | Format | Size | Word Count |')
        lines.append('|------|------|------|------|')
        for s in secondary:
            wc = f"{s['word_count']:,}" if s['word_count'] else '—'
            lines.append(
                f"| {s['filename']} | {s['format']} "
                f"| {s['size_kb']} KB | {wc} |"
            )
    else:
        lines.append('No full-text downloads yet.')

    lines.append('')

    # Primary
    primary = scan_sources_primary(sources_dir)
    lines.append('### Primary Sources (primary/)')
    lines.append('')
    if primary:
        lines.append(f'{len(primary)} file(s).')
        lines.append('')
        lines.append('| Filename | Format | Size |')
        lines.append('|------|------|------|')
        for p in primary:
            lines.append(
                f"| {p['filename']} | {p['format']} | {p['size_kb']} KB |"
            )
    else:
        lines.append('No primary sources yet.')

    lines.append('')

    # ── Section 3: Commentaries ──
    commentaries = scan_commentaries(project_dir)

    lines.append('---')
    lines.append('')
    lines.append('## Text Commentary Index (commentary-*.md)')
    lines.append('')

    if commentaries:
        lines.append(f'{len(commentaries)} commentar(ies).')
        lines.append('')
        lines.append('| Filename | Subject | Topic/Purpose | Word Count |')
        lines.append('|------|---------|----------|------|')
        for c in commentaries:
            subj = c['subject'][:40] if c['subject'] else c['slug']
            concepts = c['concepts'][:40] if c['concepts'] else '—'
            wc = f"{c['word_count']:,}" if c['word_count'] else '—'
            lines.append(f"| {c['filename']} | {subj} | {concepts} | {wc} |")
    else:
        lines.append('No text commentaries yet.')

    lines.append('')

    # ── Section 4: Reports ──
    reports = scan_reports(project_dir / 'reports')

    lines.append('---')
    lines.append('')
    lines.append('## Quality Reports Index (reports/)')
    lines.append('')

    if reports:
        lines.append(f'{len(reports)} report(s).')
        lines.append('')
        lines.append('| Filename | Type | Date | Result Summary |')
        lines.append('|------|------|------|---------|')
        for r in reports:
            summary = r['summary'] if r['summary'] else '—'
            lines.append(
                f"| {r['filename']} | {r['type']} "
                f"| {r['date'] or '—'} | {summary} |"
            )
    else:
        lines.append('No quality reports yet.')

    lines.append('')

    # ── Section 5: Summary Statistics ──
    lines.append('---')
    lines.append('')
    lines.append('## Summary Statistics')
    lines.append('')

    total_bib = len(bib_entries)
    with_abstract = sum(1 for e in bib_entries if e['has_abstract'])
    total_secondary = len(secondary)
    total_primary = len(primary)
    total_commentary = len(commentaries)
    total_reports = len(reports)

    lines.append(f'- Literature entries: {total_bib} ({with_abstract} with abstracts)')
    lines.append(f'- Secondary source full texts: {total_secondary} file(s)')
    lines.append(f'- Primary sources: {total_primary} file(s)')
    lines.append(f'- Text commentaries: {total_commentary}')
    lines.append(f'- Quality reports: {total_reports}')
    lines.append('')

    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate INDEX.md for a Claudistotle research project.'
    )
    parser.add_argument(
        'project_dir',
        help='Path to the project directory (e.g., reviews/my-thesis/)'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output file path (default: [project_dir]/INDEX.md)'
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not project_dir.is_dir():
        log_progress(f"Error: Directory not found: {project_dir}")
        sys.exit(1)

    output_path = Path(args.output) if args.output else project_dir / 'INDEX.md'

    log_progress(f"Scanning project: {project_dir}")

    content = generate_index(project_dir)

    output_path.write_text(content, encoding='utf-8')
    log_progress(f"INDEX.md written to: {output_path}")

    # Print summary to stdout (for skill completion messages)
    bib_count = len(parse_bib_entries(project_dir / 'literature-all.bib'))
    source_count = len(scan_sources_secondary(project_dir / 'sources'))
    commentary_count = len(list(project_dir.glob('commentary-*.md')))
    report_count = len(list((project_dir / 'reports').glob('*.md'))) if (project_dir / 'reports').exists() else 0

    print(f"INDEX.md generated: {bib_count} bib entries, {source_count} sources, "
          f"{commentary_count} commentaries, {report_count} reports")


if __name__ == '__main__':
    main()
