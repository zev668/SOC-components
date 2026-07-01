from __future__ import annotations

import base64
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_ID = "soc-figma-visual-inventory"


def main() -> None:
    index = ROOT / "index.html"
    source = ROOT / "SOC UXD Figma全量界面视觉资产库.md"
    text = index.read_text(encoding="utf-8")
    content = source.read_text(encoding="utf-8")

    entry = {
        "id": DOC_ID,
        "title": "Figma 全量视觉资产库",
        "file": source.name,
        "summary": "从 B2 新风格迭代 GUI 效果图汇总中抽取的系统级视觉资产索引，覆盖主效果图页与商业化资源页。",
        "lines": len(content.splitlines()),
        "contentB64": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }

    match = re.search(r"const KNOWLEDGE_DOCS = (\[.*?\]);\nlet currentKnowledgeDocId", text, re.S)
    if not match:
        raise RuntimeError("Cannot locate KNOWLEDGE_DOCS block")
    docs = json.loads(match.group(1))
    docs = [doc for doc in docs if doc.get("id") != DOC_ID]
    docs.append(entry)
    text = text[: match.start(1)] + json.dumps(docs, ensure_ascii=False) + text[match.end(1) :]

    item = (
        "{kind:'doc',doc:'soc-figma-visual-inventory',title:'Figma 全量视觉资产库',"
        "status:'ready',desc:'从 B2 全量 GUI 效果图读取出的系统级视觉资产地图，包含主效果图和商业化资源页的候选界面、资产组与双端倾向。'},"
    )
    if "doc:'soc-figma-visual-inventory'" not in text:
        target = (
            "{kind:'doc',doc:'soc-interface-inventory',title:'全量界面资产库',status:'ready',"
            "desc:'从两个 Excel 提取系统、界面、界面过程名称、负责人、PC 定制等级和 RLS 跑测问题索引。'},"
        )
        if target not in text:
            raise RuntimeError("Cannot locate assets area insertion point")
        text = text.replace(target, target + "\n      " + item, 1)

    index.write_text(text, encoding="utf-8")
    print(f"updated {index.name}: added {DOC_ID} ({entry['lines']} lines)")


if __name__ == "__main__":
    main()
