from __future__ import annotations

import base64
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT.parent / ".codex" / "skills" / "game-interaction-design" / "references" / "interface-layering-spec.md"
DOC_ID = "interface-layering-spec"


def main() -> None:
    index = ROOT / "index.html"
    text = index.read_text(encoding="utf-8")
    content = REF.read_text(encoding="utf-8")

    entry = {
        "id": DOC_ID,
        "title": "界面层级规范",
        "file": "references/interface-layering-spec.md",
        "summary": "从层级规范图、层级原则图和 08_界面表提炼出的页面层、弹层、HUD、Loading、Notice、水印与堆栈配置规则。",
        "lines": len(content.splitlines()),
        "contentB64": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }

    match = re.search(r"const KNOWLEDGE_DOCS = (\[.*?\]);\nlet currentKnowledgeDocId", text, re.S)
    if not match:
        raise RuntimeError("Cannot locate KNOWLEDGE_DOCS block")
    docs = json.loads(match.group(1))
    docs = [doc for doc in docs if doc.get("id") != DOC_ID]
    insert_at = next((i + 1 for i, doc in enumerate(docs) if doc.get("id") == "typography-color-spec"), len(docs))
    docs.insert(insert_at, entry)
    text = text[: match.start(1)] + json.dumps(docs, ensure_ascii=False) + text[match.end(1) :]

    doc_item = "{kind:'doc',doc:'interface-layering-spec',title:'界面层级规范',status:'ready',desc:'页面层、弹层、系统提示、HUD、Loading、全局层的运行层级与堆栈规则。'}"
    text = re.sub(
        r"\{title:'界面层级规范',status:'todo',desc:'[^']*?'\}",
        doc_item,
        text,
    )

    if "id:'interface-layering-spec'" not in text:
        anchor = "{action:'doc',id:'typography-color-spec',title:'字号字色规范',desc:'B2 风格里的文字层级和颜色依据。'},"
        addition = "\n    {action:'doc',id:'interface-layering-spec',title:'界面层级规范',desc:'页面层、弹层、HUD、Loading 和全局层的堆栈规则。'},"
        if anchor not in text:
            raise RuntimeError("Cannot locate top-nav insertion point")
        text = text.replace(anchor, anchor + addition, 1)

    text = text.replace(
        "desc:'界面框架、双端转译、字号字色、节点命名都归在这里。'",
        "desc:'界面框架、双端转译、字号字色、界面层级、节点命名都归在这里。'",
    )
    text = text.replace(
        "desc:'回答“这个界面应该遵守哪些底层规则”，包含框架、字号字色、层级、提示、多语言和通用原则。'",
        "desc:'回答“这个界面应该遵守哪些底层规则”，包含框架、字号字色、界面层级、提示、多语言和通用原则。'",
    )

    index.write_text(text, encoding="utf-8")
    print(f"updated {index} with {DOC_ID}: {entry['lines']} lines")


if __name__ == "__main__":
    main()
