from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "soc-uxd.html"
DEFAULT_SOURCE = ROOT / "data" / "soc-uxd" / "knowledge-docs.json"
DEFAULT_MULTILINGUAL_REF = (
    ROOT.parent
    / ".codex"
    / "skills"
    / "game-interaction-design"
    / "references"
    / "multilingual-spec.md"
)
DEFAULT_INTERACTION_PRINCIPLES_REF = (
    ROOT.parent
    / ".codex"
    / "skills"
    / "game-interaction-design"
    / "references"
    / "soc-interaction-design-principles.md"
)
DEFAULT_DESIGN_LANGUAGE_REF = (
    ROOT.parent
    / "external-references"
    / "ant-design-spec"
    / "combined-cn"
)
DESIGN_LANGUAGE_COLLECTION_ID = "soc-design-language"
LEGACY_INTERACTION_PRINCIPLES_ID = "soc-interaction-principles"
DESIGN_LANGUAGE_TITLE = "通用设计原则"
DESIGN_LANGUAGE_SUMMARY = (
    "复用 Ant Design 17 项设计原则原文结构，作为 SOC UXD 的通用交互设计原则参考。"
)

KNOWLEDGE_DOCS_RE = re.compile(
    r"const\s+KNOWLEDGE_DOCS\s*=\s*(\[.*?\]);\s*let\s+currentKnowledgeDocId",
    re.S,
)


def extract_knowledge_docs(html: str) -> list[dict[str, Any]]:
    match = KNOWLEDGE_DOCS_RE.search(html)
    if not match:
        raise ValueError("Cannot locate KNOWLEDGE_DOCS block")
    docs = json.loads(match.group(1))
    if not isinstance(docs, list):
        raise ValueError("KNOWLEDGE_DOCS must be a JSON list")
    return docs


def inject_knowledge_docs(html: str, docs: list[dict[str, Any]]) -> str:
    match = KNOWLEDGE_DOCS_RE.search(html)
    if not match:
        raise ValueError("Cannot locate KNOWLEDGE_DOCS block")
    encoded_docs = json.dumps(sanitize_knowledge_docs(docs), ensure_ascii=False, indent=2)
    return html[: match.start(1)] + encoded_docs + html[match.end(1) :]


def strip_markdown_frontmatter(content: str) -> str:
    if content.startswith("---"):
        match = re.match(r"^---\n.*?\n---\n?(.*)$", content, re.S)
        if match:
            return match.group(1)
    return content


def clean_text(value: str) -> str:
    value = value.replace("\ufffd", "")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def has_bad_text(value: str) -> bool:
    return "\ufffd" in value or bool(re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", value))


def markdown_summary_from_b64(content_b64: str, *, max_chars: int = 92) -> str:
    try:
        content = base64.b64decode(content_b64.encode("ascii")).decode("utf-8")
    except Exception:
        return ""
    content = strip_markdown_frontmatter(content)
    paragraphs: list[str] = []
    current: list[str] = []
    in_code = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not stripped:
            if current:
                paragraphs.append(clean_text(" ".join(current)))
                current = []
            continue
        if stripped.startswith(("#", "|", "- [", "---")):
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        if stripped.startswith("> "):
            stripped = stripped[2:].strip()
        current.append(stripped)
    if current:
        paragraphs.append(clean_text(" ".join(current)))
    summary = next((item for item in paragraphs if item), "")
    if len(summary) > max_chars:
        summary = summary[: max_chars - 1].rstrip("，。、；;,. ") + "..."
    return summary


def sanitize_doc_entry(doc: dict[str, Any]) -> dict[str, Any]:
    next_doc = dict(doc)
    original_summary = next_doc.get("summary")
    summary_had_bad_text = isinstance(original_summary, str) and has_bad_text(original_summary)
    for key in ("title", "file", "summary"):
        value = next_doc.get(key)
        if isinstance(value, str):
            next_doc[key] = clean_text(value)

    content_b64 = next_doc.get("contentB64")
    if summary_had_bad_text and isinstance(content_b64, str):
        rebuilt = markdown_summary_from_b64(content_b64)
        if rebuilt:
            next_doc["summary"] = rebuilt

    if next_doc.get("kind") == "collection":
        pages = next_doc.get("pages")
        if isinstance(pages, list):
            next_doc["pages"] = [
                sanitize_doc_entry(page) if isinstance(page, dict) else page for page in pages
            ]
    return next_doc


def sanitize_knowledge_docs(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [sanitize_doc_entry(doc) for doc in docs]


def build_markdown_doc_entry(
    *,
    doc_id: str,
    title: str,
    file_label: str,
    summary: str,
    source_path: Path,
) -> dict[str, Any]:
    content = source_path.read_text(encoding="utf-8")
    return {
        "id": doc_id,
        "title": title,
        "file": file_label,
        "summary": summary,
        "lines": len(content.splitlines()),
        "contentB64": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }


def upsert_knowledge_doc(docs: list[dict[str, Any]], entry: dict[str, Any]) -> list[dict[str, Any]]:
    next_docs = [dict(doc) for doc in docs]
    for index, doc in enumerate(next_docs):
        if doc.get("id") == entry.get("id"):
            next_docs[index] = entry
            return next_docs
    next_docs.append(entry)
    return next_docs


def build_soc_design_language_collection(ref_dir: Path = DEFAULT_DESIGN_LANGUAGE_REF) -> dict[str, Any]:
    manifest_path = ref_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pages: list[dict[str, Any]] = []
    local_markdown_dir = ref_dir / "markdown"
    combined_html_path = ref_dir / "ant-spec-combined-clone.html"

    def source_md_to_github_url(url: str) -> str:
        match = re.match(r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)$", url)
        if not match:
            return url
        owner, repo, branch, path = match.groups()
        return f"https://github.com/{owner}/{repo}/blob/{branch}/{path}"

    for fallback_order, page_meta in enumerate(manifest.get("pages", [])):
        slug = str(page_meta["slug"])
        if local_markdown_dir.exists():
            md_path = local_markdown_dir / f"{slug}.local-images.md"
            source_md = str(page_meta.get("sourceMd", ""))
            source_file = Path(source_md).name or f"{slug}.zh-CN.md"
            source_page_url = str(page_meta.get("sourcePage", f"https://ant.design/docs/spec/{slug}-cn"))
            source_md_url = source_md_to_github_url(source_md)
            file_label = f"assets/ant-design-spec/combined-cn/markdown/{slug}.local-images.md"
            page_order = fallback_order
            related: list[str] = []
        else:
            md_path = ref_dir / f"{slug}.md"
            source_file = page_meta["sourceFile"]
            source_page_url = page_meta["sourcePageUrl"]
            source_md_url = page_meta["sourceMdUrl"]
            file_label = f"references/soc-design-language/{slug}.md"
            page_order = int(page_meta["order"])
            related = page_meta.get("related", [])
        content = md_path.read_text(encoding="utf-8")
        page = {
            "slug": slug,
            "title": page_meta["title"],
            "group": DESIGN_LANGUAGE_TITLE,
            "order": page_order,
            "file": file_label,
            "sourceFile": source_file,
            "sourceTitle": page_meta.get("sourceTitle", ""),
            "sourcePageUrl": source_page_url,
            "sourceMdUrl": source_md_url,
            "related": related,
            "lines": len(content.splitlines()),
            "contentB64": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        }
        pages.append(page)

    collection = {
        "id": DESIGN_LANGUAGE_COLLECTION_ID,
        "kind": "collection",
        "title": DESIGN_LANGUAGE_TITLE,
        "file": "references/soc-design-language/manifest.json",
        "summary": DESIGN_LANGUAGE_SUMMARY,
        "groups": [DESIGN_LANGUAGE_TITLE],
        "source": manifest.get("source", {}),
        "lines": sum(int(page["lines"]) for page in pages),
        "pages": pages,
    }
    if combined_html_path.exists():
        combined_html = combined_html_path.read_text(encoding="utf-8")
        collection["combinedHtmlFile"] = (
            "assets/ant-design-spec/combined-cn/ant-spec-combined-clone.html"
        )
        collection["combinedHtmlB64"] = base64.b64encode(
            combined_html.encode("utf-8")
        ).decode("ascii")
    return collection


def upsert_design_language_collection(
    docs: list[dict[str, Any]], collection: dict[str, Any]
) -> list[dict[str, Any]]:
    next_docs: list[dict[str, Any]] = []
    inserted = False
    for doc in docs:
        doc_id = doc.get("id")
        if doc_id in {DESIGN_LANGUAGE_COLLECTION_ID, LEGACY_INTERACTION_PRINCIPLES_ID}:
            if not inserted:
                next_docs.append(collection)
                inserted = True
            continue
        next_docs.append(dict(doc))
    if not inserted:
        next_docs.append(collection)
    return next_docs


def ensure_multilingual_home_quick_entry(html: str) -> str:
    if re.search(r"\[[^\n\]]*'doc','multilingual-spec'\]", html):
        return html
    prompt_quick_entry = re.search(r"(?P<indent>[ \t]*)\[[^\n\]]*'doc','prompt-system'\],", html)
    if not prompt_quick_entry:
        return html
    indent = prompt_quick_entry.group("indent")
    multilingual_entry = (
        f"{indent}['多语言规范','文本长度、换行、省略、变量、伪本地化和术语规则。','doc','multilingual-spec'],"
    )
    return html[: prompt_quick_entry.end()] + "\n" + multilingual_entry + html[prompt_quick_entry.end() :]


def ensure_design_language_home_quick_entry(html: str) -> str:
    if re.search(r"\[[^\n\]]*'doc','soc-design-language'\]", html):
        return html
    multilingual_quick_entry = re.search(
        r"(?P<indent>[ \t]*)\['多语言规范',[^\n\]]*'doc','multilingual-spec'\],",
        html,
    )
    fallback_quick_entry = re.search(
        r"(?P<indent>[ \t]*)\['界面框架规则',[^\n\]]*'doc','fullscreen-framework-translation'\],",
        html,
    )
    target = multilingual_quick_entry or fallback_quick_entry
    if not target:
        return html
    indent = target.group("indent")
    design_language_entry = f"{indent}['{DESIGN_LANGUAGE_TITLE}','Ant Design 17 项设计原则原文结构。','doc','soc-design-language'],\n"
    return html[: target.end()] + "\n" + design_language_entry + html[target.end() :]


def ensure_design_language_top_nav_entry(html: str) -> str:
    if re.search(r"\{action:'doc',id:'soc-design-language',title:'(?:SOC 设计语言目录|通用设计原则)'", html):
        return html.replace("id:'soc-design-language',title:'SOC 设计语言目录'", "id:'soc-design-language',title:'通用设计原则'")
    if re.search(r"\{action:'doc',id:'soc-design-language',title:'通用设计原则'", html):
        return html
    multilingual_nav_entry = re.search(
        r"(?P<indent>[ \t]*)\{action:'doc',id:'multilingual-spec',[^\n]*\},",
        html,
    )
    fallback_nav_entry = re.search(
        r"(?P<indent>[ \t]*)\{action:'doc',id:'fullscreen-framework-translation',[^\n]*\},",
        html,
    )
    target = multilingual_nav_entry or fallback_nav_entry
    if not target:
        return html
    indent = target.group("indent")
    design_language_entry = f"{indent}{{action:'doc',id:'soc-design-language',title:'{DESIGN_LANGUAGE_TITLE}',desc:'{DESIGN_LANGUAGE_SUMMARY}'}},\n"
    return html[: target.end()] + "\n" + design_language_entry + html[target.end() :]


def ensure_design_language_rules_area_entry(html: str) -> str:
    design_language_entry = (
        "{kind:'doc',doc:'soc-design-language',title:'通用设计原则',status:'ready',"
        "desc:'复用 Ant Design 17 项设计原则原文结构，作为 SOC UXD 的通用交互设计原则参考。'}"
    )
    entry_pattern = re.compile(
        r"(?P<indent>[ \t]*)\{kind:'doc',doc:'soc-design-language',title:'(?:SOC 设计语言目录|通用设计原则)',status:'ready',"
        r"desc:'(?:沿 Ant Design 原结构重写的 SOC 设计语言目录：价值观、原则、全局样式、通用规则和页面模式。|沿 Ant Design 左侧 17 项原则结构整理的 SOC UXD 交互判断、交付要求和参考文档。|复用 Ant Design 17 项设计原则原文结构，作为 SOC UXD 的通用交互设计原则参考。)'\},?\n?"
    )
    existing = entry_pattern.search(html)
    indent = existing.group("indent") if existing else "      "
    updated = entry_pattern.sub("", html)
    multilingual_area_entries = list(re.finditer(
        r"(?P<indent>[ \t]*)\{kind:'doc',doc:'multilingual-spec',[^\n]*\},",
        updated,
    ))
    fallback_area_entries = list(re.finditer(
        r"(?P<indent>[ \t]*)\{kind:'doc',doc:'fullscreen-framework-translation',[^\n]*\},",
        updated,
    ))
    targets = multilingual_area_entries or fallback_area_entries
    if not targets:
        return html
    for target in reversed(targets):
        indent = target.group("indent") or indent
        inserted = f"{indent}{design_language_entry},\n"
        updated = updated[: target.end()] + "\n" + inserted + updated[target.end() :]
    return updated


def connect_multilingual_spec(html: str) -> str:
    replacements = {
        "{title:'多语言规范',status:'todo',desc:'后续整理文本长度、换行、省略、变量、语言切换与排版约束。'}":
        "{kind:'doc',doc:'multilingual-spec',title:'多语言规范',status:'ready',desc:'文本膨胀、换行、省略、变量、伪本地化、术语和地区资源替换规则。'}",
        "{title:'多语言规范',status:'todo',desc:'待整理文本长度、换行、省略、变量与语言切换约束。'}":
        "{kind:'doc',doc:'multilingual-spec',title:'多语言规范',status:'ready',desc:'文本膨胀、换行、省略、变量、伪本地化、术语和地区资源替换规则。'}",
        "['多语言规范','后续整理文本长度、换行、省略、变量和语言切换约束。','todo']":
        "['多语言规范','文本长度、换行、省略、变量、伪本地化和术语规则。','ready']",
        "['多语言规范','rules','todo']":
        "['多语言规范','rules','multilingual-spec','doc']",
    }
    updated = html
    for old, new in replacements.items():
        if old in updated:
            updated = updated.replace(old, new, 1)
        elif new not in updated:
            raise ValueError(f"Cannot locate multilingual placeholder: {old}")
    return ensure_multilingual_home_quick_entry(updated)


def connect_interaction_principles_spec(html: str) -> str:
    replacements = {
        "{title:'通用交互设计原则',status:'todo',desc:'后续沉淀 SOC 项目的通用交互判断原则。'}":
        "{kind:'doc',doc:'soc-interaction-principles',title:'通用交互设计原则',status:'ready',desc:'基于 Ant Design 设计语言内化的 SOC 通用交互原则：上下文、邀请、反馈、状态、文案、导航、动效和组件沉淀。'}",
        "{title:'通用交互设计原则',status:'todo',desc:'待沉淀 SOC 项目通用交互判断原则。'}":
        "{kind:'doc',doc:'soc-interaction-principles',title:'通用交互设计原则',status:'ready',desc:'基于 Ant Design 设计语言内化的 SOC 通用交互原则：上下文、邀请、反馈、状态、文案、导航、动效和组件沉淀。'}",
    }
    updated = html
    for old, new in replacements.items():
        if old in updated:
            updated = updated.replace(old, new, 1)
        elif new not in updated:
            raise ValueError(f"Cannot locate interaction principles placeholder: {old}")
    return updated


def connect_design_language_spec(html: str) -> str:
    updated = html
    updated = updated.replace(
        "doc:'soc-interaction-principles'",
        "doc:'soc-design-language'",
    )
    updated = updated.replace(
        "id:'soc-interaction-principles'",
        "id:'soc-design-language'",
    )
    updated = updated.replace(
        "'soc-interaction-principles'",
        "'soc-design-language'",
    )
    updated = updated.replace(
        "'通用交互设计原则'",
        "'通用设计原则'",
    )
    updated = updated.replace(
        "title:'通用交互设计原则'",
        "title:'通用设计原则'",
    )
    updated = updated.replace(
        "基于 Ant Design 设计语言内化的 SOC 通用交互原则：上下文、邀请、反馈、状态、文案、导航、动效和组件沉淀。",
        DESIGN_LANGUAGE_SUMMARY,
    )
    updated = ensure_design_language_rules_area_entry(updated)
    updated = ensure_design_language_home_quick_entry(updated)
    return ensure_design_language_top_nav_entry(updated)


def export_source(html_path: Path = DEFAULT_HTML, source_path: Path = DEFAULT_SOURCE) -> None:
    docs = sanitize_knowledge_docs(extract_knowledge_docs(html_path.read_text(encoding="utf-8")))
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_source(html_path: Path = DEFAULT_HTML, source_path: Path = DEFAULT_SOURCE) -> None:
    html = html_path.read_text(encoding="utf-8")
    docs = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(docs, list):
        raise ValueError(f"{source_path} must contain a JSON list")
    docs = sanitize_knowledge_docs(docs)
    source_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(inject_knowledge_docs(html, docs), encoding="utf-8")


def connect_multilingual_source(
    html_path: Path = DEFAULT_HTML,
    source_path: Path = DEFAULT_SOURCE,
    ref_path: Path = DEFAULT_MULTILINGUAL_REF,
) -> None:
    entry = build_markdown_doc_entry(
        doc_id="multilingual-spec",
        title="多语言与本地化设计规范",
        file_label="references/multilingual-spec.md",
        summary="SOC 多语言、本地化、伪本地化、术语一致性、文本适配和地区资源替换规范。",
        source_path=ref_path,
    )
    docs = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(docs, list):
        raise ValueError(f"{source_path} must contain a JSON list")
    docs = sanitize_knowledge_docs(docs)
    docs = upsert_knowledge_doc(docs, entry)
    source_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    html = html_path.read_text(encoding="utf-8")
    html = inject_knowledge_docs(html, docs)
    html = connect_multilingual_spec(html)
    html_path.write_text(html, encoding="utf-8")


def connect_interaction_principles_source(
    html_path: Path = DEFAULT_HTML,
    source_path: Path = DEFAULT_SOURCE,
    ref_path: Path = DEFAULT_INTERACTION_PRINCIPLES_REF,
) -> None:
    entry = build_markdown_doc_entry(
        doc_id="soc-interaction-principles",
        title="SOC 通用交互设计原则",
        file_label="references/soc-interaction-design-principles.md",
        summary="基于 Ant Design 设计语言内化的 SOC 通用交互原则，覆盖上下文、邀请、反馈、状态、文案、导航、动效和组件沉淀。",
        source_path=ref_path,
    )
    docs = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(docs, list):
        raise ValueError(f"{source_path} must contain a JSON list")
    docs = sanitize_knowledge_docs(docs)
    docs = upsert_knowledge_doc(docs, entry)
    source_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    html = html_path.read_text(encoding="utf-8")
    html = inject_knowledge_docs(html, docs)
    html = connect_interaction_principles_spec(html)
    html_path.write_text(html, encoding="utf-8")


def connect_design_language_source(
    html_path: Path = DEFAULT_HTML,
    source_path: Path = DEFAULT_SOURCE,
    ref_dir: Path = DEFAULT_DESIGN_LANGUAGE_REF,
) -> None:
    collection = build_soc_design_language_collection(ref_dir)
    docs = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(docs, list):
        raise ValueError(f"{source_path} must contain a JSON list")
    docs = sanitize_knowledge_docs(docs)
    docs = upsert_design_language_collection(docs, collection)
    source_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    html = html_path.read_text(encoding="utf-8")
    html = inject_knowledge_docs(html, docs)
    html = connect_design_language_spec(html)
    html_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync SOC UXD embedded KNOWLEDGE_DOCS with a local JSON source."
    )
    parser.add_argument(
        "mode",
        choices=(
            "export",
            "import",
            "connect-multilingual",
            "connect-principles",
            "connect-design-language",
        ),
    )
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()

    if args.mode == "export":
        export_source(args.html, args.source)
        print(f"exported KNOWLEDGE_DOCS to {args.source}")
    elif args.mode == "import":
        import_source(args.html, args.source)
        print(f"imported KNOWLEDGE_DOCS into {args.html}")
    elif args.mode == "connect-multilingual":
        connect_multilingual_source(args.html, args.source)
        print(f"connected multilingual spec into {args.html}")
    elif args.mode == "connect-principles":
        connect_interaction_principles_source(args.html, args.source)
        print(f"connected interaction principles into {args.html}")
    else:
        connect_design_language_source(args.html, args.source)
        print(f"connected SOC design language collection into {args.html}")


if __name__ == "__main__":
    main()
