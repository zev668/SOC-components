from __future__ import annotations

import collections
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path("E:/Project/trunk/SocRes/SocData/Excel/a2/Datas")
OUT = ROOT / ".codex" / "skills" / "game-interaction-design" / "references" / "interface-layering-spec.md"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def col_to_num(cell: str) -> int:
    match = re.match(r"([A-Z]+)", cell or "")
    if not match:
        return 0
    number = 0
    for char in match.group(1):
        number = number * 26 + ord(char) - 64
    return number


def text_of_si(si: ET.Element) -> str:
    return "".join((node.text or "") for node in si.findall(".//a:t", NS))


def read_xlsx(path: Path) -> list[tuple[str, list[list[str]]]]:
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [text_of_si(si) for si in root.findall("a:si", NS)]

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

        sheets: list[tuple[str, list[list[str]]]] = []
        for sheet in workbook.find("a:sheets", NS) or []:
            name = sheet.attrib["name"]
            rid = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = rid_to_target[rid]
            sheet_path = "xl/" + target if not target.startswith("/") else target.lstrip("/")
            root = ET.fromstring(archive.read(sheet_path))
            rows: list[list[str]] = []
            for row in root.findall(".//a:sheetData/a:row", NS):
                values: dict[int, str] = {}
                for cell in row.findall("a:c", NS):
                    ref = cell.attrib.get("r", "")
                    col = col_to_num(ref)
                    cell_type = cell.attrib.get("t")
                    v = cell.find("a:v", NS)
                    inline = cell.find("a:is", NS)
                    value = ""
                    if cell_type == "s" and v is not None:
                        idx = int(v.text or 0)
                        value = shared[idx] if idx < len(shared) else ""
                    elif cell_type == "inlineStr" and inline is not None:
                        value = "".join((t.text or "") for t in inline.findall(".//a:t", NS))
                    elif v is not None:
                        value = v.text or ""
                    values[col] = value
                if values:
                    max_col = max(values)
                    rows.append([values.get(i, "") for i in range(1, max_col + 1)])
            sheets.append((name, rows))
        return sheets


def table(rows: list[list[str]]) -> tuple[list[str], list[str], list[dict[str, str]]]:
    comments = rows[0] if rows else []
    variables = rows[1] if len(rows) > 1 else []
    data: list[dict[str, str]] = []
    for row in rows[3:]:
        if not any(str(x).strip() for x in row):
            continue
        item: dict[str, str] = {}
        for i, key in enumerate(variables):
            if key:
                item[key] = row[i] if i < len(row) else ""
        item["_comment"] = row[0] if row else ""
        data.append(item)
    return comments, variables, data


def val(item: dict[str, str], key: str) -> str:
    return str(item.get(key, "") or "").strip()


def count(data: list[dict[str, str]], field: str) -> collections.Counter[str]:
    return collections.Counter(val(row, field) or "空" for row in data)


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value: object) -> str:
        text = str(value if value is not None else "")
        text = text.replace("\r\n", "\n").replace("\n", "<br>")
        text = text.replace("|", "\\|")
        return text

    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(cell(x) for x in row) + " |" for row in rows)
    return "\n".join(out)


def layer_sort_key(layer: dict[str, str]) -> tuple[int, int]:
    order = int(val(layer, "order") or 0)
    layer_id = int(val(layer, "id") or 0)
    return (order, layer_id)


def ui_sort_key(ui: dict[str, str], layer_by_id: dict[str, dict[str, str]]) -> tuple[int, int, int]:
    layer_id = val(ui, "layer")
    layer = layer_by_id.get(layer_id, {})
    order = int(val(layer, "order") or 0)
    lid = int(layer_id or 0)
    uid = int(val(ui, "id") or 0)
    return (order, lid, uid)


def main() -> None:
    candidates = list(SOURCE_DIR.glob("08_*.xlsx"))
    if not candidates:
        raise FileNotFoundError("Cannot find 08_*.xlsx")
    source = candidates[0]

    sheets = read_xlsx(source)
    layers = table(sheets[0][1])[2]
    uis = table(sheets[1][1])[2]
    hud = table(sheets[2][1])[2]
    hud_pc = table(sheets[3][1])[2]
    hud_control = table(sheets[4][1])[2]
    slots = table(sheets[5][1])[2]
    backgrounds = table(sheets[6][1])[2]

    layer_by_id = {val(layer, "id"): layer for layer in layers}

    layer_notes = {
        "101": "与三维大世界场景强相关的 UI，如准星、血条、3D UI、世界标记等。",
        "201": "HUD 层，浮于大世界场景上方的信息与操作 UI，如战斗操作按钮、载具操作按钮等。",
        "301": "介于 HUD 之上、全屏界面之下的玩法信息界面，如载具半屏、中控台半屏、局内玩法信息等。",
        "501": "完全盖住场景的全屏界面，如背包、科技、设置、商城、地图等。",
        "502": "Pandora 专用承载层 1，表内明确备注其他界面不要放。",
        "503": "Pandora 专用承载层 2，表内明确备注其他界面不要放。",
        "504": "Pandora 专用承载层 3，表内明确备注其他界面不要放。",
        "901": "Loading 之下的弹窗层，用于部分 loading 过程中被动触发、需要与 loading 关系特殊处理的弹窗。",
        "801": "Loading 层，用于进入大厅、进入局内等加载界面。",
        "1001": "拍照界面层，单独存放拍照功能相关界面。",
        "1101": "管理员工具层。图中旁注为超宽屏幕黑色遮罩，但 Excel 当前排序与图示不一致，需确认。",
        "601": "弹窗层，所有模态/非模态弹窗默认放在这一层。",
        "701": "通知提醒层，轻量通知提示信息，如 toast、击杀播报等。",
        "902": "输入法层，Excel 表内存在但图中未展示；常驻且最大数量为 1。",
        "910": "水印层，用于测试水印等最高全局展示。",
    }

    layer_counts = count(uis, "layer")
    layer_rows: list[list[object]] = []
    for layer in sorted(layers, key=layer_sort_key):
        layer_id = val(layer, "id")
        layer_rows.append([
            val(layer, "order"),
            layer_id,
            val(layer, "name"),
            val(layer, "_comment"),
            val(layer, "ruler"),
            "是" if val(layer, "persistent") == "1" else "否",
            val(layer, "maxWinCount"),
            layer_counts.get(layer_id, 0),
            layer_notes.get(layer_id, ""),
        ])

    flag_fields = [
        ("HideWithStack", "跟随全屏界面入栈隐藏"),
        ("breakTouchOnEnable", "显示界面时打断触摸"),
        ("isHalfScreen", "半屏界面"),
        ("fullScreenVisually", "视觉上全屏界面"),
        ("EscClose", "PC 界面关闭设置"),
        ("showCursorType", "PC 鼠标指针显示类型"),
        ("IsBlockInput", "是否屏蔽操作"),
        ("multiScale", "PC 二次缩放"),
        ("uiTargetFrameRate", "打开界面时限制帧率"),
        ("hideLayerAtOnce", "立即隐藏 Layer"),
        ("HideHomeBtn", "隐藏 ComTopBar home 按钮"),
        ("fillBg", "超出宽高比例时填充黑边"),
        ("skipAutoUiTest", "跳过自动兼容性测试"),
        ("showInDeath", "死亡时显示"),
        ("showInWounded", "倒地时显示"),
        ("needCloseGyro", "屏蔽手机陀螺仪"),
        ("needPreloadMobile", "手机端需要预加载"),
        ("needPreloadPC", "PC 端需要预加载"),
    ]

    flag_rows: list[list[object]] = []
    for field, label in flag_fields:
        dist = count(uis, field).most_common()
        flag_rows.append([
            field,
            label,
            "；".join(f"{k}={v}" for k, v in dist if k != "空") or "暂无有效配置",
            count(uis, field).get("空", 0),
        ])

    pc_overrides = [ui for ui in uis if val(ui, "layer_PC")]

    hud_rows = [
        ["HUD表", len(hud), "移动端 HUD 元素定义，包含元素节点、插槽、排序、分组、内部层级、可编辑性。"],
        ["HUD_PC表", len(hud_pc), "PC 端 HUD 元素定义，字段与移动端类似，并增加 keyGuideId 等 PC 键位引导信息。"],
        ["HUD_显示控制表", len(hud_control), "按玩法/状态列出需要显示和隐藏的 HUD 元素，并提供 PC 模式追加项。"],
        ["HUD_槽位表", len(slots), "定义 HUD 主操作槽位与输入系统 path 的对应关系。"],
        ["界面场景背景表", len(backgrounds), "定义若干全屏/场景背景资源的 FGUI 路径、缩放、平铺、偏移。"],
    ]

    layer_examples: list[str] = []
    for layer in sorted(layers, key=layer_sort_key):
        layer_id = val(layer, "id")
        group = [ui for ui in uis if val(ui, "layer") == layer_id]
        if not group:
            continue
        examples = "；".join(f"{val(ui, '_comment')}({val(ui, 'uniqueName')})" for ui in group[:12])
        layer_examples.append(f"- `{layer_id}` {val(layer, 'name')}：{len(group)} 个。例：{examples}")

    full_rows: list[list[object]] = []
    for ui in sorted(uis, key=lambda item: ui_sort_key(item, layer_by_id)):
        layer_id = val(ui, "layer")
        layer = layer_by_id.get(layer_id, {})
        pc_layer = val(ui, "layer_PC")
        full_rows.append([
            val(layer, "order"),
            layer_id,
            val(layer, "name"),
            val(ui, "id"),
            val(ui, "_comment"),
            val(ui, "uniqueName"),
            val(ui, "pack"),
            val(ui, "com"),
            pc_layer,
            val(ui, "EscClose"),
            val(ui, "IsBlockInput"),
            val(ui, "isHalfScreen"),
            val(ui, "fullScreenVisually"),
            val(ui, "HideWithStack"),
        ])

    doc: list[str] = []
    doc.append("# 界面层级与堆栈规范")
    doc.append("")
    doc.append("版本：v0.1")
    doc.append("记录时间：2026-06-27")
    doc.append(f"来源：用户提供的层级规范图、层级原则图，以及 `{source}`。")
    doc.append("")
    doc.append("## 一句话结论")
    doc.append("")
    doc.append("新建或评审任何界面时，必须先判断它属于哪个运行层级，再定义关闭方式、输入阻挡、是否跟随全屏入栈隐藏、移动/PC 差异和特殊状态。层级数字越大，默认越靠上显示；但后打开界面在实际堆栈中仍会覆盖先打开界面。")
    doc.append("")
    doc.append("## 适用范围")
    doc.append("")
    doc.append("- 全局界面层级判断：场景 UI、HUD、局内覆盖层、全屏界面、Loading、弹窗、通知、水印等。")
    doc.append("- 界面堆栈规则：打开顺序、关闭顺序、PC Esc 关闭、移动点击关闭、输入阻挡。")
    doc.append("- FGUI 配置检查：`UI界面表` 中的 `layer`、`layer_PC`、`EscClose`、`IsBlockInput` 等字段。")
    doc.append("- HUD 体系：`HUD表`、`HUD_PC表`、`HUD_显示控制表` 和 `HUD_槽位表`。")
    doc.append("")
    doc.append("不替代全屏界面框架规范。全屏界面的 `bg/root/topBar/navBar/content` 结构仍查 `fullscreen-framework-translation.md`。")
    doc.append("")
    doc.append("## 层级原则")
    doc.append("")
    doc.append("1. 不同层级的界面按层级数字排序，数字越大的界面排在越上层。")
    doc.append("2. 所有界面必须按层级定义放入对应层级；不符合层级定义的界面需要调整配置表并走 QC。")
    doc.append("3. 后打开的界面会覆盖先打开的界面。")
    doc.append("4. 关闭界面时从最上层界面开始依次关闭。")
    doc.append("5. 如果后打开界面的层级低于先打开界面，实际显示上仍以后打开界面在上方；移动端通常点击关闭，PC 端通常按 Esc 关闭。")
    doc.append("6. 上述问题需要移动端和 PC 双端验证；如果不符合规则，应出 bug 给对应人员解决。")
    doc.append("")
    doc.append("## 层级定义")
    doc.append("")
    doc.append(md_table(
        ["排序", "层级ID", "工程名", "中文含义", "ruler", "常驻", "最大数量", "当前界面数", "使用说明"],
        layer_rows,
    ))
    doc.append("")
    doc.append("### 当前需要确认的差异")
    doc.append("")
    doc.append("- 图中 `Admin` 管理员工具层标注层级为 310，但 Excel `层级表` 当前 `order=291`；运行配置和规范图不一致，需要确认最终以哪一个为准。")
    doc.append("- Excel 中存在 `Input` 输入法层：`id=902`、`order=350`、`persistent=1`、`maxWinCount=1`，但图中未展示。")
    doc.append("- Excel 中存在 `PandoraType0/1/2` 三个专用承载层，图中未展示；表内明确备注其他界面不要放。")
    doc.append("- `Notice` 与 `Input` 当前排序都为 350；如果程序没有额外 tie-breaker，需要确认同排序时的实际覆盖规则。")
    doc.append("")
    doc.append("## 设计时的层级判断")
    doc.append("")
    doc.append("| 判断问题 | 推荐层级 | 说明 |")
    doc.append("| --- | --- | --- |")
    doc.append("| 是否与 3D 世界强绑定，如准星、血条、世界标记、伤害跳字？ | `101 GamePlay` | 不应作为普通弹窗或全屏页面处理。 |")
    doc.append("| 是否是玩家持续操作的 HUD 信息或按钮？ | `201 HUD` + HUD 表 | 全局 UI 表只登记 `UiHud`，具体元素要进 HUD 表。 |")
    doc.append("| 是否是局内半屏、玩法信息、覆盖在 HUD 上但不完全遮住场景？ | `301 GamePlayOverlay` | 如中控台、载具半屏、局内玩法状态。 |")
    doc.append("| 是否完全盖住场景，成为一个主要系统界面？ | `501 Full Screen` | 同时套用全屏框架规范。 |")
    doc.append("| 是否是 Pandora 专用承载？ | `502/503/504` | 普通界面不要使用。 |")
    doc.append("| 是否是 loading 过程中触发且要和 loading 特殊共存的弹窗？ | `901 PopupLoading` | 需要明确和 Loading 的遮挡关系。 |")
    doc.append("| 是否是进入大厅、进入局内等加载界面？ | `801 Loading` | 常见配置是阻挡输入、不可 Esc 关闭。 |")
    doc.append("| 是否为拍照功能相关界面？ | `1001 Photo` | 单独层，不和普通弹窗混放。 |")
    doc.append("| 是否为管理员工具或超宽黑边等管理/调试层？ | `1101 Admin` | 当前排序差异需先确认。 |")
    doc.append("| 是否为普通弹窗、Tips、确认框、二级/三级弹层？ | `601 Popup` | 当前项目最大承载量为 4。 |")
    doc.append("| 是否为 toast、击杀播报、轻量系统提示？ | `701 Notice` | 不应放进普通 Popup 抢占交互栈。 |")
    doc.append("| 是否为输入法/输入相关全局层？ | `902 Input` | 常驻且最大数量为 1。 |")
    doc.append("| 是否为测试水印？ | `910 WaterMark` | 最高层，全局覆盖。 |")
    doc.append("")
    doc.append("## UI界面表字段解读")
    doc.append("")
    doc.append("`UI界面表` 共 493 条界面记录。以下字段和交互设计最相关：")
    doc.append("")
    doc.append(md_table(
        ["字段", "含义", "设计师需要标注什么"],
        [
            ["`layer`", "移动端/默认所属层级", "每个新界面都要先判断并给出建议层级。"],
            ["`layer_PC`", "PC 专属层级覆盖", "只有 PC 需要不同层级时填写；当前表里只有 `UiCurtain` 从 501 改到 601。"],
            ["`HideWithStack`", "跟随全屏界面入栈隐藏", "新界面会不会随全屏界面的入栈关系被隐藏。"],
            ["`breakTouchOnEnable`", "显示界面时打断触摸", "打开界面是否打断当前触摸/操作。"],
            ["`isHalfScreen`", "半屏界面", "半屏不等于普通弹窗，需结合层级判断。"],
            ["`fullScreenVisually`", "视觉上全屏界面", "即使工程层不一定是 501，视觉上全屏也要注明。"],
            ["`EscClose`", "PC 关闭方式", "`Close`/`None`/`Block` 需要在交互稿写清楚。"],
            ["`showCursorType`", "PC 鼠标指针显示类型", "PC 界面要明确是否显示鼠标、显示何种状态。"],
            ["`IsBlockInput`", "是否屏蔽操作", "是否阻挡大世界操作、点击穿透或后层输入。"],
            ["`uiTargetFrameRate`", "打开界面时限制帧率", "重型界面或性能敏感界面需要和程序确认。"],
            ["`hideLayerAtOnce`", "立即隐藏 Layer", "涉及切界面/关闭动画时需要确认是否立即隐藏。"],
            ["`HideHomeBtn`", "隐藏 ComTopBar home 按钮", "全屏界面 topBar 是否保留 home。"],
            ["`fillBg`", "超出宽高比例时填充黑边", "双端宽高比适配时需要标注。"],
            ["`showInDeath` / `showInWounded`", "死亡/倒地时仍显示", "局内界面必须确认这些特殊状态。"],
            ["`needCloseGyro`", "是否屏蔽手机陀螺仪", "移动端全屏/弹窗打开后是否要停陀螺仪。"],
            ["`needPreloadMobile` / `needPreloadPC`", "是否预加载", "重型界面或高频界面要和程序确认。"],
        ],
    ))
    doc.append("")
    doc.append("### 关键字段当前分布")
    doc.append("")
    doc.append(md_table(["字段", "中文含义", "有效值分布", "空值数"], flag_rows))
    doc.append("")
    doc.append("### PC 层级覆盖")
    doc.append("")
    if pc_overrides:
        doc.append(md_table(
            ["界面ID", "界面名称", "uniqueName", "移动层级", "PC层级", "关闭方式", "视觉全屏"],
            [[val(ui, "id"), val(ui, "_comment"), val(ui, "uniqueName"), val(ui, "layer"), val(ui, "layer_PC"), val(ui, "EscClose"), val(ui, "fullScreenVisually")] for ui in pc_overrides],
        ))
    else:
        doc.append("当前没有配置 PC 专属层级覆盖。")
    doc.append("")
    doc.append("## 当前界面层级分布")
    doc.append("")
    doc.extend(layer_examples)
    doc.append("")
    doc.append("## HUD 相关规则")
    doc.append("")
    doc.append("HUD 不应只看 `UI界面表`。`UI界面表` 里只有 `UiHud` 位于 `201 HUD`，真正的 HUD 元素由 HUD 专表控制。")
    doc.append("")
    doc.append(md_table(["表", "记录数", "作用"], hud_rows))
    doc.append("")
    doc.append("交互设计涉及 HUD 时，需要额外说明：HUD 元素名称、移动/PC 是否不同、是否阻挡点击、内部排序、分组、内部层级、是否可编辑、是否可移动/缩放/调透明、显示控制状态。")
    doc.append("")
    doc.append("### HUD 槽位")
    doc.append("")
    doc.append(md_table(
        ["ID", "节点名", "输入 path", "备注"],
        [[val(slot, "id"), val(slot, "node"), val(slot, "key"), val(slot, "_comment")] for slot in slots],
    ))
    doc.append("")
    doc.append("## 界面场景背景")
    doc.append("")
    doc.append(md_table(
        ["ID", "名称", "背景路径", "缩放", "平铺", "偏移"],
        [[val(bg, "id"), val(bg, "_comment"), val(bg, "Bac"), val(bg, "Scale"), val(bg, "Tiling"), val(bg, "Offset")] for bg in backgrounds],
    ))
    doc.append("")
    doc.append("## 交互设计输出约束")
    doc.append("")
    doc.append("新交互稿在涉及界面打开、关闭、遮挡、HUD 或弹窗时，应至少补充这些内容：")
    doc.append("")
    doc.append("- 建议层级：移动端 `layer`，如 PC 不同则写 `layer_PC`。")
    doc.append("- 堆栈关系：是否覆盖前一界面，是否跟随全屏界面入栈隐藏。")
    doc.append("- 关闭规则：移动端点击关闭区域，PC 端 Esc 行为，是否允许返回/关闭。")
    doc.append("- 输入规则：是否阻挡大世界操作，是否打断触摸，是否显示鼠标。")
    doc.append("- 场景状态：死亡、倒地、loading、拍照、HUD 编辑、PC/移动差异。")
    doc.append("- 工程注意：需要改配置表时明确写给程序；涉及 FGUI 层、HUD 元素或背景表时写给拼接。")
    doc.append("")
    doc.append("## 全量界面层级清单")
    doc.append("")
    doc.append("以下清单按 Excel `层级表.order` 从低到高排序，同层内按界面 ID 排序。")
    doc.append("")
    doc.append(md_table(
        ["排序", "层级ID", "层级名", "界面ID", "界面名称", "uniqueName", "FGUI包", "FGUI组件", "PC层级", "EscClose", "阻挡输入", "半屏", "视觉全屏", "随全屏栈隐藏"],
        full_rows,
    ))
    doc.append("")

    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"wrote {OUT} ({len(doc)} markdown blocks, {len(full_rows)} UI rows)")


if __name__ == "__main__":
    main()
