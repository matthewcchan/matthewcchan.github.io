#!/usr/bin/env python3
"""Convert publications.bib to data/publications.yaml for Hugo.

Usage:
    python scripts/bib_to_data.py

Reads:  publications.bib  (project root)
Writes: data/publications.yaml
"""

import re
import sys
from pathlib import Path

try:
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
except ImportError:
    print("Missing dependency: pip install bibtexparser")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Missing dependency: pip install PyYAML")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Author to bold in the author list (substring match against BibTeX author field)
HIGHLIGHT_AUTHOR = "Chan, Matthew"

# Map filter-tag keys → display labels shown as pub-tag chips.
# None  = filter-only (institution tags); omit from the visible tag list.
TAG_DISPLAY = {
    "transporter":        "Transporter",
    "molecular-dynamics": "Molecular Dynamics",
    "mrna-translation":   "mRNA Translation",
    "cryo-em":            "Cryo-EM",
    "machine-learning":   "Machine Learning",
    "covid":              "COVID-19",
    "catalysis":          "Catalysis",
    "review":             "Review",
    "uab":                "UAB",
    "uiuc":               "UIUC",
    "fred-hutch":         "Fred Hutch",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean(value: str) -> str:
    """Strip BibTeX grouping braces and normalize whitespace."""
    value = re.sub(r"[{}]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def name_to_initials(name: str) -> str:
    """Convert 'Last, First Middle' → 'F. M. Last'."""
    name = name.strip()
    if "," in name:
        last, rest = name.split(",", 1)
        firsts = rest.strip().split()
    else:
        parts = name.split()
        last = parts[-1]
        firsts = parts[:-1]
    initials = " ".join(f[0] + "." for f in firsts if f)
    return f"{initials} {last.strip()}" if initials else last.strip()


def parse_cofirst(value: str) -> set:
    """Parse '1, 2' into a 0-indexed set {0, 1}."""
    result = set()
    for part in value.split(","):
        try:
            result.add(int(part.strip()) - 1)
        except ValueError:
            pass
    return result


def format_authors_html(authors_field: str, cofirst_indices: set, corresponding_indices: set) -> str:
    """Return an HTML author string with bolding, co-first asterisks, and corresponding-author daggers."""
    authors = [a.strip() for a in authors_field.split(" and ")]
    parts = []
    for i, author in enumerate(authors):
        name = name_to_initials(author)
        if i in cofirst_indices:
            name += "*"
        if i in corresponding_indices:
            name += "<sup>†</sup>"
        if HIGHLIGHT_AUTHOR.lower() in author.lower():
            name = f"<b>{name}</b>"
        parts.append(name)
    return ", ".join(parts)


def normalize_doi(doi: str) -> str:
    """Strip https://doi.org/ prefix if present."""
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/"):
        if doi.startswith(prefix):
            return doi[len(prefix):]
    return doi


# ---------------------------------------------------------------------------
# Entry conversion
# ---------------------------------------------------------------------------

def entry_to_dict(entry: dict) -> dict:
    entrytype = entry["ENTRYTYPE"]

    # Co-first authorship
    cofirst = parse_cofirst(entry.get("cofirst", ""))

    # Corresponding authorship
    corresponding = parse_cofirst(entry.get("corresponding", ""))

    # Author HTML
    authors_html = format_authors_html(entry.get("author", ""), cofirst, corresponding)

    # Tags
    tags_raw = entry.get("tags", "")
    filter_tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    display_tags = [TAG_DISPLAY[t] for t in filter_tags if TAG_DISPLAY.get(t)]

    # DOI
    doi = normalize_doi(entry.get("doi", ""))

    # Publication type and status
    if entrytype == "incollection":
        pub_type = "book"
        status = "published"
    elif entrytype == "unpublished":
        pub_type = "unpublished"
        status = "preprint"
    else:
        pub_type = "article"
        status = "published"

    record = {
        "citekey":      entry["ID"],
        "pub_type":     pub_type,
        "status":       status,
        "title":        clean(entry.get("title", "")),
        "authors_html": authors_html,
        "year":         entry.get("year", ""),
        "doi":          doi,
        "preprint_url": entry.get("preprint", ""),
        "abstract_url": entry.get("abstract_url", ""),
        "image":        entry.get("image", ""),
        "image_alt":    entry.get("image_alt", ""),
        "filter_tags":  filter_tags,
        "display_tags": display_tags,
        "badge":        clean(entry.get("badge", "")),
        "note":         entry.get("note", ""),
    }

    if pub_type == "article" and status == "published":
        record["journal"] = clean(entry.get("journal", ""))
        record["volume"]  = entry.get("volume", "")
        record["number"]  = entry.get("number", "")
        record["pages"]   = entry.get("pages", "").replace("--", "\u2013")

    if pub_type == "book":
        record["booktitle"] = clean(entry.get("booktitle", ""))
        record["editor"]    = name_to_initials(entry.get("editor", "")) if entry.get("editor") else ""
        record["publisher"] = clean(entry.get("publisher", ""))

    return record


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    root = Path(__file__).resolve().parent.parent
    bib_path = root / "publications.bib"
    out_path = root / "data" / "publications.yaml"

    if not bib_path.exists():
        print(f"Error: {bib_path} not found")
        sys.exit(1)

    out_path.parent.mkdir(exist_ok=True)

    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode

    with open(bib_path, encoding="utf-8") as f:
        db = bibtexparser.load(f, parser)

    entries = [entry_to_dict(e) for e in db.entries]

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(entries, f, allow_unicode=True, default_flow_style=False,
                  sort_keys=False)

    print(f"Wrote {len(entries)} entries → {out_path}")


if __name__ == "__main__":
    main()
