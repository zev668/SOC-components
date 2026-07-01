from __future__ import annotations

import base64
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "soc-interface-inventory.csv"
DOC = ROOT / "SOC UXD 全量界面资产库.md"
SKILL_REF = ROOT.parent / ".codex" / "skills" / "game-interaction-design" / "references" / "soc-interface-inventory.md"
INDEX = ROOT / "index.html"
DOC_ID = "soc-interface-inventory"


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def md(value: object) -> str:
    return clean(value).replace("|", "\\|")


def split_notes(*values: str) -> list[str]:
    text = "；".join(clean(v) for v in values if clean(v))
    if not text:
        return []
    parts = re.split(r"[；;。/]+", text)
    return [clean(p) for p in parts if clean(p)][:4]


def top_items(values: list[str], limit: int = 3) -> list[str]:
    items = [clean(v) for v in values if clean(v)]
    if not items:
        return []
    return [name for name, _ in Counter(items).most_common(limit)]


def infer_framework(system: str, interfaces: list[str], domain: str) -> str:
    text = f"{domain} {system} {' '.join(interfaces[:20])}"
    if re.search(r"HUD|hud|主界面", text):
        return "HUD / 局内常驻层"
    if re.search(r"弹窗|浮窗|TIPS|Tips|tips|提示|恭喜|获得|数字键盘", text):
        return "全局弹层 / Tips"
    if re.search(r"容器|背包|仓库|工具柜|研究台|修理|分解|制造|制作|商店|售货机", text):
        return "全屏或半屏容器 / 列表操作界面"
    if re.search(r"商城|充值|抽奖|通行证|特权|皮肤|收藏|活动|赛季|成长", text):
        return "全屏商业化 / 活动展示界面"
    if re.search(r"好友|聊天|组队|公会|社群|邮箱|个人信息|KOL", text):
        return "全屏社交 / 关系列表界面"
    if re.search(r"地图|排行|战局|匹配|结算|任务|剧本|情报|科技|中控台", text):
        return "全屏系统 / 列表与详情界面"
    if re.search(r"新手|创角|服务器|登录|设置|大厅", text):
        return "全屏流程 / 设置界面"
    return "待确认框架"


def infer_states(interfaces: list[str], notes: list[str]) -> str:
    text = " ".join(interfaces + notes)
    states: list[str] = []
    checks = [
        ("默认/常态", r"默认|常态|主界面|首页"),
        ("选中/切换", r"选中|选择|切换|Tab|页签"),
        ("Hover/快捷键", r"hover|Hover|快捷键|ESC|Esc|键位|PC"),
        ("禁用/未开放", r"禁用|置灰|未开放|锁定|不可"),
        ("空态/无数据", r"空|暂无|无可|没有"),
        ("详情/内页", r"详情|内页|二级|规则"),
        ("弹窗/Tips", r"弹窗|tips|Tips|TIPS|提示|浮窗"),
        ("加载/进行中", r"loading|加载|进行中|进度|倒计时"),
        ("异常/不足", r"不足|失败|错误|降级|过期"),
    ]
    for label, pattern in checks:
        if re.search(pattern, text):
            states.append(label)
    return "、".join(states[:5]) if states else "待补状态矩阵"


def infer_flow(system: str, interfaces: list[str]) -> str:
    text = f"{system} {' '.join(interfaces[:20])}"
    if re.search(r"商城|充值|抽奖|通行证|特权|皮肤|收藏|活动|赛季", text):
        return "入口 -> 首页/列表 -> 详情/规则 -> 购买/领取/反馈"
    if re.search(r"好友|聊天|组队|公会|社群|邮箱|个人信息", text):
        return "入口 -> 列表/空态 -> 详情/操作 -> 消息/邀请/反馈"
    if re.search(r"容器|背包|仓库|工具柜|研究台|修理|分解|制造|制作", text):
        return "入口 -> 物品/列表选择 -> 操作确认 -> 结果/提示"
    if re.search(r"地图|排行|任务|剧本|情报|科技|中控台", text):
        return "入口 -> 分类/列表 -> 详情/定位/追踪 -> 返回"
    if re.search(r"战局|匹配|结算|历史", text):
        return "入口 -> 选择/匹配/记录 -> 结果/结算 -> 返回"
    if re.search(r"HUD|提示|弹窗|tips|TIPS", text):
        return "触发条件 -> 展示 -> 操作/自动消失 -> 回到原界面"
    return "待从 Figma/策划流程确认"


def image_slot(platform: str, examples: list[str], pc_info: str = "") -> str:
    names = "、".join(examples[:3])
    if platform == "pc" and not pc_info:
        return "待确认是否需要 PC 图示"
    if names:
        return f"待补图示（样本：{names}）"
    return "待补图示"


def build_rows() -> list[dict[str, str]]:
    with DATA.open(encoding="utf-8-sig", newline="") as f:
        records = list(csv.DictReader(f))

    grouped: dict[tuple[str, str], dict[str, list[str] | str]] = {}
    for record in records:
        domain = clean(record.get("系统大类"))
        system = clean(record.get("系统"))
        if not domain or not system:
            continue
        bucket = grouped.setdefault(
            (domain, system),
            {
                "domain": domain,
                "system": system,
                "interfaces": [],
                "mobile": [],
                "pc": [],
                "pc_info": [],
                "notes": [],
            },
        )
        interface = clean(record.get("界面")) or clean(record.get("界面过程名称")) or clean(record.get("FGUI名称"))
        if interface:
            bucket["interfaces"].append(interface)  # type: ignore[index]
        level = clean(record.get("PC定制等级"))
        method = clean(record.get("PC制作方式"))
        progress = clean(record.get("PC制作进展"))
        if level or method or progress:
            bucket["pc"].append(interface)  # type: ignore[index]
            bucket["pc_info"].append(" / ".join(x for x in [level, method, progress] if x))  # type: ignore[index]
        else:
            bucket["mobile"].append(interface)  # type: ignore[index]
        bucket["notes"].extend(split_notes(record.get("RLS备注", ""), record.get("B2备注", ""), record.get("风格迭代总进展", "")))  # type: ignore[index]

    rows: list[dict[str, str]] = []
    for (domain, system), bucket in sorted(grouped.items()):
        interfaces = top_items(bucket["interfaces"], 8)  # type: ignore[arg-type]
        mobile = top_items(bucket["mobile"], 3) or interfaces[:3]  # type: ignore[arg-type]
        pc = top_items(bucket["pc"], 3)  # type: ignore[arg-type]
        pc_info = top_items(bucket["pc_info"], 2)  # type: ignore[arg-type]
        notes = top_items(bucket["notes"], 4)  # type: ignore[arg-type]
        analysis = (
            f"界面框架：{infer_framework(system, interfaces, domain)}<br>"
            f"界面元素状态分析：{infer_states(interfaces, notes)}<br>"
            f"界面跳转逻辑：{infer_flow(system, interfaces)}"
        )
        if pc_info:
            analysis += f"<br>PC备注：{'；'.join(pc_info)}"
        rows.append(
            {
                "系统大类": domain,
                "系统": system,
                "手游界面图示": image_slot("mobile", mobile),
                "PC界面图示": image_slot("pc", pc, "；".join(pc_info)),
                "界面分析（界面框架、界面元素状态分析、界面跳转逻辑）": analysis,
            }
        )
    return rows


def write_doc(rows: list[dict[str, str]]) -> None:
    lines = [
        "# SOC UXD 全量界面资产库",
        "",
        "本页只保留系统级表单结构。手游/PC 图示列用于后续补充截图、Figma 节点链接或嵌入图；界面分析列固定记录框架、元素状态、跳转逻辑三件事。",
        "",
        "| 系统大类 | 系统 | 手游界面图示 | PC界面图示 | 界面分析（界面框架、界面元素状态分析、界面跳转逻辑） |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {domain} | {system} | {mobile} | {pc} | {analysis} |".format(
                domain=md(row["系统大类"]),
                system=md(row["系统"]),
                mobile=md(row["手游界面图示"]),
                pc=md(row["PC界面图示"]),
                analysis=md(row["界面分析（界面框架、界面元素状态分析、界面跳转逻辑）"]),
            )
        )
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    SKILL_REF.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_index() -> None:
    text = INDEX.read_text(encoding="utf-8")
    content = DOC.read_text(encoding="utf-8")
    entry = {
        "id": DOC_ID,
        "title": "全量界面资产库",
        "file": DOC.name,
        "summary": "按系统大类和系统整理的界面资产表单，保留手游图示、PC图示和界面分析三类填写位。",
        "lines": len(content.splitlines()),
        "contentB64": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    match = re.search(r"const KNOWLEDGE_DOCS = (\[.*?\]);\nlet currentKnowledgeDocId", text, re.S)
    if not match:
        raise RuntimeError("Cannot locate KNOWLEDGE_DOCS")
    docs = json.loads(match.group(1))
    docs = [doc for doc in docs if doc.get("id") != DOC_ID]
    docs.append(entry)
    text = text[: match.start(1)] + json.dumps(docs, ensure_ascii=False) + text[match.end(1) :]
    INDEX.write_text(text, encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_doc(rows)
    update_index()
    print(json.dumps({"rows": len(rows), "doc": str(DOC), "updatedIndex": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
