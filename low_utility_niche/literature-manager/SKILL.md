---
name: literature-manager
description: Search, download, convert, organize, and audit academic literature collections. Use when asked to find papers, build a literature library, add papers to references, download PDFs, convert papers to markdown, organize references by category, audit a reference collection, or collect code/dataset links for tools mentioned in papers.
---

# Literature Manager

Manage academic literature collections: search → download → convert → organize → verify.

## Dependencies

- `pdftotext` (poppler-utils) — PDF text extraction
- `curl` — downloading
- `python3` — JSON processing in audit
- `file` (coreutils) — PDF validation
- `uvx markitdown` (optional) — fallback PDF→MD converter

## Quick Start

```bash
# Download a single paper by DOI
bash scripts/download.sh "10.1038/s41592-024-02200-1" output_dir/

# Convert PDF to markdown
bash scripts/convert.sh paper.pdf output.md

# Verify a single PDF+MD pair
bash scripts/verify.sh paper.pdf paper.md

# Full audit of a references/ folder
bash scripts/audit.sh /path/to/references/
```

## Workflow

### 1. Search

Use `web_fetch` on Google Scholar:
```
https://scholar.google.com/scholar?q=QUERY&as_ylo=YEAR
```
Extract: title, authors, year, journal, DOI, PDF links.

For each result, identify the best open-access PDF source (see Download Strategy).

### 2. Download

Run `scripts/download.sh <DOI_or_URL> <output_dir/>` per paper. The script tries sources in order:
1. Direct publisher PDF (Nature, eLife, Frontiers, PNAS, bioRxiv, arXiv)
2. EuropePMC (`PMC_ID` → PDF)
3. bioRxiv/arXiv preprint

If all fail, flag for manual download (paywall). Provide the user with the URL.

### 3. Convert

Run `scripts/convert.sh <input.pdf> <output.md>`. Uses `pdftotext` (reliable) with `uvx markitdown` as fallback.

### 4. Organize

Standard folder structure:
```
references/
├── README.md              # Human index (summaries per category)
├── index.json             # Machine index (structured metadata)
├── RESOURCES.md           # Code repos + datasets
├── resources.json         # Structured version
├── <category-1>/
│   ├── papers/            # PDFs
│   └── markdown/          # Converted text
└── <category-N>/
    ├── papers/
    └── markdown/
```

Categories are user-defined. Number-prefix for sort order (e.g., `01-theoretical-frameworks/`).

#### index.json schema per paper
```json
{
  "id": "short_id",
  "title": "Full title",
  "authors": ["Author1", "Author2"],
  "year": 2024,
  "journal": "Journal Name",
  "doi": "10.xxxx/...",
  "category": "category_name",
  "subcategory": "optional",
  "pdf_path": "category/papers/filename.pdf",
  "markdown_path": "category/markdown/filename.md",
  "tags": ["tag1", "tag2"],
  "one_line_summary": "English one-liner",
  "key_concepts": ["concept1"],
  "relevance_to_project": "English description"
}
```

#### README.md pattern
Per category section, per paper: title, authors, year, journal, DOI, short summary in user's language.

### 5. Verify

Run `scripts/audit.sh <references_dir/>` for full verification:
- Every PDF is valid (`file -b` = PDF)
- Every PDF title matches filename (`pdftotext | head`)
- Every PDF has matching markdown (and vice versa)
- index.json is valid, complete, paths exist, no duplicate IDs
- README.md stats match actual counts

### 6. Collect Resources

For tool/method papers, find GitHub repos and public datasets. Store in `RESOURCES.md` + `resources.json`.

## Sub-agent Strategy

For large batches, parallelize:
- **Download**: 1 sub-agent per batch of ~5-8 papers
- **Organize**: 1 sub-agent to build indexes
- **Verify**: 1 independent sub-agent (never the same as organizer)

Always use a separate sub-agent for verification (QC should not self-grade).

## Adding Papers Incrementally

To add papers to an existing collection:
1. Download + convert new papers into correct category folder
2. Append entries to index.json
3. Update README.md stats
4. Run audit to verify consistency
