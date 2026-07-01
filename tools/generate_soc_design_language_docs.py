from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
RAW_ANT_DIR = WORKSPACE / "external-references" / "ant-design-spec" / "raw-md"
OUT_DIR = (
    WORKSPACE
    / ".codex"
    / "skills"
    / "game-interaction-design"
    / "references"
    / "soc-design-language"
)
ANT_COMMIT = "61861c8bc3a443836b20336830f2ae30db518813"


@dataclass(frozen=True)
class PageProfile:
    slug: str
    title: str
    group: str
    order: int
    focus: str
    scenario: str
    related: tuple[str, ...]


PAGE_PROFILES: list[PageProfile] = [
    PageProfile("introduce", "SOC 设计语言：体系介绍", "设计语言总览", 0, "把 SOC UXD 的原则、规范、资产和 AI 生产方式放进同一套可读目录。", "新系统立项、旧界面重构、AI 生成交互稿前的总入口。", ("soc-interaction-design-principles.md", "contracts.md", "checklists.md")),
    PageProfile("values", "SOC 设计语言：价值观", "设计语言总览", 1, "用顺手自然、明确确定、目标有意义、可沉淀生长四个价值观统一设计判断。", "需求还没有历史案例时，用价值观先判断方向是否成立。", ("soc-interaction-design-principles.md", "checklists.md")),
    PageProfile("overview", "SOC 设计语言：原则概览", "设计语言总览", 2, "把视觉组织、上下文保持、操作邀请、即时反馈等原则串成设计检查路径。", "评审一个界面是否只是堆控件，还是能解释任务、状态和结果。", ("soc-interaction-design-principles.md", "interaction-document-template-spec.md")),
    PageProfile("proximity", "SOC 原则：信息亲密性", "交互原则", 3, "用距离和分组表达对象关系、条件关系、奖励归属和操作归属。", "背包、任务、成员、奖励、配置列表等高密度信息组织。", ("soc-interaction-design-principles.md", "soc-common-components-catalog.md")),
    PageProfile("alignment", "SOC 原则：阅读对齐", "交互原则", 4, "用稳定阅读线降低扫读成本，让数值、按钮、状态和说明有清晰起点。", "列表、表格、配置项、弹窗按钮区、规则说明页。", ("soc-interaction-design-principles.md", "figma-patterns.md")),
    PageProfile("contrast", "SOC 原则：主次对比", "交互原则", 5, "让当前、可操作、危险、成功、失败、推荐与禁用状态被快速区分。", "购买、消耗、领奖、队伍操作、权限提示、状态切换。", ("soc-interaction-design-principles.md", "prompt-system-spec.md")),
    PageProfile("repetition", "SOC 原则：模式重复", "交互原则", 6, "让同类系统复用相同结构、命名、状态和反馈，减少每个界面重新学习。", "活动入口、奖励卡、任务行、成员行、物品卡、筛选器。", ("soc-common-components-catalog.md", "figma-node-naming-spec.md")),
    PageProfile("direct", "SOC 原则：直截了当", "交互原则", 7, "让用户直接完成目标，避免用解释、跳转和多余确认掩盖交互不清。", "领取、装备、购买、筛选、改名、加入队伍等短路径任务。", ("soc-interaction-design-principles.md", "interaction-document-template-spec.md")),
    PageProfile("stay", "SOC 原则：保持上下文", "交互原则", 8, "能在当前场景解决的查看、选择和轻编辑，不强行跳到独立大页面。", "列表详情、轻量配置、局内提示、活动规则和奖励预览。", ("interface-layering-spec.md", "prompt-system-spec.md")),
    PageProfile("lightweight", "SOC 原则：降低操作负担", "交互原则", 9, "把高频操作放在对象附近，降低移动距离、记忆负担和跨端操作成本。", "PC 鼠标、移动触控、手柄焦点与 HUD 高频入口。", ("interface-layering-spec.md", "figma-patterns.md")),
    PageProfile("invitation", "SOC 原则：提供操作邀请", "交互原则", 10, "让可拖拽、可展开、可领取、可编辑、可查看的对象在操作前就可感知。", "新手引导之外的常规可发现性设计。", ("prompt-system-spec.md", "soc-common-components-catalog.md")),
    PageProfile("transition", "SOC 原则：过渡解释变化", "交互原则", 11, "用动效解释新增、消失、切换、获得、消耗和位置变化，而不是单纯装饰。", "奖励入包、列表刷新、弹层开合、页面切换、局内状态变化。", ("interface-layering-spec.md", "prompt-system-spec.md")),
    PageProfile("reaction", "SOC 原则：即时反馈", "交互原则", 12, "让每一次点击、提交、失败、冷却、等待和成功都有合适强度的反馈。", "Toast、持续提示、错误码、加载、领奖和强结果页。", ("prompt-system-spec.md", "interface-layering-spec.md")),
    PageProfile("colors", "SOC 全局样式：色彩", "全局样式", 13, "把色彩用于信息层级、状态、风险和反馈，不让单次页面随意定义功能色。", "成功/失败/警告/稀有度/可领取/禁用等状态色。", ("typography-color-spec.md", "soc-interaction-design-principles.md")),
    PageProfile("layout", "SOC 全局样式：布局", "全局样式", 14, "用稳定网格、模块间距和安全区规则承载双端适配与高密度内容。", "全屏界面、半屏层、弹窗、HUD、宽屏和移动转 PC。", ("fullscreen-framework-translation.md", "interface-layering-spec.md")),
    PageProfile("font", "SOC 全局样式：字体", "全局样式", 15, "让字号、字重、行高和颜色服务可读性、主次和本地化扩展。", "标题、按钮、规则说明、数值、状态标签和多语言文本。", ("typography-color-spec.md", "multilingual-spec.md")),
    PageProfile("icon", "SOC 全局样式：图标", "全局样式", 16, "图标必须解释对象、操作或状态，并能在 PC/移动端被识别。", "工具按钮、资源图标、状态标识、导航入口和空状态。", ("soc-common-components-catalog.md", "figma-patterns.md")),
    PageProfile("illustration", "SOC 全局样式：图形化", "全局样式", 17, "用图形化承载空、异常、引导和规则解释，不替代关键信息。", "空状态、异常页、教程、活动说明和系统入口。", ("figma-patterns.md", "multilingual-spec.md")),
    PageProfile("motion", "SOC 全局样式：动效", "全局样式", 18, "动效用于状态理解、上下文连续和等待感控制，优先性能与节奏。", "页面切换、弹层、奖励、Loading、HUD 和局内反馈。", ("interface-layering-spec.md", "prompt-system-spec.md")),
    PageProfile("dark", "SOC 全局样式：暗色场景", "全局样式", 19, "在暗色、半透明和局内环境中保持文字、状态和交互热区可读。", "局内 HUD、夜间场景、遮罩层、弹窗压暗和视频背景。", ("typography-color-spec.md", "interface-layering-spec.md")),
    PageProfile("visual", "SOC 全局样式：数据可视化", "全局样式", 20, "先判断用户要看趋势、对比、分布、占比还是异常，再选择图形。", "战绩、排行、经济、活动统计、队伍贡献和系统监控。", ("soc-figma-visual-interface-inventory.md", "multilingual-spec.md")),
    PageProfile("shadow", "SOC 全局样式：层级阴影", "全局样式", 21, "阴影和遮罩用于表达层级、浮起、可拖拽和阻断关系。", "弹窗、浮层、Tooltip、拖拽、卡片和半屏覆盖层。", ("interface-layering-spec.md", "figma-patterns.md")),
    PageProfile("buttons", "SOC 规则：按钮", "通用规则", 22, "按钮表达命令、风险、主次和归属，一个区域最多一个主操作。", "购买、确认、取消、删除、领取、返回、批量操作。", ("soc-common-components-catalog.md", "multilingual-spec.md")),
    PageProfile("feedback", "SOC 规则：反馈", "通用规则", 23, "按重要性、持续时间、打断程度和所在层级选择反馈，而不是统一做强弹窗。", "通用提示、错误、奖励、成就、持续目标和加载。", ("prompt-system-spec.md", "interface-layering-spec.md")),
    PageProfile("navigation", "SOC 规则：导航", "通用规则", 24, "导航回答当前位置、可去位置和返回路径，复杂流程要展示阶段。", "大厅系统、活动、商城、背包、设置、局内回退和 PC 快捷键。", ("fullscreen-framework-translation.md", "interface-layering-spec.md")),
    PageProfile("data-entry", "SOC 规则：输入与配置", "通用规则", 25, "输入前给格式、范围和默认值，输入中校验，输入后说明结果和失败原因。", "改名、搜索、筛选、创建队伍、公会公告、配置表单。", ("multilingual-spec.md", "soc-common-components-catalog.md")),
    PageProfile("data-display", "SOC 规则：信息展示", "通用规则", 26, "按识别对象、比较差异和推进操作的需求组织展示密度。", "物品、成员、任务、奖励、排行、战绩和状态卡。", ("soc-common-components-catalog.md", "soc-interface-inventory.md")),
    PageProfile("data-format", "SOC 规则：数据格式", "通用规则", 27, "数值、单位、时间、百分比和敏感信息必须有统一格式和本地化规则。", "货币、资源、倒计时、排行、进度、价格和概率。", ("multilingual-spec.md", "typography-color-spec.md")),
    PageProfile("copywriting", "SOC 规则：文案", "通用规则", 28, "文案从用户目标出发，保持术语一致、错误友好、可翻译和可配置。", "按钮、弹窗、Toast、规则说明、空状态、错误和本地化术语。", ("multilingual-spec.md", "prompt-system-spec.md")),
    PageProfile("data-list", "SOC 页面模式：列表", "页面模式", 29, "列表要支持识别、筛选、排序、批量、详情返回和局部失败。", "好友、成员、公会、物品、任务、邮件、服务器和活动列表。", ("soc-common-components-catalog.md", "soc-interface-inventory.md")),
    PageProfile("detail-page", "SOC 页面模式：详情页", "页面模式", 30, "详情页要说明对象身份、状态、关键数据、可做动作和来源返回。", "物品详情、队伍详情、活动详情、任务详情、规则说明。", ("soc-interface-inventory.md", "interaction-document-template-spec.md")),
    PageProfile("cases", "SOC 页面模式：实践案例", "页面模式", 31, "把已验证的界面经验沉淀成可复用案例，不只截图留档。", "从 Figma、交互稿和已上线系统抽取设计模式。", ("soc-interface-inventory.md", "soc-figma-visual-interface-inventory.md")),
    PageProfile("research-overview", "SOC 探索模式：概览", "页面模式", 32, "用探索页模板整理复杂系统的入口、任务、状态和异常。", "尚未形成正式规范的新系统探索。", ("contracts.md", "checklists.md")),
    PageProfile("research-form", "SOC 探索模式：表单页", "页面模式", 33, "把复杂配置拆成可理解的字段、分组、校验、保存和回退机制。", "创建、设置、导入、公告、权限、活动配置。", ("multilingual-spec.md", "soc-common-components-catalog.md")),
    PageProfile("research-workbench", "SOC 探索模式：工作台", "页面模式", 34, "工作台优先暴露待处理事项、核心状态、高频入口和异常提醒。", "大厅首页、管理台、模式入口、活动聚合和运营配置。", ("soc-interface-inventory.md", "prompt-system-spec.md")),
    PageProfile("research-list", "SOC 探索模式：列表页", "页面模式", 35, "列表页要让用户快速定位对象、比较状态并进入下一步操作。", "高数据量或高频操作的对象管理页。", ("soc-common-components-catalog.md", "multilingual-spec.md")),
    PageProfile("research-result", "SOC 探索模式：结果页", "页面模式", 36, "结果页只用于强结果或信息量大的流程结束，并给清楚的下一步。", "结算、抽奖、购买成功、提交完成和任务完成。", ("prompt-system-spec.md", "interface-layering-spec.md")),
    PageProfile("research-empty", "SOC 探索模式：空状态", "页面模式", 37, "空状态说明为什么空，并按场景给下一步，不把所有空都做成营销入口。", "搜索无结果、列表无数据、权限为空、完成型空状态。", ("multilingual-spec.md", "prompt-system-spec.md")),
    PageProfile("research-exception", "SOC 探索模式：异常页", "页面模式", 38, "异常页说明发生什么、影响范围、是否可重试和是否能返回。", "网络错误、权限不足、资源缺失、局部加载失败。", ("prompt-system-spec.md", "interface-layering-spec.md")),
    PageProfile("research-message-and-feedback", "SOC 探索模式：消息与反馈", "页面模式", 39, "消息与反馈要按队列、优先级、时长、打断和恢复逻辑设计。", "Toast、强提示、侧弹窗、持续提示、奖励和引导。", ("prompt-system-spec.md", "checklists.md")),
    PageProfile("research-navigation", "SOC 探索模式：导航", "页面模式", 40, "导航探索要验证深层路径、返回、跨系统入口和 PC 快捷键。", "大厅、商城、背包、地图、活动和设置等复杂路径。", ("fullscreen-framework-translation.md", "interface-layering-spec.md")),
    PageProfile("visualization-page", "SOC 页面模式：可视化页", "页面模式", 41, "可视化页先定义读图任务，再定义图表、筛选、单位和异常状态。", "战绩、排行、统计、经济、活动数据和运营看板。", ("soc-figma-visual-interface-inventory.md", "multilingual-spec.md")),
]


GROUP_INTRO = {
    "设计语言总览": "这一组定义 SOC 设计语言的总体结构：价值观、原则地图、阅读顺序和维护方式。",
    "交互原则": "这一组把 Ant Design 的底层交互原则转译到 SOC 的游戏 UI、双端操作和 FGUI 落地语境。",
    "全局样式": "这一组约束跨界面复用的视觉语言，重点是信息表达、状态一致和多语言可扩展。",
    "通用规则": "这一组面向高频组件和行为规则，帮助设计稿在按钮、反馈、导航、输入、展示和文案上保持一致。",
    "页面模式": "这一组沉淀常见页面类型，帮助新系统直接从可复用结构开始，而不是重新发明页面。",
}


GROUP_REQUIREMENTS = {
    "设计语言总览": (
        "先确认页面目标、用户角色、所在场景和非目标。",
        "把 Ant 的结构化判断转为 SOC 的交互稿检查项。",
        "每次新增规则都要写清适用范围和不适用范围。",
    ),
    "交互原则": (
        "说明原则作用于信息结构、操作路径、反馈还是状态表达。",
        "给出 PC、移动端或手柄场景下的差异判断。",
        "如果原则会影响 FGUI 节点、层级或组件复用，要写进交付备注。",
    ),
    "全局样式": (
        "先说明样式服务的信息目的，不先讨论装饰。",
        "明确状态色、字号、图标、动效和阴影是否已有规范来源。",
        "检查多语言、宽屏、暗色场景和性能边界。",
    ),
    "通用规则": (
        "写清默认、悬停、按下、禁用、加载、成功、失败和无权限状态。",
        "写清操作前邀请、操作中反馈、操作后结果。",
        "写清组件复用、提示选型、配置字段和术语来源。",
    ),
    "页面模式": (
        "先定义页面要帮助用户完成的任务，而不是先选卡片、表格或弹窗。",
        "覆盖默认、空、加载、错误、无权限、局部失败和完成状态。",
        "保留来源返回、筛选状态、跳转路径和下一步操作。",
    ),
}


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    if not match:
        return {}, raw
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, match.group(2)


def extract_headings(raw: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    in_code = False
    for line in raw.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if match:
            title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
            if title:
                headings.append((len(match.group(1)), title))
    return headings


def ant_page_url(slug: str) -> str:
    return f"https://ant.design/docs/spec/{slug}-cn/"


def ant_source_url(slug: str) -> str:
    return (
        "https://github.com/ant-design/ant-design/blob/"
        f"{ANT_COMMIT}/docs/spec/{slug}.zh-CN.md"
    )


def frontmatter_for(profile: PageProfile, source_title: str) -> str:
    related = "\n".join(f"  - {item}" for item in profile.related)
    return (
        "---\n"
        f"id: soc-design-language/{profile.slug}\n"
        f"title: {profile.title}\n"
        f"group: {profile.group}\n"
        f"order: {profile.order}\n"
        f"sourceFile: {profile.slug}.zh-CN.md\n"
        f"sourceTitle: {source_title}\n"
        f"sourcePage: {ant_page_url(profile.slug)}\n"
        f"sourceMarkdown: {ant_source_url(profile.slug)}\n"
        "related:\n"
        f"{related}\n"
        "---\n"
    )


def section_copy(profile: PageProfile, heading: str, index: int) -> str:
    requirements = GROUP_REQUIREMENTS[profile.group]
    return f"""## {heading}

这一节在 SOC 中用于落到“{profile.focus}”。它不复刻 Ant Design 的企业后台描述，而是保留原有章节位置，把判断对象替换为 SOC 的游戏 UI、Figma 交互稿、FGUI 拼接和双端适配。

### SOC 改写

- 当前要解决的场景：{profile.scenario}
- 设计稿需要先说明这个章节影响的是入口、信息结构、状态、反馈、文案、层级还是交付备注。
- 如果本节规则与已有专项规范冲突，优先采用 SOC 已沉淀的专项规范，并在本页记录差异来源。

### 交付要求

- {requirements[0]}
- {requirements[1]}
- {requirements[2]}
- 页面或组件如果会重复出现，要同步沉淀为组件规则、提示规则、层级规则或文案规则。

### 待补 SOC 案例

> 待补充 SOC 案例 / Figma 截图：建议补一个正例和一个反例。正例说明规则如何降低理解成本，反例说明缺少该规则会造成什么误读、重复操作或落地风险。
"""


def fallback_sections(profile: PageProfile) -> str:
    return f"""## 核心判断

{profile.focus}

### 设计时先问

- 当前用户是谁，正在完成什么任务？
- 信息、操作和反馈分别服务哪一个目标？
- 是否已有 SOC 组件、提示、层级或文案规则可复用？

## SOC 落地规则

{section_copy(profile, "结构与行为", 0)}
"""


def build_doc(profile: PageProfile) -> tuple[str, dict[str, object]]:
    source = RAW_ANT_DIR / f"{profile.slug}.zh-CN.md"
    raw = source.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    source_title = meta.get("title") or profile.slug
    headings = extract_headings(body)
    h2_headings = [title for level, title in headings if level == 2]
    if not h2_headings:
        h2_headings = ["核心判断", "SOC 落地规则", "交付检查"]

    md = [
        frontmatter_for(profile, source_title),
        f"# {profile.title}",
        "",
        f"> 本页以 Ant Design《{source_title}》的章节结构为骨架，关键描述已替换为 SOC UXD 的项目语境。页面给人阅读；同名 Markdown 给 AI 和维护者作为可检索知识源。",
        "",
        "## 本页定位",
        "",
        f"{GROUP_INTRO[profile.group]}本页聚焦：{profile.focus}",
        "",
        "### 适用场景",
        "",
        f"- {profile.scenario}",
        "- 新交互稿评审、Figma 草稿生成、AI 交互文档生成和旧界面重构都可以引用本页。",
        "- 若遇到更具体的专项规范，以专项规范为准；本页负责提供底层判断和目录定位。",
        "",
        "### 不适用场景",
        "",
        "- 不直接规定最终视觉风格、商业活动皮肤或一次性运营包装。",
        "- 不替代策划规则、数值配置、程序接口和 GUI 资产验收。",
        "",
        "## 原结构映射",
        "",
        "| Ant 原章节 | SOC 改写用途 |",
        "| --- | --- |",
    ]
    for heading in h2_headings:
        md.append(f"| {heading} | 用 SOC 场景重写该章节的设计判断、交付要求和案例占位。 |")
    md.append("")

    if h2_headings:
        for index, heading in enumerate(h2_headings):
            md.append(section_copy(profile, heading, index))
    else:
        md.append(fallback_sections(profile))

    md.extend(
        [
            "## 交付检查",
            "",
            "- [ ] 页面目标、入口、返回、关闭、取消和异常路径已经写清。",
            "- [ ] 默认、空、加载、错误、无权限、禁用、完成和局部失败状态已经覆盖。",
            "- [ ] PC / 移动 / 手柄差异已经标注，尤其是热区、悬停、快捷键和焦点规则。",
            "- [ ] 文案已检查术语一致、多语言扩展、变量、富文本和文本膨胀。",
            "- [ ] 涉及反馈时已映射到提示系统；涉及层级时已映射到界面层级规范。",
            "- [ ] 可复用模式已经回写到知识库或组件规则，不只留在单个页面。",
            "",
            "## 参考文档",
            "",
            f"- [Ant Design 原页面：《{source_title}》]({ant_page_url(profile.slug)})",
            f"- [Ant Design 原始 Markdown：`{profile.slug}.zh-CN.md`]({ant_source_url(profile.slug)})",
        ]
    )
    for item in profile.related:
        md.append(f"- SOC 内部参考：`references/{item}`")
    md.append("")

    content = "\n".join(md).replace("\n\n\n", "\n\n")
    manifest_entry = {
        "slug": profile.slug,
        "title": profile.title,
        "group": profile.group,
        "order": profile.order,
        "sourceFile": f"{profile.slug}.zh-CN.md",
        "sourceTitle": source_title,
        "sourcePageUrl": ant_page_url(profile.slug),
        "sourceMdUrl": ant_source_url(profile.slug),
        "related": list(profile.related),
    }
    return content, manifest_entry


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, object]] = []
    total_lines = 0
    for profile in PAGE_PROFILES:
        content, entry = build_doc(profile)
        (OUT_DIR / f"{profile.slug}.md").write_text(content, encoding="utf-8")
        entry["lines"] = len(content.splitlines())
        pages.append(entry)
        total_lines += int(entry["lines"])

    manifest = {
        "id": "soc-design-language",
        "title": "SOC 设计语言目录",
        "summary": "基于 Ant Design 设计语言结构重写的 SOC UXD 设计原则、全局样式、通用规则和页面模式目录。",
        "source": {
            "name": "Ant Design docs/spec",
            "commit": ANT_COMMIT,
            "rawDir": str(RAW_ANT_DIR),
            "sourceRecord": str(WORKSPACE / "external-references" / "ant-design-spec" / "SOURCE.md"),
        },
        "groups": list(GROUP_INTRO.keys()),
        "pageCount": len(pages),
        "lines": total_lines,
        "pages": pages,
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"generated {len(pages)} SOC design language docs into {OUT_DIR}")


if __name__ == "__main__":
    main()
