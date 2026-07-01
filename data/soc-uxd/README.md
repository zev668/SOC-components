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
