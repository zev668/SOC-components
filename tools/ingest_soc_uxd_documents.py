from __future__ import annotations

import argparse
import json
import re
import zipfile

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET

try:
    from tools.build_soc_uxd_inventory import DEFAULT_OUTPUT as INVENTORY_OUTPUT
    from tools.build_soc_uxd_inventory import write_inventory
except ModuleNotFoundError:
    from build_soc_uxd_inventory import DEFAULT_OUTPUT as INVENTORY_OUTPUT
    from build_soc_uxd_inventory import write_inventory


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DEFAULT_OUTPUT_ROOT = ROOT / "data" / "soc-uxd"


LOCAL_SOURCE_SPECS = [
    {
        "doc_id": "localization-consensus",
        "title": "本地化设计共识与落地规范",
        "path": WORKSPACE_ROOT / "本地化设计共识与落地规范.md",
        "topics": ["多语言规范", "本地化", "合规风险", "文本适配"],
    },
    {
        "doc_id": "pseudo-localization-requirements",
        "title": "伪本地化需求文档",
        "path": WORKSPACE_ROOT / "伪本地化需求文档.md",
        "topics": ["多语言规范", "伪本地化", "测试流程"],
    },
    {
        "doc_id": "survival-manual-image-text-localization",
        "title": "生存手册配图文本多语言适配规范",
        "path": WORKSPACE_ROOT / "【生存手册】配图文本多语言适配规范.md",
        "topics": ["多语言规范", "配图文本", "生存手册"],
    },
    {
        "doc_id": "prompt-system-source-notes",
        "title": "提示系统整理",
        "path": WORKSPACE_ROOT / "提示系统整理.md",
        "topics": ["信息提示系统", "提示队列", "配置表"],
    },
    {
        "doc_id": "food-spoilage-interaction-draft",
        "title": "食物腐败交互设计文档草稿",
        "path": WORKSPACE_ROOT / "食物腐败-交互设计文档草稿.md",
        "topics": ["项目专项案例库", "容器系统", "物品状态", "食物腐败"],
    },
    {
        "doc_id": "pet-system-planning-source",
        "title": "宠物系统策划设计文档",
        "path": WORKSPACE_ROOT / "宠物系统策划设计文档.md",
        "topics": ["项目专项案例库", "策划输入", "宠物系统"],
    },
    {
        "doc_id": "figma-fgui-workflow-source",
        "title": "Figma 转 FGUI 工作流整合说明",
        "path": WORKSPACE_ROOT / "Figma转FGUI工作流整合说明.md",
        "topics": ["Figma 到 FGUI 工作流", "交付落地"],
    },
    {
        "doc_id": "figma-fgui-property-mapping",
        "title": "Figma 到 FGUI 属性映射",
        "path": WORKSPACE_ROOT / "figma-fgui-property-mapping.md",
        "topics": ["Figma 到 FGUI 工作流", "属性映射"],
    },
    {
        "doc_id": "soc-terms-tw-en-pending",
        "title": "SOC 术语表台英待确认",
        "path": WORKSPACE_ROOT / "SOC-术语表-台英待确认.xlsx",
        "topics": ["多语言规范", "术语表", "待确认"],
    },
    {
        "doc_id": "soc-common-component-source-workbook",
        "title": "SOC 通用组件清单原始表",
        "path": WORKSPACE_ROOT / "SOC通用组件清单（已整理至B2下）.xlsx",
        "topics": ["组件复用规范", "通用组件资产库"],
    },
    {
        "doc_id": "soc-interface-inventory-source-workbook",
        "title": "SOC 项目全量界面整理原始表",
        "path": WORKSPACE_ROOT / "SOC项目全量界面整理.xlsx",
        "topics": ["历史界面资产库", "全量界面资产"],
    },
    {
        "doc_id": "rls-interface-run-test-source-workbook",
        "title": "RLS 全量界面跑测表原始表",
        "path": WORKSPACE_ROOT / "_RLS-全量界面跑测表.xlsx",
        "topics": ["历史界面资产库", "跑测问题", "RLS"],
    },
]


@dataclass(frozen=True)
class SourceSpec:
    doc_id: str
    title: str
    path: Path
    topics: list[str]
    extract: bool = True

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SourceSpec":
        return cls(
            doc_id=str(data["doc_id"]),
            title=str(data["title"]),
            path=Path(data["path"]),
            topics=list(data.get("topics", [])),
            extract=bool(data.get("extract", True)),
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def path_for_manifest(path: Path, source_root: Path) -> str:
    try:
        return path.resolve().relative_to(source_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def source_type(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    return suffix or "file"


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def strip_markdown_images_for_summary(text: str) -> str:
    return re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)


def markdown_plain_lines(markdown: str) -> list[str]:
    lines: list[str] = []
    in_code = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith("|") or stripped.startswith("---"):
            continue
        stripped = re.sub(r"^#{1,6}\s*", "", stripped)
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        stripped = re.sub(r"^\d+[.)]\s+", "", stripped)
        stripped = strip_markdown_images_for_summary(stripped)
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        stripped = re.sub(r"[*_`>]+", "", stripped).strip()
        if stripped:
            lines.append(stripped)
    return lines


def first_paragraph(markdown: str, max_chars: int = 160) -> str:
    text = " ".join(markdown_plain_lines(markdown))
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "该资料已登记，等待进一步解析。"
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip("，。、；;,. ") + "..."
    return text


def extract_headings(markdown: str) -> list[str]:
    headings: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            heading = re.sub(r"\s+", " ", match.group(2)).strip()
            if heading:
                headings.append(heading)
    return headings


def extract_explicit_rules(markdown: str, max_items: int = 12) -> list[str]:
    candidates: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("![]("):
            continue
        if any(keyword in stripped for keyword in ("必须", "不要", "避免", "需要", "建议", "禁止", "应", "不能", "确保")):
            stripped = re.sub(r"^[-*+]\s+", "", stripped)
            stripped = re.sub(r"\s+", " ", stripped).strip()
            if len(stripped) > 8 and stripped not in candidates:
                candidates.append(stripped)
        if len(candidates) >= max_items:
            break
    return candidates


def extract_uncertain_items(markdown: str, max_items: int = 8) -> list[str]:
    items: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if any(keyword in stripped for keyword in ("待确认", "后续", "暂未", "目前无", "需要确认", "待补充", "计划")):
            stripped = re.sub(r"^[-*+]\s+", "", stripped)
            stripped = re.sub(r"\s+", " ", stripped).strip()
            if len(stripped) > 5 and stripped not in items:
                items.append(stripped)
        if len(items) >= max_items:
            break
    return items


def frontmatter_value(value: str | list[str]) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(json.dumps(item, ensure_ascii=False) for item in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", ns):
        text = "".join(node.text or "" for node in para.findall(".//w:t", ns)).strip()
        if text:
            paragraphs.append(text)
    return "# " + path.stem + "\n\n" + "\n\n".join(paragraphs)


def read_html_text(path: Path) -> str:
    html = path.read_text(encoding="utf-8", errors="ignore")
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"</(h[1-6]|p|li|tr)>", "\n", html, flags=re.I)
    html = re.sub(r"<h([1-6])[^>]*>", lambda m: "\n" + "#" * int(m.group(1)) + " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"\n\s+\n", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return clean_text(text)


def read_xlsx_preview(path: Path, row_limit: int = 80) -> str:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            for si in shared_root.findall(".//x:si", ns):
                shared_strings.append("".join(t.text or "" for t in si.findall(".//x:t", ns)))
        sheet_names = sorted(name for name in archive.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", name))
        rows: list[str] = [f"# {path.stem}", "", "> 这是 Excel 预览抽取；大表建议后续按 sheet 分批解析。"]
        ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        for sheet_name in sheet_names[:3]:
            root = ET.fromstring(archive.read(sheet_name))
            rows.append("")
            rows.append(f"## {sheet_name}")
            count = 0
            for row in root.findall(".//x:row", ns):
                values: list[str] = []
                for cell in row.findall("x:c", ns):
                    cell_type = cell.attrib.get("t")
                    value_node = cell.find("x:v", ns)
                    if value_node is None or value_node.text is None:
                        continue
                    value = value_node.text
                    if cell_type == "s":
                        try:
                            value = shared_strings[int(value)]
                        except (IndexError, ValueError):
                            pass
                    values.append(value)
                if values:
                    rows.append(" | ".join(values))
                    count += 1
                if count >= row_limit:
                    rows.append("...")
                    break
        return "\n".join(rows)


def xml_text(node: ET.Element, namespaces: dict[str, str]) -> str:
    return "".join(text_node.text or "" for text_node in node.findall(".//x:t", namespaces))


def read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [xml_text(si, ns) for si in root.findall(".//x:si", ns)]


def workbook_sheet_targets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    ns = {
        "x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    }
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships: dict[str, str] = {}
    if "xl/_rels/workbook.xml.rels" in archive.namelist():
        rel_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        for rel in rel_root.findall(".//pr:Relationship", ns):
            rel_id = rel.attrib.get("Id", "")
            target = rel.attrib.get("Target", "")
            if rel_id and target:
                relationships[rel_id] = target
    sheets: list[tuple[str, str]] = []
    for sheet in workbook.findall(".//x:sheet", ns):
        name = sheet.attrib.get("name", "未命名 Sheet")
        rel_id = sheet.attrib.get(f"{{{ns['r']}}}id", "")
        target = relationships.get(rel_id, "")
        if target:
            if target.startswith("/"):
                target_path = target.lstrip("/")
            elif target.startswith("xl/"):
                target_path = target
            else:
                target_path = "xl/" + target
            sheets.append((name, target_path))
    if sheets:
        return sheets
    fallback = sorted(name for name in archive.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", name))
    return [(Path(name).stem, name) for name in fallback]


def cell_value(cell: ET.Element, shared_strings: list[str], namespaces: dict[str, str]) -> str:
    cell_type = cell.attrib.get("t")
    inline_text = cell.find("x:is", namespaces)
    if inline_text is not None:
        return xml_text(inline_text, namespaces).strip()
    value_node = cell.find("x:v", namespaces)
    if value_node is None or value_node.text is None:
        return ""
    value = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(value)].strip()
        except (IndexError, ValueError):
            return value.strip()
    return value.strip()


def column_letters_to_number(value: str) -> int:
    total = 0
    for char in value.upper():
        if not ("A" <= char <= "Z"):
            continue
        total = total * 26 + ord(char) - ord("A") + 1
    return total


def column_number_to_letters(value: int) -> str:
    if value <= 0:
        return "A"
    letters: list[str] = []
    while value:
        value, remainder = divmod(value - 1, 26)
        letters.append(chr(ord("A") + remainder))
    return "".join(reversed(letters))


def sampled_dimension(cell_refs: Iterable[str]) -> str:
    max_col = 0
    max_row = 0
    for ref in cell_refs:
        match = re.match(r"([A-Z]+)(\d+)", ref.upper())
        if not match:
            continue
        max_col = max(max_col, column_letters_to_number(match.group(1)))
        max_row = max(max_row, int(match.group(2)))
    if max_col <= 1 and max_row <= 1:
        return ""
    return f"A1:{column_number_to_letters(max_col)}{max_row}（采样推断）"


def read_xlsx_catalog(path: Path, *, sample_rows: int = 5, max_sheets: int = 30) -> str:
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        shared_strings = read_shared_strings(archive)
        sheets = workbook_sheet_targets(archive)
        lines = [
            f"# {path.stem}",
            "",
            "> 这是 Excel 目录级解析：保留工作簿结构、sheet 名、维度、表头和样例行；不把整张大表直接塞进网页。",
            "",
            f"- Sheet 数量：{len(sheets)}",
            f"- 文件大小：{path.stat().st_size / (1024 * 1024):.1f} MB",
        ]
        for index, (sheet_name, target_path) in enumerate(sheets[:max_sheets], start=1):
            if target_path not in archive.namelist():
                continue
            root = ET.fromstring(archive.read(target_path))
            dimension = root.find("x:dimension", ns)
            dimension_ref = dimension.attrib.get("ref", "") if dimension is not None else ""
            sampled_rows: list[list[str]] = []
            sampled_cell_refs: list[str] = []
            for row in root.findall(".//x:sheetData/x:row", ns):
                cells = row.findall("x:c", ns)
                sampled_cell_refs.extend(cell.attrib.get("r", "") for cell in cells)
                values = [cell_value(cell, shared_strings, ns) for cell in cells]
                values = [value for value in values if value]
                if values:
                    sampled_rows.append(values)
                if len(sampled_rows) >= sample_rows + 1:
                    break
            if dimension_ref in {"", "A1"}:
                dimension_ref = sampled_dimension(sampled_cell_refs) or dimension_ref
            header = sampled_rows[0] if sampled_rows else []
            body_rows = sampled_rows[1:]
            lines.extend(
                [
                    "",
                    f"## Sheet: {sheet_name}",
                    "",
                    f"- 顺序：{index}",
                    f"- XML：{target_path}",
                    f"- 维度：{dimension_ref or '未声明'}",
                    f"- 表头：{' | '.join(header) if header else '未识别'}",
                ]
            )
            if body_rows:
                lines.append("")
                lines.append("| " + " | ".join(header or [f"列 {i+1}" for i in range(max(len(row) for row in body_rows))]) + " |")
                lines.append("| " + " | ".join("---" for _ in (header or body_rows[0])) + " |")
                for row in body_rows:
                    width = len(header) if header else len(row)
                    padded = row + [""] * max(0, width - len(row))
                    lines.append("| " + " | ".join(padded[:width]) + " |")
        if len(sheets) > max_sheets:
            lines.extend(["", f"## 未展开 Sheet", "", f"- 还有 {len(sheets) - max_sheets} 个 sheet 未在本轮目录级解析中展开。"])
        return "\n".join(lines)


def read_source_text(spec: SourceSpec) -> tuple[str, str]:
    path = spec.path
    if not path.exists():
        return f"# {spec.title}\n\n> 原始文件未找到，已仅登记来源路径。", "missing"
    if not spec.extract:
        size_mb = path.stat().st_size / (1024 * 1024)
        return (
            f"# {spec.title}\n\n"
            f"> 原始文件已登记，当前为 local-only。文件约 {size_mb:.1f} MB，未直接纳入 GitHub Pages。"
            "\n\n## 待处理\n\n- 后续按 sheet / 表格区域分批抽取为可检索 md 与 jsonl。\n",
            "registered",
        )
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return clean_text(path.read_text(encoding="utf-8", errors="ignore")), "converted"
    if suffix in {".html", ".htm"}:
        return read_html_text(path), "converted"
    if suffix == ".docx":
        return read_docx_text(path), "converted"
    if suffix == ".xlsx":
        return read_xlsx_catalog(path), "converted"
    return f"# {spec.title}\n\n> 暂不支持自动解析该文件类型，已登记来源。", "registered"


def build_retrieval_markdown(
    spec: SourceSpec,
    source_text: str,
    *,
    source_root: Path,
    publish_status: str,
    generated_at: str,
) -> str:
    path = spec.path
    headings = extract_headings(source_text)
    explicit_rules = extract_explicit_rules(source_text)
    uncertain = extract_uncertain_items(source_text)
    summary = first_paragraph(source_text)
    frontmatter = {
        "docId": spec.doc_id,
        "title": spec.title,
        "sourceFile": path_for_manifest(path, source_root),
        "sourceType": source_type(path),
        "publishStatus": publish_status,
        "ingestMode": "archival",
        "updatedAt": generated_at[:10],
        "topics": spec.topics,
    }
    fm = "\n".join(f"{key}: {frontmatter_value(value)}" for key, value in frontmatter.items())
    rules_md = "\n".join(f"- {item}" for item in explicit_rules) or "- 原文未明确提取到强规则；暂按资料归档处理。"
    uncertain_md = "\n".join(f"- {item}" for item in uncertain) or "- 暂无。"
    headings_md = "\n".join(f"- {item}" for item in headings[:40]) or "- 原文未使用显式标题结构。"
    keywords = sorted(set(spec.topics + [spec.title] + headings[:8]))
    keywords_md = "、".join(keywords)
    return (
        f"---\n{fm}\n---\n\n"
        f"# {spec.title}\n\n"
        "## 文档身份\n"
        f"- 原始文件：{path_for_manifest(path, source_root)}\n"
        f"- 文档类型：{source_type(path)}\n"
        f"- 所属模块：{'、'.join(spec.topics) if spec.topics else '待分类'}\n"
        f"- 状态：{publish_status}\n"
        "- 入库模式：资料归档优先\n\n"
        "## 资料摘要\n\n"
        f"{summary}\n\n"
        "## 原文结构转写\n\n"
        f"{headings_md}\n\n"
        "## 明确规则 / 决策\n\n"
        f"{rules_md}\n\n"
        "## 案例经验\n\n"
        "以下保留原文主体，供 AI 检索和人工回溯。\n\n"
        "## 待确认 / AI 推论\n\n"
        f"{uncertain_md}\n\n"
        "## 检索关键词\n\n"
        f"{keywords_md}\n\n"
        "## 来源定位\n\n"
        f"- 文件：{path_for_manifest(path, source_root)}\n"
        "- 位置：按原文标题和段落回溯。\n\n"
        "---\n\n"
        "## 原文主体\n\n"
        f"{source_text.strip()}\n"
    )


def split_markdown_sections(markdown: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "文档概览"
    current_lines: list[str] = []
    in_frontmatter = False
    for index, line in enumerate(markdown.splitlines()):
        if index == 0 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if match:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = match.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_title, current_lines))
    return [(title, "\n".join(lines).strip()) for title, lines in sections if "\n".join(lines).strip()]


def chunk_text(text: str, size: int = 950, overlap: int = 120) -> list[str]:
    normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not normalized:
        return []
    if len(normalized) <= size:
        return [normalized]
    chunks: list[str] = []
    step = size - overlap
    for start in range(0, len(normalized), step):
        piece = normalized[start : start + size].strip()
        if len(piece) >= 40:
            chunks.append(piece)
        if start + size >= len(normalized):
            break
    return chunks


def build_chunks(spec: SourceSpec, markdown: str, *, source_file: str, status: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for section_title, section_text in split_markdown_sections(markdown):
        source: dict[str, str] = {"file": source_file, "section": section_title}
        if section_title.startswith("Sheet: "):
            source["sheet"] = section_title.replace("Sheet: ", "", 1)
        for piece in chunk_text(section_text):
            rows.append(
                {
                    "docId": spec.doc_id,
                    "chunkId": f"{spec.doc_id}#{len(rows) + 1}",
                    "title": f"{spec.title} / {section_title}",
                    "source": source,
                    "tags": spec.topics,
                    "text": piece,
                    "status": "archival" if status == "converted" else status,
                }
            )
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_document_library(
    specs: list[SourceSpec],
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    source_root: Path = WORKSPACE_ROOT,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or now_iso()
    documents_dir = output_root / "documents"
    chunks_dir = output_root / "chunks"
    documents_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []

    for spec in specs:
        source_text, publish_status = read_source_text(spec)
        retrieval_markdown = build_retrieval_markdown(
            spec,
            source_text,
            source_root=source_root,
            publish_status=publish_status,
            generated_at=generated_at,
        )
        document_path = documents_dir / f"{spec.doc_id}.md"
        chunk_path = chunks_dir / f"{spec.doc_id}.jsonl"
        document_path.write_text(retrieval_markdown.rstrip() + "\n", encoding="utf-8")
        source_file = path_for_manifest(spec.path, source_root)
        chunks = build_chunks(spec, retrieval_markdown, source_file=source_file, status=publish_status)
        write_jsonl(chunk_path, chunks)
        exists = spec.path.exists()
        size = spec.path.stat().st_size if exists else 0
        entries.append(
            {
                "docId": spec.doc_id,
                "title": spec.title,
                "sourceFile": source_file,
                "sourceType": source_type(spec.path),
                "publishStatus": publish_status,
                "ingestMode": "archival",
                "topics": spec.topics,
                "sizeBytes": size,
                "sourceLastModified": datetime.fromtimestamp(spec.path.stat().st_mtime).astimezone().isoformat(timespec="seconds")
                if exists
                else "",
                "documentPath": f"documents/{spec.doc_id}.md",
                "chunkPath": f"chunks/{spec.doc_id}.jsonl",
                "chunkCount": len(chunks),
                "summary": first_paragraph(source_text),
            }
        )

    manifest = {
        "version": 1,
        "generatedAt": generated_at,
        "mode": "archival",
        "sourceRoot": path_for_manifest(source_root, source_root),
        "documents": entries,
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if output_root == DEFAULT_OUTPUT_ROOT:
        inventory_markdown = write_inventory(INVENTORY_OUTPUT)
        inventory_spec = SourceSpec(
            doc_id="soc-uxd-current-inventory",
            title="SOC UXD 知识库当前盘点",
            path=INVENTORY_OUTPUT,
            topics=["资料库", "知识库盘点", "当前缺口"],
        )
        inventory_chunk_path = chunks_dir / f"{inventory_spec.doc_id}.jsonl"
        inventory_chunks = build_chunks(
            inventory_spec,
            inventory_markdown,
            source_file="data/soc-uxd/SOC-UXD-知识库当前盘点.md",
            status="converted",
        )
        write_jsonl(inventory_chunk_path, inventory_chunks)
        entries.insert(
            0,
            {
                "docId": inventory_spec.doc_id,
                "title": inventory_spec.title,
                "sourceFile": "data/soc-uxd/SOC-UXD-知识库当前盘点.md",
                "sourceType": "md",
                "publishStatus": "converted",
                "ingestMode": "archival",
                "topics": inventory_spec.topics,
                "sizeBytes": INVENTORY_OUTPUT.stat().st_size if INVENTORY_OUTPUT.exists() else 0,
                "sourceLastModified": datetime.fromtimestamp(INVENTORY_OUTPUT.stat().st_mtime).astimezone().isoformat(timespec="seconds")
                if INVENTORY_OUTPUT.exists()
                else "",
                "documentPath": "SOC-UXD-知识库当前盘点.md",
                "chunkPath": f"chunks/{inventory_spec.doc_id}.jsonl",
                "chunkCount": len(inventory_chunks),
                "summary": "汇总当前 SOC UXD 知识库的人读网页文档、AI 检索文档、来源资料、存放位置和缺口建议。",
            },
        )
        manifest = {**manifest, "documents": entries}
        (output_root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return manifest


def default_specs() -> list[SourceSpec]:
    return [SourceSpec.from_mapping(item) for item in LOCAL_SOURCE_SPECS]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SOC UXD document-center markdown, chunks, and manifest.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--source-root", type=Path, default=WORKSPACE_ROOT)
    args = parser.parse_args()
    manifest = build_document_library(default_specs(), output_root=args.output_root, source_root=args.source_root)
    print(
        f"ingested {len(manifest['documents'])} source documents into {args.output_root}"
    )


if __name__ == "__main__":
    main()
