from __future__ import annotations

import argparse
import base64
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "soc-uxd"
DEFAULT_KNOWLEDGE_DOCS = DATA_ROOT / "knowledge-docs.json"
DEFAULT_MANIFEST = DATA_ROOT / "manifest.json"
DEFAULT_OUTPUT = DATA_ROOT / "SOC-UXD-知识库当前盘点.md"


AREA_BY_DOC_ID = {
    "skill": "设计流程",
    "contracts": "设计流程",
    "checklists": "设计流程",
    "interaction-document-template": "设计流程",
    "fullscreen-framework-translation": "规范规则",
    "typography-color-spec": "规范规则",
    "interface-layering-spec": "规范规则",
    "figma-node-naming-spec": "规范规则",
    "prompt-system": "规范规则",
    "multilingual-spec": "规范规则",
    "soc-design-language": "规范规则",
    "soc-common-components-catalog": "资产参考",
    "soc-interface-inventory": "资产参考",
    "soc-figma-visual-inventory": "资产参考",
    "corpus-notes": "资产参考",
    "figma-patterns": "交付落地",
    "ai-figma-fgui": "交付落地",
}


GAP_NOTES = [
    ("设计流程", "缺少真实项目复盘库：每个专题从策划输入到交互稿再到上线反馈的闭环案例。"),
    ("规范规则", "颜色字体、界面层级、提示系统已有规则页，但仍缺少更多正反例截图和边界判断样例。"),
    ("规范规则", "多语言规范已经入库，后续需要把术语确认结果、地区资源替换清单和伪本地化跑测结论持续补齐。"),
    ("资产参考", "Excel 大表目前为目录级解析，适合发现和检索；重点 sheet 后续需要拆成更细的 md/jsonl。"),
    ("资产参考", "通用组件资产库已有入口，但每个组件的可复用边界、状态矩阵和反例还需要继续补图。"),
    ("交付落地", "Figma 到 FGUI 工作流已有长文档，后续要补更多失败案例、校验规则和常见报错处理。"),
    ("问答助手", "助手能读取网页内置规范和资料库 chunks；如要更准确，需要继续把原始文档批量转成检索片段。"),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def decode_b64(value: str | None) -> str:
    if not value:
        return ""
    try:
        return base64.b64decode(value.encode("ascii")).decode("utf-8")
    except Exception:
        return ""


def compact(value: str, max_chars: int = 120) -> str:
    value = " ".join(str(value or "").split())
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1].rstrip("，。、；;,. ") + "..."


def md_link(label: str, path: str | None) -> str:
    if not path:
        return ""
    return f"[{label}]({path})"


def knowledge_doc_rows(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in docs:
        if doc.get("kind") == "collection":
            pages = doc.get("pages") or []
            rows.append(
                {
                    "id": doc.get("id", ""),
                    "title": doc.get("title", ""),
                    "area": AREA_BY_DOC_ID.get(doc.get("id", ""), "待分类"),
                    "type": f"collection / {len(pages)} 页",
                    "aiSource": doc.get("file", ""),
                    "webSource": doc.get("combinedHtmlFile", ""),
                    "lines": int(doc.get("lines") or 0),
                    "summary": compact(doc.get("summary", "")),
                }
            )
            continue
        web_content = decode_b64(doc.get("webContentB64"))
        rows.append(
            {
                "id": doc.get("id", ""),
                "title": doc.get("title", ""),
                "area": AREA_BY_DOC_ID.get(doc.get("id", ""), "待分类"),
                "type": "single-page",
                "aiSource": doc.get("file", ""),
                "webSource": doc.get("webFile", ""),
                "lines": int(doc.get("lines") or 0),
                "summary": compact(doc.get("summary", "") or web_content),
            }
        )
    return rows


def manifest_doc_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in manifest.get("documents", []):
        topics = doc.get("topics") if isinstance(doc.get("topics"), list) else []
        area = next((topic for topic in topics if topic in {"多语言规范", "信息提示系统", "组件复用规范", "Figma 到 FGUI 工作流", "历史界面资产库", "项目专项案例库"}), "")
        rows.append(
            {
                "id": doc.get("docId", ""),
                "title": doc.get("title", ""),
                "area": area or "资料库",
                "sourceType": doc.get("sourceType", ""),
                "status": doc.get("publishStatus", ""),
                "sourceFile": doc.get("sourceFile", ""),
                "documentPath": doc.get("documentPath", ""),
                "chunkPath": doc.get("chunkPath", ""),
                "chunkCount": int(doc.get("chunkCount") or 0),
                "summary": compact(doc.get("summary", "")),
            }
        )
    return rows


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ").replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def build_inventory_markdown(
    *,
    knowledge_docs_path: Path = DEFAULT_KNOWLEDGE_DOCS,
    manifest_path: Path = DEFAULT_MANIFEST,
    generated_at: str | None = None,
) -> str:
    generated_at = generated_at or datetime.now().astimezone().isoformat(timespec="seconds")
    knowledge_docs = load_json(knowledge_docs_path)
    manifest = load_json(manifest_path)
    knowledge_rows = knowledge_doc_rows(knowledge_docs)
    source_rows = manifest_doc_rows(manifest)

    area_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in knowledge_rows:
        area_groups[row["area"]].append(row)

    source_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        source_groups[row["area"]].append(row)

    total_chunks = sum(row["chunkCount"] for row in source_rows)
    converted_sources = sum(1 for row in source_rows if row["status"] == "converted")
    lines: list[str] = [
        "# SOC UXD 知识库当前盘点",
        "",
        f"- 更新时间：{generated_at}",
        "- 盘点口径：网页文档给项目成员阅读；AI 检索文档和 JSONL chunk 给问答助手检索。",
        "- 原始大文件默认保留在本机；GitHub Pages 发布转换后的 md、json、jsonl 和轻量资源。",
        "",
        "## 总览",
        "",
        table(
            ["类别", "数量", "说明"],
            [
                ["可读网页文档", str(len(knowledge_rows)), "网站中可直接阅读的规范、流程、资产和集合页。"],
                ["原始资料入库条目", str(len(source_rows)), "已登记并转换为 AI 检索材料的本地来源资料。"],
                ["已转检索文档", str(converted_sources), "已生成 documents/*.md 与 chunks/*.jsonl。"],
                ["检索片段", str(total_chunks), "问答助手会加载这些片段作为回答依据。"],
            ],
        ),
        "",
        "## 已沉淀的可读网页文档",
        "",
    ]

    for area in ["设计流程", "规范规则", "资产参考", "交付落地", "待分类"]:
        rows = area_groups.get(area, [])
        if not rows:
            continue
        lines.extend(
            [
                f"### {area}",
                "",
                table(
                    ["文档", "网页稿", "AI 约束源", "行数", "摘要"],
                    [
                        [
                            row["title"],
                            md_link("网页稿", row["webSource"]) if row["webSource"] else "",
                            row["aiSource"],
                            str(row["lines"]),
                            row["summary"],
                        ]
                        for row in rows
                    ],
                ),
                "",
            ]
        )

    lines.extend(["## 已入库的原始资料 / AI 检索文档", ""])
    for area, rows in sorted(source_groups.items()):
        lines.extend(
            [
                f"### {area}",
                "",
                table(
                    ["资料", "来源", "类型", "状态", "转换 MD", "片段", "摘要"],
                    [
                        [
                            row["title"],
                            row["sourceFile"],
                            row["sourceType"],
                            row["status"],
                            md_link("打开", row["documentPath"]),
                            str(row["chunkCount"]),
                            row["summary"],
                        ]
                        for row in rows
                    ],
                ),
                "",
            ]
        )

    lines.extend(
        [
            "## 当前缺口和下一步补充方向",
            "",
            table(["模块", "缺口 / 建议"], [[area, note] for area, note in GAP_NOTES]),
            "",
            "## 存放位置",
            "",
            table(
                ["内容", "路径"],
                [
                    ["网页可读文档", "data/soc-uxd/web-docs/*.page.md"],
                    ["AI 检索 Markdown", "data/soc-uxd/documents/*.md"],
                    ["AI 检索 chunk", "data/soc-uxd/chunks/*.jsonl"],
                    ["资料库索引", "data/soc-uxd/manifest.json"],
                    ["网页内置知识文档索引", "data/soc-uxd/knowledge-docs.json"],
                    ["入库流程 Skill", "../.codex/skills/soc-uxd-document-ingest/SKILL.md"],
                ],
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_inventory(output_path: Path = DEFAULT_OUTPUT) -> str:
    markdown = build_inventory_markdown()
    output_path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return markdown


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a readable SOC UXD knowledge inventory.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    write_inventory(args.output)
    print(f"wrote SOC UXD inventory to {args.output}")


if __name__ == "__main__":
    main()
