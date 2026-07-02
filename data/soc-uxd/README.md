# SOC UXD Local Sources

This folder keeps local source data for `soc-uxd.html`.

## Knowledge docs

`knowledge-docs.json` mirrors the embedded `KNOWLEDGE_DOCS` array in `soc-uxd.html`.

Use:

```powershell
python tools\sync_soc_uxd_knowledge_source.py export
```

to refresh the JSON file from the current page.

Use:

```powershell
python tools\sync_soc_uxd_knowledge_source.py import
```

to write the JSON file back into the page after editing it.

## Document library

The document library is the lightweight, publishable layer for uploaded or local UXD source material.

- `manifest.json`: document-center index used by the website.
- `documents/*.md`: AI-retrieval markdown converted from source files.
- `chunks/*.jsonl`: small retrieval chunks loaded by the question assistant.

Original large files stay in the local workspace by default. GitHub Pages should receive only converted text, indexes, and lightweight website assets.

Rebuild the current first batch:

```powershell
python tools\ingest_soc_uxd_documents.py
```

Current ingest mode is archival: preserve source structure, mark inferred conclusions as tentative, and do not turn examples into hard rules unless the source says so.
