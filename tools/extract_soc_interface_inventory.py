from __future__ import annotations

import csv
import json
import posixpath
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
DATA_DIR = ROOT / "data"
INVENTORY_BOOK_KEY = "SOC项目全量界面整理"
RLS_BOOK_KEY = "_RLS-全量界面跑测表"

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CELL_RE = re.compile(r"([A-Z]+)([0-9]+)")


@dataclass(frozen=True)
class SheetInfo:
    index: int
    name: str
    target: str


def column_to_number(col: str) -> int:
    value = 0
    for char in col:
        value = value * 26 + ord(char) - 64
    return value


def split_cell_ref(ref: str) -> tuple[int, int]:
    match = CELL_RE.match(ref)
    if not match:
        raise ValueError(f"Invalid cell ref: {ref}")
    return column_to_number(match.group(1)), int(match.group(2))


def find_workbook(key: str) -> Path:
    matches = [path for path in WORKSPACE.glob("*.xlsx") if key in path.name]
    if not matches:
        raise FileNotFoundError(f"Cannot find workbook containing {key!r} in {WORKSPACE}")
    return matches[0]


def load_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    values: list[str] = []
    ns = f"{{{MAIN_NS}}}"
    for si in root.findall(ns + "si"):
        values.append("".join(t.text or "" for t in si.iter(ns + "t")))
    return values


def workbook_sheets(zf: zipfile.ZipFile) -> list[SheetInfo]:
    wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
    rel_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rid_to_target: dict[str, str] = {}
    for rel in rel_root:
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if not rid or not target:
            continue
        rid_to_target[rid] = (
            target.lstrip("/")
            if target.startswith("/")
            else posixpath.normpath(posixpath.join("xl", target))
        )

    sheets: list[SheetInfo] = []
    ns = {"main": MAIN_NS}
    for index, sheet in enumerate(wb_root.findall("main:sheets/main:sheet", ns), 1):
        rid = sheet.attrib.get(f"{{{REL_NS}}}id")
        target = rid_to_target.get(rid or "")
        if target:
            sheets.append(SheetInfo(index=index, name=sheet.attrib["name"], target=target))
    return sheets


def read_sheet_rows(
    zf: zipfile.ZipFile,
    sheet: SheetInfo,
    shared: list[str],
    fill_merged_cols: set[int] | None = None,
) -> dict[int, dict[int, str]]:
    root = ET.fromstring(zf.read(sheet.target))
    ns = f"{{{MAIN_NS}}}"
    rows: dict[int, dict[int, str]] = {}
    for cell in root.iter(ns + "c"):
        ref = cell.attrib.get("r", "")
        match = CELL_RE.match(ref)
        if not match:
            continue
        col = column_to_number(match.group(1))
        row = int(match.group(2))
        cell_type = cell.attrib.get("t")
        value = ""
        if cell_type == "inlineStr":
            value = "".join(t.text or "" for t in cell.iter(ns + "t"))
        else:
            raw = cell.find(ns + "v")
            if raw is not None and raw.text is not None:
                if cell_type == "s":
                    try:
                        value = shared[int(raw.text)]
                    except (IndexError, ValueError):
                        value = f"#S({raw.text})"
                else:
                    value = raw.text
        value = clean_text(value)
        if value:
            rows.setdefault(row, {})[col] = value
    if fill_merged_cols:
        apply_merged_cells(root, rows, fill_merged_cols)
    return rows


def apply_merged_cells(root: ET.Element, rows: dict[int, dict[int, str]], fill_cols: set[int]) -> None:
    ns = f"{{{MAIN_NS}}}"
    merge_root = root.find(ns + "mergeCells")
    if merge_root is None:
        return
    for merge in merge_root.findall(ns + "mergeCell"):
        ref = merge.attrib.get("ref", "")
        if ":" not in ref:
            continue
        start, end = ref.split(":", 1)
        start_col, start_row = split_cell_ref(start)
        end_col, end_row = split_cell_ref(end)
        if start_col not in fill_cols:
            continue
        value = rows.get(start_row, {}).get(start_col, "")
        if not value:
            continue
        for row in range(start_row, end_row + 1):
            row_values = rows.setdefault(row, {})
            for col in range(start_col, end_col + 1):
                row_values.setdefault(col, value)


def clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    raw_lines = [part.strip() for part in text.replace("\r", "\n").split("\n") if part.strip()]
    if len(raw_lines) > 1 and all(len(part) <= 2 for part in raw_lines):
        text = "".join(raw_lines)
    else:
        text = " / ".join(raw_lines) if raw_lines else text
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    text = re.sub(r"\s*/\s*-\s*/\s*", "-", text)
    text = re.sub(r"-\s*/\s*", "-", text)
    return text


def normalize_inventory_label(value: str) -> str:
    text = clean_text(value)
    replacements = {
        "局外系统 / —含跨局内外部分—": "局外系统（含跨局内外部分）",
        "局内 / - / 主 / H / U / D": "局内-主HUD",
        "交互容器- / 储物类": "交互容器-储物类",
        "交互容器- / 特殊类": "交互容器-特殊类",
        "交互容器- / 转化类": "交互容器-转化类",
        "活动中心 / (潘多拉)": "活动中心（潘多拉）",
        "活跃 / (贡献点抽奖&商城)": "活跃（贡献点抽奖&商城）",
    }
    return replacements.get(text, text)


def normalize_name(value: str) -> str:
    value = clean_text(value)
    value = re.sub(r"^\d+[-_ ]*", "", value)
    value = value.replace("（", "(").replace("）", ")")
    value = re.sub(r"\s+", "", value)
    return value.lower()


def split_people(value: str) -> list[str]:
    value = clean_text(value).replace("@", "")
    if not value or value in {"无", "/", "-"}:
        return []
    parts = re.split(r"[,，、/；;|]+", value)
    return [part.strip() for part in parts if part.strip() and part.strip() not in {"无", "-"}]


def extract_inventory() -> tuple[list[dict[str, str]], dict[str, Any]]:
    path = find_workbook(INVENTORY_BOOK_KEY)
    with zipfile.ZipFile(path) as zf:
        shared = load_shared_strings(zf)
        sheets = workbook_sheets(zf)
        sheet = next(s for s in sheets if s.name == "界面盘点")
        rows = read_sheet_rows(zf, sheet, shared, fill_merged_cols={1, 2, 9, 10, 11})

    records: list[dict[str, str]] = []
    current_domain = ""
    current_system = ""
    current_process = ""
    skipped_rows = 0

    for row_number in sorted(rows):
        if row_number == 1:
            continue
        cells = rows[row_number]
        if cells.get(1):
            current_domain = normalize_inventory_label(cells[1])
        if cells.get(2):
            current_system = normalize_inventory_label(cells[2])
            current_process = current_system
        if cells.get(3):
            current_process = normalize_inventory_label(cells[3])

        interface_name = normalize_inventory_label(cells.get(3, ""))
        fgui_name = clean_text(cells.get(4, ""))
        if not interface_name and not fgui_name:
            skipped_rows += 1
            continue

        record = {
            "来源文件": path.name,
            "来源Sheet": sheet.name,
            "原始行号": str(row_number),
            "系统大类": current_domain,
            "系统": current_system,
            "界面": interface_name or fgui_name,
            "界面过程名称": interface_name or current_process or current_system,
            "FGUI名称": fgui_name,
            "界面优先级": cells.get(5, ""),
            "负责交互": cells.get(9, ""),
            "负责拼接": cells.get(10, ""),
            "负责GUI": cells.get(11, ""),
            "PC定制等级": cells.get(12, ""),
            "PC制作方式": cells.get(13, ""),
            "PC工作量": cells.get(14, ""),
            "定制优先级": cells.get(15, ""),
            "PC制作进展": cells.get(16, ""),
            "RLS备注": cells.get(17, ""),
            "B2备注": cells.get(18, ""),
            "风格迭代总进展": cells.get(20, ""),
            "跑测来源": cells.get(21, ""),
        }
        records.append(record)

    meta = {
        "source": str(path),
        "sheet": "界面盘点",
        "records": len(records),
        "skipped_rows_without_interface_or_fgui": skipped_rows,
    }
    return records, meta


def is_example_rls_row(cells: dict[int, str], header: dict[int, str]) -> bool:
    desc = cells.get(header_reverse(header).get("问题描述", 4), "")
    link = " ".join(cells.values())
    reporter = cells.get(1, "")
    return (
        "大厅通行证入口UI显示异常" in desc
        and ("xxxxx" in link or reporter in {"张三", "王杰"})
    )


def header_reverse(header: dict[int, str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for col, label in header.items():
        normalized = clean_text(label)
        if "问题描述" in normalized:
            out["问题描述"] = col
        elif "负责职能" in normalized:
            out["负责职能"] = col
        elif "解决人员" in normalized:
            out["解决人员"] = col
        elif "完成状态" in normalized:
            out["完成状态"] = col
        elif "负责UI" in normalized:
            out["负责UI"] = col
        elif "所属模块" in normalized:
            out["所属模块"] = col
        elif "开单链接" in normalized:
            out["开单链接"] = col
        elif "优先级" in normalized:
            out["优先级"] = col
        elif "类型" in normalized:
            out["类型"] = col
        elif "测试环境" in normalized or "移动/PC端" in normalized:
            out["平台/环境"] = col
    return out


def extract_rls() -> tuple[list[dict[str, str]], list[dict[str, Any]], dict[str, Any]]:
    path = find_workbook(RLS_BOOK_KEY)
    issue_records: list[dict[str, str]] = []
    sheet_summaries: list[dict[str, Any]] = []

    with zipfile.ZipFile(path) as zf:
        shared = load_shared_strings(zf)
        sheets = workbook_sheets(zf)
        for sheet in sheets:
            rows = read_sheet_rows(zf, sheet, shared)
            if sheet.name in {"总览", "模板"}:
                continue
            header_row = rows.get(2, {})
            header_map = header_reverse(header_row)
            desc_col = header_map.get("问题描述", 4)
            role_col = header_map.get("负责职能", 9)
            assignee_col = header_map.get("解决人员", 10)
            status_col = header_map.get("完成状态", 12)
            ui_col = header_map.get("负责UI", 14)
            module_col = header_map.get("所属模块", 16)
            priority_col = header_map.get("优先级", 8)
            type_col = header_map.get("类型", 7)
            env_col = header_map.get("平台/环境", 3)
            link_col = header_map.get("开单链接", 13)

            roles: Counter[str] = Counter()
            assignees: Counter[str] = Counter()
            ui_owners: Counter[str] = Counter()
            statuses: Counter[str] = Counter()
            modules: Counter[str] = Counter()
            issue_count = 0
            examples: list[str] = []

            for row_number in sorted(rows):
                if row_number <= 2:
                    continue
                cells = rows[row_number]
                if is_example_rls_row(cells, header_row):
                    continue
                desc = cells.get(desc_col, "")
                if not desc:
                    continue
                issue_count += 1
                role = cells.get(role_col, "")
                assignee = cells.get(assignee_col, "")
                status = cells.get(status_col, "")
                ui_owner = cells.get(ui_col, "")
                module = cells.get(module_col, "")
                for item in split_people(role):
                    roles[item] += 1
                for item in split_people(assignee):
                    assignees[item] += 1
                for item in split_people(ui_owner):
                    ui_owners[item] += 1
                if status:
                    statuses[status] += 1
                if module:
                    modules[module] += 1
                if len(examples) < 3:
                    examples.append(desc)

                issue_records.append(
                    {
                        "来源文件": path.name,
                        "来源Sheet": sheet.name,
                        "原始行号": str(row_number),
                        "系统/跑测表": sheet.name,
                        "系统归一名": normalize_name(sheet.name),
                        "平台/环境": cells.get(env_col, ""),
                        "问题描述": desc,
                        "类型": cells.get(type_col, ""),
                        "优先级": cells.get(priority_col, ""),
                        "负责职能": role,
                        "解决人员": assignee,
                        "完成状态": status,
                        "负责UI": ui_owner,
                        "所属模块": module,
                        "开单链接": cells.get(link_col, ""),
                    }
                )

            sheet_summaries.append(
                {
                    "sheet序号": sheet.index,
                    "系统/跑测表": sheet.name,
                    "系统归一名": normalize_name(sheet.name),
                    "问题数": issue_count,
                    "主要负责职能": counter_to_text(roles, 5),
                    "主要解决人员": counter_to_text(assignees, 5),
                    "负责UI": counter_to_text(ui_owners, 5),
                    "状态分布": counter_to_text(statuses, 6),
                    "所属模块": counter_to_text(modules, 5),
                    "样例问题": "；".join(examples),
                }
            )

    meta = {
        "source": str(path),
        "sheets": len(sheet_summaries),
        "issues": len(issue_records),
    }
    return issue_records, sheet_summaries, meta


def counter_to_text(counter: Counter[str], limit: int = 5) -> str:
    if not counter:
        return ""
    return "、".join(f"{name}({count})" for name, count in counter.most_common(limit))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def group_inventory(records: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for record in records:
        system = record["系统"] or "未归类"
        bucket = grouped.setdefault(
            system,
            {
                "系统大类": record["系统大类"],
                "系统": system,
                "界面数": 0,
                "界面优先级": Counter(),
                "负责交互": Counter(),
                "负责拼接": Counter(),
                "负责GUI": Counter(),
                "PC定制等级": Counter(),
                "PC制作方式": Counter(),
                "PC制作进展": Counter(),
                "界面列表": [],
            },
        )
        bucket["界面数"] += 1
        for field in ["界面优先级", "负责交互", "负责拼接", "负责GUI", "PC定制等级", "PC制作方式", "PC制作进展"]:
            value = record.get(field, "")
            if not value:
                continue
            if field.startswith("负责"):
                for person in split_people(value):
                    bucket[field][person] += 1
            else:
                bucket[field][value] += 1
        bucket["界面列表"].append(record)
    return grouped


def summarize_domains(records: list[dict[str, str]]) -> list[dict[str, str]]:
    domains: dict[str, dict[str, Any]] = {}
    for record in records:
        domain = record["系统大类"] or "未归类"
        system = record["系统"] or "未归类"
        bucket = domains.setdefault(domain, {"系统大类": domain, "系统集合": set(), "界面数": 0})
        bucket["系统集合"].add(system)
        bucket["界面数"] += 1
    rows = []
    for domain, bucket in domains.items():
        systems = sorted(bucket["系统集合"])
        rows.append(
            {
                "系统大类": domain,
                "系统数": str(len(systems)),
                "界面数": str(bucket["界面数"]),
                "系统清单": "、".join(systems),
            }
        )
    return rows


def write_markdown(
    inventory_records: list[dict[str, str]],
    rls_summaries: list[dict[str, Any]],
    inventory_meta: dict[str, Any],
    rls_meta: dict[str, Any],
) -> None:
    grouped = group_inventory(inventory_records)
    domains = summarize_domains(inventory_records)
    rls_by_norm = {row["系统归一名"]: row for row in rls_summaries}

    lines: list[str] = []
    lines.append("# SOC UXD 全量界面资产库")
    lines.append("")
    lines.append("## 元信息")
    lines.append("")
    lines.append("| 字段 | 内容 |")
    lines.append("| --- | --- |")
    lines.append("| 所属工作区 | 资产参考 |")
    lines.append("| 页面类型 | 资产页 |")
    lines.append("| 成熟度 | 建设中 |")
    lines.append(f"| 来源 | {Path(inventory_meta['source']).name}；{Path(rls_meta['source']).name} |")
    lines.append("| 最近更新 | 2026-06-27 |")
    lines.append("")
    lines.append("## 一句话结论")
    lines.append("")
    lines.append("当前最可信的“系统-界面-负责人”资产来源是《SOC项目全量界面整理.xlsx》的“界面盘点”sheet；《_RLS-全量界面跑测表.xlsx》更适合作为按系统拆分的落地问题库，用来补充系统边界、负责职能、拼接风险和回归验收线索。")
    lines.append("")
    lines.append("## 数据读取结论")
    lines.append("")
    lines.append(f"- 主界面资产表提取到 {len(inventory_records)} 条界面记录，跳过 {inventory_meta['skipped_rows_without_interface_or_fgui']} 行没有界面名/FGUI 名称的辅助记录。")
    lines.append(f"- 跑测表提取到 {len(rls_summaries)} 个系统/功能 sheet，问题记录 {rls_meta['issues']} 条。")
    lines.append("- 两个 Excel 的体积主要来自截图图片；本次只抽取文本单元格、sheet 名称和问题字段，未对截图做 OCR。")
    lines.append("- “界面过程名称”在当前表格中不是独立字段，本版先用“界面名”暂代；后续如果从 Figma 交互文档中抽取流程节点，可再升级为真正的过程名。")
    lines.append("")
    lines.append("## 系统大类总览")
    lines.append("")
    lines.append("| 系统大类 | 系统数 | 界面数 | 系统清单 |")
    lines.append("| --- | ---: | ---: | --- |")
    for row in domains:
        lines.append(f"| {md(row['系统大类'])} | {row['系统数']} | {row['界面数']} | {md(row['系统清单'])} |")
    lines.append("")
    lines.append("## 系统级资产索引")
    lines.append("")
    lines.append("| 系统大类 | 系统 | 界面数 | 负责交互 | 负责拼接 | 负责GUI | PC定制等级 | PC制作方式 | 跑测问题数 |")
    lines.append("| --- | --- | ---: | --- | --- | --- | --- | --- | ---: |")
    for system, bucket in sorted(grouped.items(), key=lambda item: (item[1]["系统大类"], item[0])):
        norm = normalize_name(system)
        rls = rls_by_norm.get(norm)
        issue_count = rls["问题数"] if rls else ""
        lines.append(
            "| {domain} | {system} | {count} | {interaction} | {stitch} | {gui} | {level} | {method} | {issues} |".format(
                domain=md(bucket["系统大类"]),
                system=md(system),
                count=bucket["界面数"],
                interaction=md(counter_to_text(bucket["负责交互"], 6)),
                stitch=md(counter_to_text(bucket["负责拼接"], 6)),
                gui=md(counter_to_text(bucket["负责GUI"], 6)),
                level=md(counter_to_text(bucket["PC定制等级"], 4)),
                method=md(counter_to_text(bucket["PC制作方式"], 4)),
                issues=issue_count,
            )
        )
    lines.append("")
    lines.append("## 全量界面清单")
    lines.append("")
    lines.append("| 系统大类 | 系统 | 界面 | 界面过程名称 | FGUI名称 | 优先级 | 负责交互 | 负责拼接 | 负责GUI | PC定制等级 | PC制作方式 | PC进展 | 备注 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for record in inventory_records:
        note = "；".join(filter(None, [record["RLS备注"], record["B2备注"], record["风格迭代总进展"]]))
        lines.append(
            "| {domain} | {system} | {interface} | {process} | {fgui} | {priority} | {interaction} | {stitch} | {gui} | {level} | {method} | {progress} | {note} |".format(
                domain=md(record["系统大类"]),
                system=md(record["系统"]),
                interface=md(record["界面"]),
                process=md(record["界面过程名称"]),
                fgui=md(record["FGUI名称"]),
                priority=md(record["界面优先级"]),
                interaction=md(record["负责交互"]),
                stitch=md(record["负责拼接"]),
                gui=md(record["负责GUI"]),
                level=md(record["PC定制等级"]),
                method=md(record["PC制作方式"]),
                progress=md(record["PC制作进展"]),
                note=md(note),
            )
        )
    lines.append("")
    lines.append("## 跑测系统索引")
    lines.append("")
    lines.append("| sheet序号 | 系统/跑测表 | 问题数 | 主要负责职能 | 主要解决人员 | 负责UI | 状态分布 | 所属模块 | 样例问题 |")
    lines.append("| ---: | --- | ---: | --- | --- | --- | --- | --- | --- |")
    for row in rls_summaries:
        lines.append(
            "| {idx} | {system} | {count} | {roles} | {people} | {ui} | {status} | {module} | {sample} |".format(
                idx=row["sheet序号"],
                system=md(row["系统/跑测表"]),
                count=row["问题数"],
                roles=md(row["主要负责职能"]),
                people=md(row["主要解决人员"]),
                ui=md(row["负责UI"]),
                status=md(row["状态分布"]),
                module=md(row["所属模块"]),
                sample=md(row["样例问题"]),
            )
        )
    lines.append("")
    lines.append("## 交互设计使用方式")
    lines.append("")
    lines.append("1. 新功能立项时，先在“系统级资产索引”查同类系统，确认是否已有相似界面、PC定制等级和负责人经验。")
    lines.append("2. 写交互文档时，用“全量界面清单”校验界面边界：系统内有哪些主界面、弹窗、Tips、HUD、列表、设置项等历史对象。")
    lines.append("3. 做 Figma/FGUI 交付前，用“跑测系统索引”查看历史高频问题，尤其是拼接、GUI、客户端、策划之间的责任边界。")
    lines.append("4. 后续从 Figma 文档继续抽取入口/出口/状态矩阵后，可以把本表中的“界面过程名称”升级为真正的流程节点。")
    lines.append("")
    lines.append("## 待补充 / 待确认")
    lines.append("")
    lines.append("- 当前 Excel 未提供稳定的“入口、出口、跳转目标、状态矩阵”字段，需要继续从典型 Figma 交互文档中抽取。")
    lines.append("- 跑测表的系统 sheet 名可视为系统分类依据，但部分 sheet 是问题表或模板历史遗留，仍需人工确认是否进入正式资产库。")
    lines.append("- “负责交互/负责拼接/负责GUI”来自盘点表，可能随排期变化，需要后续和当前项目分工表同步。")

    (ROOT / "SOC UXD 全量界面资产库.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def md(value: Any) -> str:
    text = clean_text(value)
    text = text.replace("|", "\\|")
    return text


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    inventory_records, inventory_meta = extract_inventory()
    rls_issues, rls_summaries, rls_meta = extract_rls()

    write_csv(DATA_DIR / "soc-interface-inventory.csv", inventory_records)
    write_csv(DATA_DIR / "soc-rls-issues.csv", rls_issues)
    write_csv(DATA_DIR / "soc-rls-system-summary.csv", rls_summaries)
    (DATA_DIR / "soc-interface-analysis-meta.json").write_text(
        json.dumps({"inventory": inventory_meta, "rls": rls_meta}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(inventory_records, rls_summaries, inventory_meta, rls_meta)
    print(json.dumps({"inventory": inventory_meta, "rls": rls_meta}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
