from __future__ import annotations

import base64
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    source = next(ROOT.glob("SOC UXD *界面资产库.md"))
    content = source.read_text(encoding="utf-8")
    entry = {
        "id": "soc-interface-inventory",
        "title": "全量界面资产库",
        "file": source.name,
        "summary": "从 SOC 项目全量界面整理与 RLS 全量界面跑测表提取的系统、界面、负责人、PC 定制等级与跑测问题索引。",
        "lines": len(content.splitlines()),
        "contentB64": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }

    match = re.search(r"const KNOWLEDGE_DOCS = (\[.*?\]);\nlet currentKnowledgeDocId", text, re.S)
    if not match:
        raise RuntimeError("Cannot locate KNOWLEDGE_DOCS")
    docs = json.loads(match.group(1))
    docs = [doc for doc in docs if doc.get("id") != entry["id"]]
    docs.append(entry)
    text = text[: match.start(1)] + json.dumps(docs, ensure_ascii=False) + text[match.end(1) :]

    replacements = {
        "{title:'现存界面结构与跳转逻辑',status:'building',desc:'待把战局、好友、组队、制造、容器、公会等历史界面拆成资产条目。'}":
            "{kind:'doc',doc:'soc-interface-inventory',title:'全量界面资产库',status:'ready',desc:'从两个 Excel 提取系统、界面、界面过程名称、负责人、PC 定制等级和 RLS 跑测问题索引。'}",
        "['现存界面结构与跳转逻辑','assets','building'],":
            "['Figma 结构与跳转逻辑精读','assets','building'],",
        "['通用组件清单','assets','','component-library'],":
            "['全量界面资产库','assets','soc-interface-inventory','doc'],\n    ['通用组件清单','assets','','component-library'],",
    }
    for old, new in replacements.items():
        if old not in text:
            raise RuntimeError(f"Missing replacement target: {old}")
        text = text.replace(old, new, 1)

    index.write_text(text, encoding="utf-8")
    print(f"updated index.html with {entry['lines']} doc lines")


if __name__ == "__main__":
    main()
