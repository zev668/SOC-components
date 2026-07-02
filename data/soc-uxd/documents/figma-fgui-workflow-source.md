---
docId: "figma-fgui-workflow-source"
title: "Figma 转 FGUI 工作流整合说明"
sourceFile: "Figma转FGUI工作流整合说明.md"
sourceType: "md"
publishStatus: "converted"
ingestMode: "archival"
updatedAt: "2026-07-02"
topics: ["Figma 到 FGUI 工作流", "交付落地"]
---

# Figma 转 FGUI 工作流整合说明

## 文档身份
- 原始文件：Figma转FGUI工作流整合说明.md
- 文档类型：md
- 所属模块：Figma 到 FGUI 工作流、交付落地
- 状态：converted
- 入库模式：资料归档优先

## 资料摘要

Figma 转 FGUI 工作流整合说明 更新时间：2026-06-25 结论先行 Figma 转 FGUI 不是把 Figma 节点直接交给 AI 一步生成 XML，而是走一条带中间表示和校验闭环的流水线： 核心对应方式是： Figma 的节点树先被导出为 figma-raw.json。 Raw 再由确定性脚本转成...

## 原文结构转写

- Figma 转 FGUI 工作流整合说明
- 1. 结论先行
- 2. 本文整合来源
- 3. 总体职责划分
- 4. Figma 文档应该怎么写
- 4.1 根节点命名
- 4.2 节点命名协议
- 4.3 类型前缀对应关系
- 4.4 无前缀时的类型推断
- 5. Figma 与 FGUI 的核心对应关系
- 5.1 概念对应
- 5.2 属性对应
- 5.2.1 几何与层级属性
- 5.2.2 布局与响应式属性
- 5.2.3 视觉样式属性
- 5.2.4 图像、图形与矢量
- 5.2.5 文本属性
- 5.2.6 组件、状态与复用
- 5.2.7 交互、原型与动效
- 5.2.8 资源、样式、变量与发布
- 5.2.9 不建议直接映射的 Figma 能力
- 5.3 Constraints 到 Relations
- 6. IR 是怎么表达 FGUI 的
- 7. 各阶段如何转换
- 7.1 `f2f-create`：Figma 到 Raw，再到 IR
- 7.2 `f2f-checktree`：人工校树
- 7.3 `f2f-tasks`：IR 到任务清单
- 7.4 `f2f-apply`：任务清单到 FGUI XML
- 7.5 `fairygui-generator`：真正写 FGUI 文件
- 8. FGUI XML 里最终怎么落
- 8.1 包体
- 8.2 组件根节点
- 8.3 displayList 节点
- 8.4 节点类型落点
- 9. ID 映射如何保证增量稳定
- 10. 校验和修复怎么做
- 11. 手动和自动两种使用方式
- 11.1 手动流程
- 11.2 自动流程
- 11.3 从中间阶段重跑

## 明确规则 / 决策

- 导出的 Figma 起始节点必须带包名：
- 扩展型控件在 FairyGUI 里本质上仍是组件资源，只是组件根节点带 `extention`，并带对应扩展标签，例如 `<Button>`、`<Label>`。
- | Layer name | name | 作为逻辑访问名，建议稳定且不重复 |
- | Variants | Controller | 需要按状态规则重建 |
- | Prototype interaction | Controller / Transition / 运行时代码 | 不直接照搬，需要转真实交互逻辑 |
- | 缺口 | 当前没有可靠字段、脚本规则或专门 skill，需要后续开发。 |
- | 不转 | 不建议进入 FGUI 运行时，通常忽略或只作为报告信息。 |
- | X / Y | Position | 直映 | 写入 IR `props.x/y`，生成 XML `xy="x,y"`，落地前取整数。 | 已有：`f2f-create` 字段映射 + `fairygui-generator` displayList 规则。 | 需要补齐小数取整策略的统一测试。 |
- | Width / Height | Size | 直映 | 写入 IR `props.width/height`，生成 XML `size="w,h"`。 | 已有：`f2f-create` 字段映射 + `fairygui-generator`。 | 需要补齐 0 尺寸、负尺寸、浮点误差的诊断规则。 |
- | Rotation | Rotation | 近似 | 写入 IR `props.rotation`，生成 XML `rotation`。 | 已有：`f2f-create` 直接复制 rotation。 | 需确认 Figma 与 FGUI 正角度方向是否需要取反；当前规则未做符号转换。 |
- | Visible / Hidden | Invisible | 直映 | 写入 IR `props.visible`，生成 XML `visible`。 | 已有：`f2f-create` 字段映射。 | 需要定义 Figma 隐藏父节点时子树是否仍生成。 |
- | Clip content | Overflow handling: hide | 直映 | `clipsContent=true` 写入 `props.overflow=hidden`，组件 XML `overflow="hidden"`。 | 已有：`f2f-create` 字段映射。 | 需要区分 Frame 裁剪与滚动区域。 |

## 案例经验

以下保留原文主体，供 AI 检索和人工回溯。

## 待确认 / AI 推论

- | 阶段管理 | `f2f-stage` | 模块名、阶段名 | `.f2f/{module}/task.md` | 初始化、创建模块、标记阶段完成、获取后续阶段 |
- 本节把 `figma-fgui-property-mapping.md` 中的映射项全部并入，并额外补充“当前支撑”和“缺口”。后续如果要补齐转换能力，可以直接按 `缺口/待开发` 列拆 skill 或 converter 规则。
- | 缺口 | 当前没有可靠字段、脚本规则或专门 skill，需要后续开发。 |
- | Prototype flow | 运行时代码 / 页面跳转逻辑 | 重构 | 不直接生成 UI XML，转运行时代码或需求备注。 | 缺口。 | 后续如需转代码，新增 route/action skill。 |
- `exist` 表示目标资源在本地 FGUI assets 中是否已存在，决定后续任务是 `new` 还是 `modify`。

## 检索关键词

1. 结论先行、2. 本文整合来源、3. 总体职责划分、4. Figma 文档应该怎么写、4.1 根节点命名、4.2 节点命名协议、4.3 类型前缀对应关系、Figma 到 FGUI 工作流、Figma 转 FGUI 工作流整合说明、交付落地

## 来源定位

- 文件：Figma转FGUI工作流整合说明.md
- 位置：按原文标题和段落回溯。

---

## 原文主体

# Figma 转 FGUI 工作流整合说明

更新时间：2026-06-25

## 1. 结论先行

Figma 转 FGUI 不是把 Figma 节点直接交给 AI 一步生成 XML，而是走一条带中间表示和校验闭环的流水线：

```text
Figma Design URL
  -> Figma Raw JSON
  -> FGUI IR JSON
  -> ui-generate-tasks.xml
  -> fairygui-generator 生成/修改 FGUI XML
  -> id-map.json + 校验/修复
```

核心对应方式是：

- Figma 的节点树先被导出为 `figma-raw.json`。
- Raw 再由确定性脚本转成 `fgui-ir.json`，IR 中保存组件、子节点、资源引用、属性、关系和备注。
- IR 再拆成按依赖拓扑排序的生产任务 `ui-generate-tasks.xml`。
- `f2f-apply` 逐个任务装配 prompt，调用 `fairygui-generator` 生成或修改 FairyGUI 的 `package.xml` 与组件 XML。
- `id-map.json` 保存 `semanticId -> FGUI nodeId`，保证增量修改时节点 ID 稳定。

一句话：通过“确定性脚本 + IR 中间层 + 任务清单 + generator 子代理 + 校验修复闭环”完成转换，而不是靠 AI 直接猜 XML。

## 2. 本文整合来源

本文整合了以下材料：

- `figma-fgui-property-mapping.md`
- `基于AI的Figma到FGUI的工作流设计.md`
- 当前项目 `.codex/skills` 下的 f2f 技能体系：
  - `f2f-stage`
  - `f2f-create`
  - `f2f-checktree`
  - `f2f-tasks`
  - `f2f-apply`
  - `f2f-ff`
  - `f2f-implement`
  - `fairygui-generator`
  - `fairygui-resource-lookup`
  - `fairygui-ref-validator`
  - `figma-use`

口径说明：早期工作流文档中出现过 `.ff`、`tasks.xml`、`todo.md` 等命名；当前技能实现口径统一为 `.f2f`、`ui-generate-tasks.xml`、`task.md`。

## 3. 总体职责划分

| 阶段 | 负责技能 | 输入 | 输出 | 作用 |
|---|---|---|---|---|
| 阶段管理 | `f2f-stage` | 模块名、阶段名 | `.f2f/{module}/task.md` | 初始化、创建模块、标记阶段完成、获取后续阶段 |
| 设计导出与 IR 转换 | `f2f-create` | Figma URL 或 `figma-raw.json` | `figma-raw.json`、`fgui-ir.json` | 从 Figma 拉取节点树，并转成 FGUI 可消费的 IR |
| 结构审查 | `f2f-checktree` | `fgui-ir.json` | 更新后的 `fgui-ir.json`、`ui-tree.md`、`tree-modify.cmds` | 人工校准组件划分、节点结构、属性和备注 |
| 任务生成 | `f2f-tasks` | `fgui-ir.json` | `ui-generate-tasks.xml` | 按组件依赖生成拓扑有序的生产任务 |
| 组件生成 | `f2f-apply` | `ui-generate-tasks.xml` | FGUI XML、`id-map.json` | 调 generator 生成/修改组件，并执行校验修复 |
| XML 生产 | `fairygui-generator` | 单组件 prompt、idMap | `package.xml`、组件 XML | 按 FGUI 编辑器规则生成或修改包体与组件 |
| 资源查找 | `fairygui-resource-lookup` | assets 路径、资源 ID 或 `ui://` | 资源详情 | 判断资源是否存在、解析包名/资源名/ID |
| 引用校验 | `fairygui-ref-validator` | assets 路径、包体、组件 | 校验报告 | 检查 `src`、`pkg`、`ui://`、transition target 等是否合法 |
| 自动编排 | `f2f-ff` | 模块名、起始阶段 | 阶段执行报告 | 从指定阶段起自动跑完剩余阶段 |
| 端到端入口 | `f2f-implement` | Figma URL 或 raw 路径 | 全流程产物 | 等价于 `f2f-ff create <figma输入>` |

## 4. Figma 文档应该怎么写

### 4.1 根节点命名

导出的 Figma 起始节点必须带包名：

```text
UiLogin@LobbyLogin
type#UiLogin@LobbyLogin
UiLogin@LobbyLogin/UiLogin
```

含义：

- `UiLogin`：节点名，也是默认组件名。
- `LobbyLogin`：FairyGUI 包名，也会作为 `.f2f/{module}` 的模块名。
- 如果写成 `@包名/组件名`，则组件名以 `/` 后的名字为准。

子节点没有显式包名时，默认沿用根节点包名。

### 4.2 节点命名协议

标准格式：

```text
[类型前缀#]节点名称[@资源引用]
```

示例：

| Figma 节点名 | 含义 |
|---|---|
| `bg` | 无显式类型，按 Figma 节点类型推断 |
| `graph#background` | 生成图形节点 |
| `text#title` | 生成文本节点 |
| `img#icon@CommonGlobal/Icon_001` | 生成图片节点，引用指定资源 |
| `loader#avatar@AssetAvatar/Avatar001` | 生成加载器，引用指定资源 |
| `list#itemList@CommonGlobal/ComItem` | 生成列表，默认子项为 `ComItem` |
| `button#btnBuy@CommonGlobal/BtnBuy` | 生成按钮型组件 |
| `ignore#效果图` | 跳过该节点和子树 |

### 4.3 类型前缀对应关系

| 前缀 | FGUI 语义 | IR / XML 落点 | 是否支持资源引用 |
|---|---|---|---|
| 缺省 | 组件或自动推断 | `component` 或推断类型 | 是 |
| `ignore` | 忽略 | 不进入 IR | 否 |
| `graph` | 图形 | `<graph>` | 否 |
| `img` | 图片 | `<image>` | 是 |
| `loader` | 装载器 | `<loader>` | 是 |
| `text` | 普通文本 | `<text>` | 否 |
| `rich` | 富文本 | `<richtext>` | 否 |
| `list` | 列表 | `<list>` | 是，作为 `defaultItem` |
| `group` | 分组 | `<group>` | 否 |
| `label` | 标签扩展组件 | `component` + `extension=Label` | 是 |
| `button` | 按钮扩展组件 | `component` + `extension=Button` | 是 |
| `progress` | 进度条扩展组件 | `component` + `extension=ProgressBar` | 是 |
| `slider` | 滑动条扩展组件 | `component` + `extension=Slider` | 是 |
| `scrollbar` | 滚动条扩展组件 | `component` + `extension=ScrollBar` | 是 |
| `combobox` | 下拉框扩展组件 | `component` + `extension=ComboBox` | 是 |

扩展型控件在 FairyGUI 里本质上仍是组件资源，只是组件根节点带 `extention`，并带对应扩展标签，例如 `<Button>`、`<Label>`。

### 4.4 无前缀时的类型推断

| Figma type | 默认 elementType | 说明 |
|---|---|---|
| `TEXT` | `text` | 直接映射为文本 |
| `RECTANGLE` / `ELLIPSE` / `LINE` / `VECTOR` / `POLYGON` / `STAR` / `BOOLEAN_OPERATION` | `graph` | 简单几何体走图形 |
| `FRAME` / `COMPONENT` / `COMPONENT_SET` / `INSTANCE` / `SECTION` | `component` | 容器或组件 |
| `GROUP` | `group` | 分组 |
| `SLICE` | `image` | 切片/图片资源 |
| `DOCUMENT` / `PAGE` | 跳过 | 元层级不生成运行时节点 |

注意：如果节点有子节点且没有显式类型，优先按 `component` 处理。复杂矢量、布尔图形、多重填充、特殊描边等虽然可能被推断为 `graph`，但高保真落地通常更适合烘焙成图片资源。

## 5. Figma 与 FGUI 的核心对应关系

### 5.1 概念对应

| Figma 概念 | FGUI 概念 | 转换方式 |
|---|---|---|
| File | Project / 资源集合 | 不直接一一映射，按 UI 工程组织 |
| Page | Package 或设计组织 | 通常按模块拆成 FGUI 包 |
| Top-level Frame | Component / 界面根组件 | 生成 root component |
| Nested Frame | 子 Component / Group | 有复用、裁剪、状态时拆组件；纯组织可为 group |
| Layer hierarchy | displayList | 父子层级和同级顺序映射到显示列表 |
| Layer name | name | 作为逻辑访问名，建议稳定且不重复 |
| Constraints | Relation | 映射为相对父组件的 relation |
| Auto layout | GList / Relation / 手工坐标 | 列表型优先 GList，非列表需近似重构 |
| Component / Instance | FGUI component resource / component node | 资源存在则引用，不存在则新建 |
| Variants | Controller | 需要按状态规则重建 |
| Prototype interaction | Controller / Transition / 运行时代码 | 不直接照搬，需要转真实交互逻辑 |

### 5.2 属性对应

本节把 `figma-fgui-property-mapping.md` 中的映射项全部并入，并额外补充“当前支撑”和“缺口”。后续如果要补齐转换能力，可以直接按 `缺口/待开发` 列拆 skill 或 converter 规则。

支撑状态说明：

| 状态 | 含义 |
|---|---|
| 已有 | 现有 `f2f-create` / `f2f-tasks` / `f2f-apply` / `fairygui-generator` 已有明确字段、规则或生成能力。 |
| 部分 | 有基础字段或可通过 `comments` / `attrs` / `remark` 传递，但缺少稳定自动转换规则。 |
| 缺口 | 当前没有可靠字段、脚本规则或专门 skill，需要后续开发。 |
| 不转 | 不建议进入 FGUI 运行时，通常忽略或只作为报告信息。 |

#### 5.2.1 几何与层级属性

| Figma 设计属性 | FGUI 设计属性 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| X / Y | Position | 直映 | 写入 IR `props.x/y`，生成 XML `xy="x,y"`，落地前取整数。 | 已有：`f2f-create` 字段映射 + `fairygui-generator` displayList 规则。 | 需要补齐小数取整策略的统一测试。 |
| Width / Height | Size | 直映 | 写入 IR `props.width/height`，生成 XML `size="w,h"`。 | 已有：`f2f-create` 字段映射 + `fairygui-generator`。 | 需要补齐 0 尺寸、负尺寸、浮点误差的诊断规则。 |
| Min / Max size | smallest size / biggest size | 近似 | 作为组件尺寸限制或运行时布局约束处理。 | 缺口：IR schema 暂无 min/max 字段。 | 增加 raw 采集、IR `attrs` 标准字段，以及 generator 写入规则。 |
| Aspect ratio lock | Keep ratio | 近似 | 映射为 FGUI keep ratio 或图片/loader 的 aspect。 | 部分：`displaylist-nodes.md` 支持 `aspect`，但 create 未自动映射。 | 增加 Figma 比例锁采集和 `props/attrs.aspect` 规则。 |
| Scale | Scale | 直映 | 可写 XML `scale="sx,sy"`；UI 白模优先转 size。 | 部分：generator 支持 scale，共通属性有规则；IR 暂无 scale 标准字段。 | 增加 scale 采集、是否折算到 size 的策略开关。 |
| Rotation | Rotation | 近似 | 写入 IR `props.rotation`，生成 XML `rotation`。 | 已有：`f2f-create` 直接复制 rotation。 | 需确认 Figma 与 FGUI 正角度方向是否需要取反；当前规则未做符号转换。 |
| Pivot / transform origin | Axis / As anchor | 近似 | 映射为 XML `pivot` / `anchor`。 | 部分：generator 支持 `pivot`、`anchor`；IR 暂无标准字段。 | 增加 Figma transform origin 或推导规则，补 `props/attrs.pivot`。 |
| Opacity | Alpha | 直映 | Figma opacity 写入 IR `props.alpha`，生成 XML `alpha`。 | 已有：`f2f-create` 字段映射。 | 需区分对象 alpha 与单个 fill alpha 的合成策略。 |
| Visible / Hidden | Invisible | 直映 | 写入 IR `props.visible`，生成 XML `visible`。 | 已有：`f2f-create` 字段映射。 | 需要定义 Figma 隐藏父节点时子树是否仍生成。 |
| Lock layer | 编辑器锁定 | 无 | 不进入运行时。 | 不转。 | 可作为转换报告 warning，不生成 XML。 |
| Layer order | Display list order | 直映 | 按 Figma children 顺序生成组件 children，再生成 displayList 顺序。 | 已有：Raw skeleton 保留 childIds，tasks/apply 按 IR 顺序消费。 | 需补遮挡顺序回归测试。 |
| Absolute position in auto layout | 手工 Position / 脱离布局处理 | 近似 | 对脱离 Auto Layout 的节点保留 x/y，作为手工坐标。 | 部分：x/y 已有；Auto Layout 特例缺细规则。 | 增加 absolute-positioned child 的布局优先级规则。 |
| Clip content | Overflow handling: hide | 直映 | `clipsContent=true` 写入 `props.overflow=hidden`，组件 XML `overflow="hidden"`。 | 已有：`f2f-create` 字段映射。 | 需要区分 Frame 裁剪与滚动区域。 |
| Overflow scroll | Overflow handling: vertical / horizontal / free scroll | 直映 | 映射为 `overflow="scroll"` 或 ScrollPane 相关配置。 | 部分：`clipsContent=false` 可转 `scroll`；但 Figma 原型滚动行为未完整采集。 | 增加 scroll direction、scrollbar、clipSoftness、固定层拆分规则。 |

#### 5.2.2 布局与响应式属性

| Figma 属性/机制 | FGUI 属性/机制 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Constraints: Left | Relation: Left -> Left | 直映 | `horizontal=MIN` -> `left-left`。 | 已有：`figma-fgui-rules.md` constraints 映射。 | 补不同父级尺寸变化的验证用例。 |
| Constraints: Right | Relation: Right -> Right | 直映 | `horizontal=MAX` -> `right-right`。 | 已有。 | 同上。 |
| Constraints: Left and Right | Relation: Left + Right / Width | 近似 | `horizontal=STRETCH` -> `left-left,right-right`。 | 已有：保守 relation 输出。 | 需确认是否额外补 width-width 百分比关系。 |
| Constraints: Top | Relation: Top -> Top | 直映 | `vertical=MIN` -> `top-top`。 | 已有。 | 补验证用例。 |
| Constraints: Bottom | Relation: Bottom -> Bottom | 直映 | `vertical=MAX` -> `bottom-bottom`。 | 已有。 | 补验证用例。 |
| Constraints: Top and Bottom | Relation: Top + Bottom / Height | 近似 | `vertical=STRETCH` -> `top-top,bottom-bottom`。 | 已有：保守 relation 输出。 | 需确认是否额外补 height-height 百分比关系。 |
| Constraints: Center | Relation: Center / Middle | 近似 | `CENTER` -> `center-center` 或 `middle-middle`。 | 已有。 | 需保证初始坐标仍正确。 |
| Constraints: Scale | 百分比 Relation / Controller 百分比坐标 | 近似 | 当前保守映射为 left/top。 | 部分：规则里已保守降级。 | 开发百分比 relation 或运行时缩放策略。 |
| Auto layout: horizontal | List single row / horizontal flow / 手工 Relation | 近似 | 列表型转 GList 横向；普通容器转坐标、间距、relation。 | 部分：raw 采集 layout；缺稳定自动布局转换。 | 开发 layout-default skill：识别列表/工具栏/普通容器。 |
| Auto layout: vertical | List single column / vertical flow / 手工 Relation | 近似 | 列表、菜单、表单优先 GList；普通容器转坐标和 relation。 | 部分。 | 同上，补 vertical stack 到 GList/Group 的决策规则。 |
| Auto layout: wrap | List flow / pagination | 近似 | 转 `layout=flow_hz` / `flow_vt` 或分页列表。 | 缺口：IR 未标准化 wrap 输出。 | 增加 wrap、lineItemCount、lineGap、colGap 规则。 |
| Auto layout: grid | List flow / 自定义布局 | 重构 | 转 GList flow 或运行时自定义布局。 | 缺口。 | 需要专门 grid layout skill，支持行列、span、track resize。 |
| Padding | List / Component 内边距结构 | 近似 | 转容器内部坐标偏移、List padding 或保留为 attrs。 | 部分：raw 采集 padding；IR/XML 无统一规则。 | 补 `attrs.padding*`、List padding 或坐标折算规则。 |
| Gap between items | List line spacing / column gap / 手工间距 | 近似 | 列表写 `lineGap/colGap`；普通容器保持坐标。 | 部分：raw 采集 itemSpacing；generator 支持 list gap。 | 开发 Auto Layout gap -> list/group gap 规则。 |
| Alignment in auto layout | Aligned / Relation / List alignment | 近似 | 文本对齐、列表对齐和容器内对象对齐分开映射。 | 部分：文本 align 已有；list/container align 缺细则。 | 补 primary/counter axis align 到 list align / relation。 |
| Hug contents | Auto size / List autosize / 文本自动尺寸 | 近似 | 文本可转 autoSize；容器和 List 需按内容计算或保留固定尺寸。 | 部分：文本 autoSize 已有。 | 补容器 hug 的尺寸重算规则。 |
| Fill container | Relation Size / Width / Height | 近似 | 转跟随父级的 relation 或百分比尺寸。 | 部分：constraints stretch 已有；Auto Layout fill 缺规则。 | 补 layoutSizing FILL 到 relation 的映射。 |
| Layout guides | 无运行时等价 | 无 | 仅设计辅助，不生成。 | 不转。 | 可进入转换报告。 |

#### 5.2.3 视觉样式属性

| Figma 属性 | FGUI 属性 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Solid fill | Graph fill color / Image colour / Text colour | 直映 | `fills[0]` solid -> IR `props.color`，按节点类型生成 `fillColor/color`。 | 已有：`f2f-create` 采集首个 solid fill。 | 需补多 fill 选择优先级。 |
| Fill opacity | Alpha 或颜色 alpha | 近似 | 可合成到对象 alpha 或颜色 alpha。 | 部分：对象 opacity 已有；paint opacity 未完整映射。 | 定义 fill opacity 与 node opacity 的合成规则。 |
| Multiple fills | 多子节点叠加 / 烘焙图片 | 重构 | 拆多个图形/图片节点，或烘焙为图片资源。 | 缺口：当前只取首个 fill。 | 开发多填充展开/烘焙策略。 |
| Gradient fill | 图片资源 / 自定义 shader | 重构 | 导出位图或写 shader/自定义渲染。 | 缺口：raw 可采集 gradientStops，但 IR 无落地规则。 | 开发 gradient 烘焙 asset-export skill 或 shader 规范。 |
| Pattern fill | 图片资源 / 平铺图像 | 重构 | 简单 pattern 转 tile image；复杂 pattern 烘焙。 | 缺口。 | 补 pattern/image tile 规则。 |
| Image fill | Image / Loader URL | 近似 | 转资源引用，生成 `<image>` 或 `<loader>`。 | 部分：命名 `@资源` 已有；Figma imageHash 自动导出缺口。 | 开发 imageHash -> FGUI 资源导入/注册 skill。 |
| Video fill | MovieClip / Loader / 引擎侧视频 | 重构 | 转 movieclip、loader 或运行时视频组件。 | 缺口。 | 定义视频资源导出和运行时组件策略。 |
| Stroke color / weight | Graph line color / line size | 直映 | `strokes[0]` solid + `strokeWeight` -> `lineColor/lineSize`。 | 已有：`f2f-create` 字段映射。 | 补 stroke align、inside/outside 处理。 |
| Individual strokes | 拆分为多个 Graph 线条 | 重构 | 每边拆独立 graph 线条或烘焙。 | 缺口。 | 开发单边描边拆节点规则。 |
| Dashed stroke | 烘焙图片 / 自定义绘制 | 重构 | 烘焙或自定义绘制。 | 缺口。 | 增加 dashed stroke 资产化规则。 |
| Stroke caps / arrows | 额外图形节点 / 图片资源 | 重构 | 端点/箭头拆节点或切图。 | 缺口。 | 补 line cap、arrowhead 资源化规则。 |
| Variable width stroke | 图片 / 自定义矢量 | 重构 | 高级矢量描边通常烘焙。 | 缺口。 | 资产导出或自定义矢量组件。 |
| Corner radius | Graph fillet / 圆角矩形 | 近似 | 矩形 graph 写圆角；图片圆角需 mask/切图。 | 部分：`cornerRadius` 已进 IR；generator 需按 graph 写出。 | 补四角不等半径、图片圆角策略。 |
| Blend mode | BlendMode | 近似 | `ADD` -> `blend=add`，其他降级 none。 | 已有：`blendMode` 映射 add/none。 | 扩展 FGUI 支持的更多 blend mode。 |
| Layer blur / background blur | Filter / 烘焙 | 近似 | 简单 blur 转 filter，复杂背景 blur 烘焙。 | 缺口：IR 无 filter 字段。 | 增加 effects 采集与 filter/烘焙策略。 |
| Drop shadow | Filter / 文本 projection / 烘焙 | 近似 | 文本投影或滤镜；复杂阴影烘焙。 | 缺口。 | 增加 shadow -> projection/filter 规则。 |
| Inner shadow | 烘焙图片 / 自定义效果 | 重构 | 烘焙或自定义效果。 | 缺口。 | 资产化或 shader/filter 规则。 |
| Noise effect | 图片 / shader | 重构 | 资源化或 shader。 | 缺口。 | 增加 noise 烘焙/材质规则。 |
| Grayscale | Grayed / Color filter | 直映 | 映射为 `grayed` 或颜色滤镜。 | 部分：generator 支持 `grayed`；create 未自动采集。 | 需定义从 Figma effect/style 到 grayed 的判断规则。 |

#### 5.2.4 图像、图形与矢量

| Figma 属性/对象 | FGUI 属性/对象 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Rectangle | Graph Rectangle | 直映 | `RECTANGLE` -> IR `graphType=rect`，生成 `<graph type="rect">`。 | 已有：类型推断 + graphType。 | 补圆角、描边、填充组合测试。 |
| Ellipse | Graph Circle | 近似 | `ELLIPSE` -> IR `graphType=eclipse`，生成 `<graph type="eclipse">`。 | 已有：类型推断 + graphType。 | 确认椭圆尺寸与 FGUI graph 行为。 |
| Polygon / star | Graph Polygon / Regular Polygon | 近似 | 简单形状可转 graph，多点复杂形状建议烘焙。 | 部分：类型推断为 graph；缺具体 polygon attrs。 | 增加 polygon/star 点数、路径或烘焙规则。 |
| Vector network | Graph / 图片 / 自定义路径 | 重构 | 普通 graph 不覆盖完整 vector network，建议烘焙。 | 缺口。 | 开发 vector flatten/export asset skill。 |
| Boolean operations | 烘焙为图片或矢量资源 | 重构 | 转换前展平或导出图片。 | 缺口。 | 增加 boolean operation 展平/导出规则。 |
| Pencil / Draw illustrations | 图片资源 | 重构 | 作为图片资源导入 FGUI。 | 缺口。 | 增加插画节点导出和 package 注册规则。 |
| Image crop | 预裁切资源 / Loader fill processing | 近似 | 按策略转 loader fill 或预裁切。 | 缺口：当前无 crop 规则。 | 采集 imageScaleMode、cropTransform，映射 loader fill。 |
| Image fit / fill | Loader Fill processing | 近似 | Figma fit/fill -> FGUI loader `fill`。 | 部分：raw 采集 image scaleMode；IR 无标准字段。 | 补 scaleMode -> loader fill 映射表。 |
| Image smoothing | Allow smoothing | 直映 | 写 package image smoothing。 | 缺口。 | 资源注册时补 smoothing 字段。 |
| Nine-slice scaling | Scale 9 grid / Zoom with Nine Palace | 直映 | 写 image resource `scale="9grid"` + `scale9grid`。 | 部分：generator 支持 package image 字段；Figma 采集缺口。 | 补 9-slice 采集和资源注册规则。 |
| Tile image | Zoom using tiles / tile | 近似 | 写 image resource `scale="tile"` 或 loader tile。 | 部分：generator 支持 image resource 字段。 | 补 Figma tile/pattern 到 package image tile。 |
| Image tint | Image colour / Loader colour | 直映 | 颜色叠加写 image/loader `color`。 | 部分：solid color 已采集；tint 语义缺口。 | 定义 tint 与 fill/color 的优先级。 |
| Brightness | brightness | 直映 | 写 image/loader brightness。 | 缺口：IR 无 brightness 字段。 | 增加 brightness 采集和 XML 写入规则。 |
| Flip | Flip | 直映 | 写 FGUI flip。 | 缺口：IR 无 flip 字段。 | 增加 transform flip 判断和 XML 字段。 |

#### 5.2.5 文本属性

| Figma 文本属性 | FGUI 文本属性 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Text content | text / title | 直映 | 普通文本写 `<text text="...">`；Label/Button 可写 title。 | 已有：`props.text`。 | 补扩展组件 title 自动转写规则。 |
| Font family | font | 近似 | 写 `font`，动态字体需确保运行时可用；位图字体用资源 URL。 | 已有：`props.font` 采集 family。 | 补字体资源 lookup 与系统字体/位图字体策略。 |
| Font size | font size | 直映 | 写 `fontSize`。 | 已有：`props.fontSize`。 | 补混合字号处理。 |
| Font weight | bold / 字体资源 | 近似 | weight >= 600 或 style 含 Bold -> `bold`。 | 已有：`props.bold`。 | 补多字重字体资源映射。 |
| Italic | italic | 直映 | 写 `italic`。 | 缺口：IR schema 暂无 italic。 | 增加 text italic 采集和 generator 写入。 |
| Underline | underline | 直映 | 写 `underline`。 | 缺口。 | 增加 underline 采集和 XML 字段。 |
| Strikethrough | UBB / RichText / 自定义 | 近似 | 转 UBB/RichText 或自定义渲染。 | 缺口。 | 增加混排文本解析和 richtext 规则。 |
| Text color | colour | 直映 | 写 text `color`。 | 已有：solid fill -> `props.color`。 | 需区分文本 fill 和图形 fill。 |
| Line height | Line spacing | 近似 | Figma lineHeight 转 FGUI `leading`。 | 部分：raw 采集 lineHeight；IR schema 暂无 leading。 | 增加 lineHeight -> leading 公式。 |
| Letter spacing | Kerning | 近似 | 写 `letterSpacing`。 | 部分：raw 采集 letterSpacing；IR schema 暂无字段。 | 增加字段并标记 H5 支持风险。 |
| Horizontal alignment | Aligned | 直映 | `LEFT/CENTER/RIGHT` -> `left/center/right`。 | 已有：`props.align`。 | 无明显缺口。 |
| Vertical alignment | Aligned | 直映 | `TOP/CENTER/BOTTOM` -> `top/middle/bottom`。 | 已有：`props.vAlign`。 | 无明显缺口。 |
| Auto width | Auto size: Auto width and height | 近似 | `WIDTH_AND_HEIGHT` 可转自动宽高或 shrink。 | 部分：当前映射到 `autoSize`。 | 需确认 FGUI auto width/height 与现有 enum 的精确对应。 |
| Auto height / wrap | Auto size: Automatic height | 直映 | 固定宽度，自动增长高度，写 `autoSize=height`。 | 已有：`textAutoResize=HEIGHT` -> `height`。 | 补换行策略和固定宽度校验。 |
| Fixed size | Auto size: no | 直映 | 写 `autoSize=none`。 | 已有。 | 无明显缺口。 |
| Auto shrink | Auto size: Automatic shrink | 直映 | 写 `autoSize=shrink`。 | 已有：`WIDTH_AND_HEIGHT` 当前映射需确认。 | 校准 Figma auto resize 与 FGUI shrink。 |
| Single line | Single line | 直映 | 写 `singleLine`。 | 缺口：IR schema 暂无 singleLine。 | 增加单行判断和 XML 字段。 |
| Mixed text styles | UBB / RichText | 近似 | 复杂混排转 `richtext` 或 UBB。 | 缺口：raw 目前只采基础 text 字段。 | 采集 styled text segments，生成 richtext/UBB。 |
| Text stroke | Stroke | 直映 | 写 text `strokeColor/strokeSize`。 | 缺口：IR 无 text stroke 字段。 | 增加文本描边采集与 XML 写入。 |
| Text shadow | projection | 近似 | 转 FGUI projection 或滤镜。 | 缺口。 | 开发 text shadow -> projection 规则。 |
| Input text | GTextInput | 直映 | 生成 `<text input="true">` 或专用输入组件。 | 缺口：缺输入框识别规则。 | 增加 `input#` 类型前缀或 text attrs。 |
| Placeholder / input restrictions | GTextInput 设置 | 近似 | 写 `prompt`、限制规则等。 | 缺口。 | 增加 input placeholder、限制、键盘类型字段。 |

#### 5.2.6 组件、状态与复用

| Figma 属性/机制 | FGUI 属性/机制 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Component | Component resource / GComponent | 直映 | Figma 组件边界转 IR component，生成 FGUI component resource。 | 已有：组件平铺 + tasks/apply。 | 需补 Figma main component 与实例 override 的差异处理。 |
| Instance | Component instance | 近似 | 资源存在则生成 `<component src/fileName/pkg>`；override 转属性或备注。 | 部分：资源引用和存在性 lookup 已有。 | 增加 instance override 自动提取规则。 |
| Component set | Component + Controller | 近似 | variants 组合成 Controller pages。 | 缺口：当前没有 variant -> controller 自动规则。 | 开发 variant/controller skill。 |
| Variant property | Controller page / Controller value | 近似 | variant 属性值转 Controller 页。 | 缺口。 | 定义命名、pages、selected、gear 规则。 |
| Boolean component property | Display control / Controller | 近似 | 显隐布尔值转 controller display control。 | 缺口。 | 增加 boolean prop -> gearDisplay。 |
| Text component property | Text control | 近似 | 转子文本属性或 gearText。 | 缺口。 | 增加 text prop -> property/gearText。 |
| Instance swap property | Icon control / URL / 子组件替换 | 重构 | 转 loader/icon URL 或子组件替换规则。 | 缺口。 | 增加 swap prop -> resource URL/property。 |
| Exposed nested property | Export as component property | 近似 | 暴露子组件控制器作为组件属性。 | 缺口。 | 增加 exported nested prop 采集与 XML property。 |
| Interactive component | Controller + Button linkage + Transition | 近似 | 重建为 Button、Controller、Transition。 | 部分：button 前缀和 generator 支持 Button/Controller/Transition。 | 缺交互采集和自动状态机规则。 |
| Disabled state | Grayed / Touchable / Controller | 近似 | 转 `grayed`、`touchable=false` 或 controller 状态。 | 部分：generator 支持字段；无 Figma 状态规则。 | 定义 disabled 命名/variant 到 grayed 的规则。 |
| Button variants | GButton mode / selected state / Controller | 近似 | `button#` 生成 Button extension，状态由 controller/remark 补足。 | 部分：类型前缀支持 Button。 | 补 Common/Check/Radio、selected/down 状态自动规则。 |
| Slot | 子组件占位 / Graph placeholder | 近似 | 转空 graph、占位 component 或备注。 | 缺口。 | 定义 slot 命名协议和替换规则。 |
| Custom data | Custom data | 直映 | 写 XML `customData` 或 component `remark`。 | 部分：generator 支持 customData；IR 无标准字段。 | 增加 `attrs.customData` 标准化。 |

#### 5.2.7 交互、原型与动效

| Figma 原型/动效属性 | FGUI 对应机制 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Prototype flow | 运行时代码 / 页面跳转逻辑 | 重构 | 不直接生成 UI XML，转运行时代码或需求备注。 | 缺口。 | 后续如需转代码，新增 route/action skill。 |
| Trigger: click/tap | Button event / touch event | 近似 | 按钮事件由运行时代码绑定，或写 remark。 | 部分：Button 组件可生成；事件不生成。 | 增加事件备注或代码生成规则。 |
| Trigger: hover/press | Button state / Controller | 近似 | 转 Button 状态、Controller、Transition。 | 部分：generator 支持 Button/Transition。 | 需要 prototype interaction 采集。 |
| Navigate to frame | 打开 Component / Window / 切换页面 | 重构 | 转运行时代码，或在任务备注中说明。 | 缺口。 | 开发 navigation -> code/window 规则。 |
| Overlay | Window / Popup | 近似 | 转弹窗组件或 popup 行为。 | 缺口：UI 可生成，行为缺规则。 | 定义 overlay frame 到 Window/Popup 的命名协议。 |
| Back / close overlay | Window close / Popup hide | 近似 | 运行时代码或按钮事件。 | 缺口。 | 增加关闭行为元数据。 |
| Scroll behavior | ScrollPane | 直映 | 生成 scroll overflow 或 ScrollPane 结构。 | 部分：overflow 字段已有；方向/滚动条缺。 | 补 scroll direction、scrollbar、fixed children。 |
| Fixed objects in scroll | Relation / 独立层级 / sortingOrder | 近似 | 从滚动容器拆出固定层，或设置独立层级。 | 缺口。 | 增加 fixed-in-scroll 结构拆分规则。 |
| Smart animate | Transition | 近似 | 位移、缩放、透明度、旋转、颜色转 transition item。 | 部分：generator 支持 transition；无采集转换。 | 开发 Figma prototype animation -> transition。 |
| Dissolve / move in / push | Transition / 运行时代码 | 近似 | 简单动效转 Transition，页面切换转代码。 | 缺口。 | 同上。 |
| Animated GIF | MovieClip / Loader | 近似 | 转 movieclip 或 loader。 | 部分：generator 支持 movieclip。 | 增加 GIF 资源导入/注册规则。 |
| Video in prototype | 引擎侧视频组件 / 自定义 Loader | 重构 | 运行时视频组件承接。 | 缺口。 | 定义视频组件和代码绑定策略。 |
| Export animations | Transition / MovieClip / 外部视频 | 重构 | 区分运行时动效和导出视频。 | 缺口。 | 增加动画资产化或 transition 转换规则。 |
| State management for prototypes | Controller / 运行时状态 | 近似 | 静态状态转 Controller，业务状态转代码。 | 缺口。 | 开发状态模型/Controller 生成规则。 |

#### 5.2.8 资源、样式、变量与发布

| Figma 机制 | FGUI 机制 | 映射等级 | 转换方式 | 当前支撑 | 缺口/待开发 |
|---|---|---:|---|---|---|
| Color style | 资源规范 / 代码常量 / 默认属性 | 重构 | 可转项目色表、默认属性或代码常量。 | 缺口：当前只采节点实际颜色。 | 开发 style token 抽取和映射规则。 |
| Text style | 文本默认属性 / 代码生成规范 | 重构 | 转文本样式表或默认字段。 | 缺口。 | 开发 text style -> font preset。 |
| Effect style | 滤镜/烘焙规则 | 重构 | 转滤镜或烘焙。 | 缺口。 | 开发 effect style 规则。 |
| Layout guide style | 无运行时等价 | 无 | 不生成运行时 UI。 | 不转。 | 仅进入报告。 |
| Variables | Controller / Branch / 自定义配置 | 重构 | 颜色/文本/数字/布尔变量分别转配置、Controller 或代码。 | 缺口。 | 开发 variables -> config/controller 的分型规则。 |
| Variable modes | Branch / Controller pages / 配置表 | 重构 | 主题、多语言、平台差异转配置或分支。 | 缺口。 | 增加 mode 到主题/语言/平台分支策略。 |
| Library | Package / 跨包引用 | 近似 | Figma library 复用转 FGUI package 跨包引用。 | 部分：`@pack/resource` + lookup/ref-validator 已有。 | 补 Figma library component key 到包资源映射。 |
| Published component | Exported resource | 近似 | 跨包可访问资源需要 `exported=true`。 | 已有：`f2f-apply` 导出感知 + generator 定向 exported。 | 补更多资源类型 exported 检查。 |
| Import images | Resource library import | 直映 | 图片导入 FGUI 包并注册 package.xml。 | 部分：generator 能注册资源；Figma image 自动导出缺口。 | 开发 image asset export/import skill。 |
| Static export PNG/JPG/SVG/PDF | Publish / 资源导出 | 近似 | Figma export 是资产输出，FGUI publish 是运行时打包。 | 缺口：不属于当前 f2f 主流程。 | 增加资产导出和 publish 检查规则。 |
| Export scale | 高清资源 / @2x / 发布设置 | 近似 | 映射高清资源策略或发布设置。 | 缺口。 | 定义倍率、命名、图集配置。 |
| Atlas packing | Publish atlas settings | 直映 | FGUI publish atlas 配置。 | 部分：package.xml publish 结构有规则。 | 补图集归属、alone/atlas index 策略。 |
| i18n | i18n text export/import | 直映 | 文本导出翻译再加载，或标记静态多语言。 | 缺口：当前无自动 i18n 标记。 | 开发多语言标记规则，支持 remark -> XML/配置。 |
| Branching | Project branch | 近似 | Figma branch 是协作分支，FGUI branch 偏项目差异资源。 | 缺口。 | 作为工程流程规则，不建议进入组件转换。 |

#### 5.2.9 不建议直接映射的 Figma 能力

| Figma 能力 | 处理建议 | 当前支撑 | 缺口/待开发 |
|---|---|---|---|
| Comments | 忽略，或作为转换报告备注。 | 部分：checktree 支持 `comments` 字段，但不是 Figma 原生评论。 | 如要消费 Figma 评论，需新增评论采集规则。 |
| Multiplayer cursors / spotlight | 忽略。 | 不转。 | 无需开发。 |
| Viewer history | 忽略。 | 不转。 | 无需开发。 |
| Branch review | 忽略，或作为设计流程信息。 | 不转。 | 如需审计，可做流程报告，不进 XML。 |
| Canvas background color | 一般不进组件；如需要可转根背景。 | 缺口。 | 可增加根 Frame 背景生成策略。 |
| Layer lock | 仅编辑态信息，忽略。 | 不转。 | 无需开发。 |
| Layout guides | 仅设计辅助，忽略。 | 不转。 | 无需开发。 |
| Dev Mode inspect 信息 | 可辅助转换，但不是 UI 运行时属性。 | 不转。 | 可作为诊断输入，不进 XML。 |
| Figma AI / Agent 操作 | 不映射。 | 不转。 | 无需开发。 |

### 5.3 Constraints 到 Relations

只有父节点不是 Auto Layout 时，才把 Figma manual constraints 转成 FGUI relations。

| Figma horizontal | FGUI sidePair |
|---|---|
| `MIN` | `left-left` |
| `MAX` | `right-right` |
| `CENTER` | `center-center` |
| `STRETCH` | `left-left,right-right` |
| `SCALE` | `left-left`，保守近似 |

| Figma vertical | FGUI sidePair |
|---|---|
| `MIN` | `top-top` |
| `MAX` | `bottom-bottom` |
| `CENTER` | `middle-middle` |
| `STRETCH` | `top-top,bottom-bottom` |
| `SCALE` | `top-top`，保守近似 |

输出示例：

```json
{
  "target": "",
  "sidePair": "left-left,right-right,top-top"
}
```

`target=""` 表示目标是父组件。

## 6. IR 是怎么表达 FGUI 的

`fgui-ir.json` 是 Figma 到 FairyGUI 之间的中间层，它不直接等于 Figma 节点树，也不直接等于 FGUI XML，而是一个可审查、可调整、可生成任务的组件表。

核心结构：

```json
{
  "version": "1.0",
  "source": {
    "figmaUrl": "...",
    "extractedAt": "..."
  },
  "components": [],
  "rootCom": "ui://LobbyLogin/UiLogin"
}
```

每个 component：

```json
{
  "raw": "ui://LobbyLogin/UiLogin",
  "pkg": "LobbyLogin",
  "name": "UiLogin",
  "extension": "",
  "ref": [],
  "exist": false,
  "children": [],
  "comments": "可选备注"
}
```

每个 child：

```json
{
  "semanticId": "btn_buy",
  "name": "btnBuy",
  "elementType": "component",
  "extension": "Button",
  "props": {
    "x": 100,
    "y": 200,
    "width": 240,
    "height": 80,
    "res": "ui://CommonGlobal/BtnBuy",
    "sourceNodeId": "1:234"
  },
  "attrs": {},
  "relations": [],
  "children": [],
  "comments": "按钮有 normal/disabled 两个状态"
}
```

关键规则：

- `components` 是平铺组件表，不保留无限嵌套树。
- 每个 component 的 `children` 只保留直接子节点。
- 子组件通过 `props.res` 引用目标 component，而不是在父组件里嵌套完整后代。
- `ref` 是反向引用列表，用于生成依赖图。
- `exist` 表示目标资源在本地 FGUI assets 中是否已存在，决定后续任务是 `new` 还是 `modify`。
- `semanticId` 是跨阶段稳定识别节点的关键，不能依赖 `name` 做 ID 匹配。

## 7. 各阶段如何转换

### 7.1 `f2f-create`：Figma 到 Raw，再到 IR

输入：

```text
https://www.figma.com/design/{fileKey}/{fileName}?node-id={nodeId}
```

或：

```text
.f2f/{module}/figma-raw.json
```

执行方式：

1. 如果是 Figma URL，先通过 Figma MCP 的 `use_figma` 执行导出脚本。
2. 当前主路径使用 `skeleton-details` 分批传输：
   - skeleton 保存结构、父子关系、节点索引。
   - details 保存每个节点的坐标、尺寸、文本、填充、描边、布局等详情。
   - 每个批次带 checksum，避免长 JSON 被截断或转录出错。
3. 组装完整 raw tree，校验 schema、根节点包名、provenance、checksum。
4. 本地转换器把 raw 转成 `fgui-ir.json`。
5. 审计通过后标记 `create` 阶段完成。

主要产物：

```text
.f2f/{module}/figma-raw.json
.f2f/{module}/fgui-ir.json
.f2f/{module}/task.md
```

注意：

- 标准路径不使用完整大 JSON 直返。
- 标准路径不使用浏览器桥接、localhost FigmaAgent、平台 session log 或 `figma.io.write`。
- `transportTextBudget` 默认 18000，用来避开 `use_figma` 返回值约 20KB 的截断风险。

### 7.2 `f2f-checktree`：人工校树

作用：把机器转换出的 IR 渲染成可读节点树，让人检查组件划分和节点结构。

执行方式：

```text
fgui-ir.json + tree-modify.cmds -> 内存 IR -> ui-tree.md
```

人工可以通过自然语言调整：

- 删除、增加、移动、重命名节点。
- 修改节点属性或控件类型。
- 合并、拆分、删除、迁移组件。
- 给节点或组件追加 `comments` 备注。

脚本会把自然语言调整翻译成 DSL 命令，追加到：

```text
.f2f/{module}/tree-modify.cmds
```

然后在 `finalize` 时重放命令、校验 schema，并原子替换：

```text
.f2f/{module}/fgui-ir.json
```

重要语义：

- `fgui-ir.json` 是唯一真相。
- `tree-modify.cmds` 是唯一可变调整记录。
- `ui-tree.md` 只是派生视图，不应该手改。
- 自动流程中的 `checktree auto` 只重放历史命令，不进入人工调整循环。

### 7.3 `f2f-tasks`：IR 到任务清单

作用：从 IR 的组件引用关系中生成可生产的任务清单。

执行方式：

```text
fgui-ir.json -> 依赖 DAG -> 拓扑排序 -> ui-generate-tasks.xml
```

排序原则：

- 被依赖的组件先生成。
- 根组件最后生成。
- 同层使用稳定规则排序，避免每次生成任务顺序漂移。

任务结构：

```xml
<?xml version="1.0" encoding="utf-8"?>
<tasks>
  <produce>
    <task mapId="on" done="false">
      <target pack="LobbyLogin" com="UiLogin"/>
      <action type="new">
        <![CDATA[
          {
            "children": [
              {
                "semanticId": "btn_buy",
                "name": "btnBuy",
                "elementType": "component",
                "extension": "Button",
                "props": {},
                "attrs": {},
                "relations": [],
                "comments": "..."
              }
            ]
          }
        ]]>
      </action>
      <remark>人工备注或待解析说明</remark>
    </task>
  </produce>
  <verify>
    <!-- 用户自定义验证任务，重跑 tasks 时原样保留 -->
  </verify>
</tasks>
```

关键规则：

- `action type="new"`：目标 FGUI 资源不存在，需要新建。
- `action type="modify"`：目标 FGUI 资源已存在，需要修改。
- CDATA 中只保留单组件生产所需的瘦身 children。
- `<verify>` 块是用户可编辑的自定义验证区，重新生成任务时原样保留。
- 匿名 `ui://xxx` 引用会尝试用 `fairygui-resource-lookup` 解析；解析不了会在 `<remark>` 标 `[待解析]`，apply 时必须人工处理，不能猜。

### 7.4 `f2f-apply`：任务清单到 FGUI XML

作用：消费任务清单，驱动 `fairygui-generator` 按任务逐个生成或修改 FGUI 组件。

核心循环：

```text
next-task
  -> build-prompt
  -> fairygui-generator 子代理生成 XML
  -> verify-idmap
  -> mark-done
  -> validate
  -> insert-fix 最多 3 轮
  -> finalize
```

关键产物：

```text
.f2f/{module}/id-map.json
{assetsPath}/{pack}/package.xml
{assetsPath}/{pack}/Views/{UiXxx}.xml
{assetsPath}/{pack}/Coms/{ComXxx}.xml
```

目录规则：

- 组件名以 `ui` 开头，不区分大小写：输出到 `Views/`。
- 其他组件：输出到 `Coms/`。
- `.f2f/` 只保存流程数据，不能作为 FGUI XML 的产物目录。

强约束：

- 主代理不能自己手写、补全或修改组件 XML/package.xml 来完成 task。
- 生产组件必须走 `build-prompt -> fairygui-generator -> verify-idmap -> mark-done`。
- 非 `fairygui-generator` 根据本次 prompt 产出的 XML，不能作为 `mark-done` 的依据。

### 7.5 `fairygui-generator`：真正写 FGUI 文件

generator 负责按 FairyGUI 编辑器规则生成或修改：

- `package.xml`
- 组件 XML
- displayList 节点
- 控制器
- 扩展标签
- relation
- transition
- 资源引用

它生成后必须调用 `fairygui-ref-validator` 校验引用，不通过则修复，最多 3 次。

当上游提供 `idMap` 时，generator 必须走指定 ID 模式：

```json
{
  "idMap": {
    "btn_buy": "n0_ns5o",
    "title": "n1_ns5o"
  },
  "buildId": "v7qad38hns5o",
  "pkgId": "v7qad38h"
}
```

匹配规则：

- 用 `semanticId` 匹配 nodeId。
- 不依赖 `name`。
- 不自主调用 `nextNodeId` 分配节点 ID。

## 8. FGUI XML 里最终怎么落

### 8.1 包体

`package.xml` 根结构：

```xml
<?xml version="1.0" encoding="utf-8"?>
<packageDescription id="6xcg6ppw">
  <resources>
    <folder .../>
    <image .../>
    <component .../>
    <movieclip .../>
    <font .../>
  </resources>
  <publish>
    <atlas name="atlas0"/>
  </publish>
</packageDescription>
```

组件资源注册：

```xml
<component id="eqx54" name="UiLogin.xml" path="/Views/" exported="true"/>
<component id="abc12" name="ComItem.xml" path="/Coms/"/>
```

跨包引用需要目标资源 `exported="true"`。`f2f-apply` 会按资源引用情况生成导出指令，generator 只允许定向修改目标资源条目的 `exported` 属性。

### 8.2 组件根节点

组件 XML 根节点：

```xml
<component size="1920,1080" overflow="hidden" extention="Button">
  <displayList>
    ...
  </displayList>
</component>
```

常见属性：

| XML 属性 | 来源 |
|---|---|
| `size` | IR component/root 节点宽高 |
| `overflow` | `props.overflow` |
| `extention` | `extension`，例如 Button/Label/List |
| `pivot` | 轴点或人工备注推导 |
| `remark` | 人工备注或项目定制属性 |

### 8.3 displayList 节点

所有子节点都有共通属性：

```xml
<text id="n1_ns5o" name="title" xy="100,80" size="300,60" text="购买" fontSize="32"/>
```

共通字段：

| XML 属性 | 说明 |
|---|---|
| `id` | FGUI nodeId，来自 `id-map.json` |
| `name` | 逻辑节点名 |
| `xy` | 坐标，整数对 |
| `size` | 尺寸，整数对 |
| `rotation` | 旋转 |
| `alpha` | 透明度 |
| `visible` | 显隐 |
| `blend` | 混合模式 |

几何数值规则：

- `xy`、`size` 只能写整数对。
- Figma 浮点数要四舍五入。
- 接近 0 的科学计数法误差要写成 `0`。

### 8.4 节点类型落点

| IR elementType | FGUI XML 标签 | 关键字段 |
|---|---|---|
| `image` | `<image>` | `src`、`fileName`、`pkg`、`color` |
| `loader` | `<loader>` | `url`、`fill`、`align`、`vAlign` |
| `text` | `<text>` | `text`、`font`、`fontSize`、`color`、`align` |
| `richtext` | `<richtext>` | 富文本内容、UBB、尺寸限制 |
| `graph` | `<graph>` | `type`、`lineSize`、`lineColor`、`fillColor` |
| `component` | `<component>` | `src`、`fileName`、`pkg`、`controller` |
| `movieclip` | `<movieclip>` | `src`、`fileName`、`pkg`、`playing` |
| `list` | `<list>` | `layout`、`defaultItem`、`overflow`、`lineGap`、`colGap` |
| `group` | `<group>` | `layout`、`lineGap`、`excludeInvisibles` |

列表特殊规则：

- `elementType=list` 且 `props.res` 非空时，`props.res` 必须写入 `<list defaultItem="ui://...">`。
- 不能把 list 因为引用了组件资源就改成 `<component>`。
- `<list>` 不使用 `src`、`fileName`、`pkg` 表达默认项。

## 9. ID 映射如何保证增量稳定

`id-map.json` 是增量更新的关键文件：

```json
{
  "_meta": {
    "buildIds": {
      "LobbyLogin": "v7qad38hns5o"
    }
  },
  "ui://LobbyLogin/UiLogin": {
    "btn_buy": "n0_ns5o",
    "title": "n1_ns5o"
  }
}
```

规则：

- `semanticId` 仍存在：复用旧 nodeId。
- 新增 `semanticId`：调用 `genIdPool` 分配新 nodeId。
- 删除 `semanticId`：从新 idMap 中移除。
- 同一个包复用 `_meta.buildIds[pack]`，避免 buildId 漂移。
- `build-prompt` 是 id 分配提交点，装配后立即写回 id-map。
- `verify-idmap` 只读已写回的 idMap，不重新装配，避免校验阶段造成 ID 漂移。

这解决的是：第二次从 Figma 更新时，原来没变的节点在 FGUI 里仍保持同一个 `id`，减少代码绑定、控制器、动效、引用关系被破坏的风险。

## 10. 校验和修复怎么做

固定校验项：

| 校验项 | 说明 |
|---|---|
| 节点树完备性 | XML displayList 是否覆盖 idMap 中全部 semanticId |
| 引用正确性 | 调 `fairygui-ref-validator` 检查 `src`、`pkg`、`ui://` |
| 命名合理性 | 节点 name 是否为空或非法 |
| 文件归属 | 组件 XML 是否在 `Views/` 或 `Coms/`，package.xml 是否注册 |
| 类型一致性 | IR 的 `elementType` 是否生成了正确 XML 标签 |
| ID 一致性 | buildId、pkgId、resourceId、nodeId 前后缀是否一致 |
| 用户自定义验证 | 执行或提示 `<verify>` 块中的人工验证要求 |

修复机制：

```text
validate 不通过
  -> insert-fix 追加 fix task
  -> 回到 produce
  -> 最多 3 轮
```

超过 3 轮仍失败时，停止自动修复，报告残留问题。已经生成的部分仍然保留，但不能静默当作完全正确。

## 11. 手动和自动两种使用方式

### 11.1 手动流程

适合需要人工校树或任务审查的情况：

```text
f2f-create
  -> f2f-checktree
  -> f2f-tasks
  -> 手工审查 ui-generate-tasks.xml
  -> f2f-apply
```

人工介入点：

- `checktree` 阶段：调整 IR 节点树、组件划分、属性和备注。
- `tasks` 后：编辑 `ui-generate-tasks.xml` 的 `<remark>` 和 `<verify>`。
- `apply` 后：处理残留问题。

### 11.2 自动流程

适合快速从设计生成白模：

```text
f2f-implement <Figma URL>
```

等价于：

```text
f2f-ff create <Figma URL>
```

自动流程会跳过实时人工校树，使用 `checktree auto` 重放历史 `tree-modify.cmds`，然后继续生成 tasks 和 apply。

### 11.3 从中间阶段重跑

`f2f-ff` 可以从指定阶段开始重跑该阶段及之后所有阶段：

```text
f2f-ff <module> tasks
```

含义：重置 `tasks` 和 `apply` 为未完成，然后重新生成任务并重新 apply。

## 12. 什么时候能直映，什么时候要重构

### 12.1 适合直接映射

- Frame 到 Component。
- Layer hierarchy 到 displayList。
- x/y/width/height 到 xy/size。
- opacity/visible/rotation 到 alpha/visible/rotation。
- 简单文本到 `<text>`。
- 简单矩形、椭圆到 `<graph>`。
- Constraints 到 Relation。
- Scroll 区域到 overflow scroll / ScrollPane。
- Component 引用到 `<component>`。

### 12.2 需要近似映射

- Auto Layout：列表型转 GList，普通容器转坐标和 Relation。
- Figma Instance override：转子节点属性、Controller 或备注。
- Variants：转 Controller pages。
- Button 状态：转 Button extension、Controller、gear 或 transition。
- 图片 fit/fill/crop：转 Loader fill 或预裁切资源。
- 阴影、模糊、混合模式：按 FGUI 支持范围近似。

### 12.3 通常需要重构或烘焙

- 多重 fill。
- 渐变、pattern、noise。
- 复杂 vector network。
- Boolean operation。
- 独立每边 stroke、虚线、箭头端点。
- 高级原型流程。
- 视频。
- Figma variables、theme modes、复杂设计系统样式。

处理方式通常是：

- 烘焙成图片资源。
- 拆成多个 FGUI 节点。
- 使用 Controller / Transition 重建状态和动效。
- 交给运行时代码承接。
- 写入 `comments` 或 `<remark>`，由人工或 generator 按项目规则补足。

## 13. 最小可执行规范

如果要让一个 Figma 设计稳定进入 f2f 流程，至少做到：

1. 导出根节点命名为 `UiXxx@PackageName`。
2. 关键节点使用 `[类型前缀#]节点名[@包/资源]` 明确类型和引用。
3. 可复用或需要引用的区域拆成 Frame/Component，并命名清楚。
4. 列表节点用 `list#xxx@Package/ItemComponent` 标注默认项。
5. 按钮、标签、进度条等扩展控件用 `button#`、`label#`、`progress#` 等前缀标注。
6. 高级视觉效果提前决定：转 FGUI 属性、拆节点，还是烘焙图片。
7. 需要额外状态、控制器、动效、多语言等内容，在 checktree comment 或 tasks remark 中补充。
8. 提供或配置 FGUI `assetsPath`，否则资源存在性和引用校验会降级。

## 14. 最终回答：如何对应，通过什么方式转

### 如何对应

Figma 和 FGUI 的对应关系分三层：

1. 结构层：Figma Frame/Component/Instance 对应 FGUI Component，Figma 图层树对应 FGUI displayList。
2. 属性层：坐标、尺寸、文本、颜色、描边、透明度、裁剪、约束等进入 IR 的 `props` 和 `relations`，再生成 XML 属性。
3. 资源层：Figma 节点名里的 `@pack/resource` 统一转成 `ui://pack/resource`，再通过 resource lookup 解析到 FGUI 的 package/resource ID，最终落到 `src`、`fileName`、`pkg`、`url` 或 `defaultItem`。

### 通过什么方式转

转换方式是分阶段的：

1. 用 `figma-use` 在 Figma 文件上下文执行导出脚本，分批抓取节点数据。
2. 用 `f2f-create` 的本地转换器把 Raw JSON 转成 `fgui-ir.json`。
3. 用 `f2f-checktree` 允许人工校准 IR。
4. 用 `f2f-tasks` 把 IR 按组件依赖转成任务清单。
5. 用 `f2f-apply` 为每个任务装配 prompt 和 idMap。
6. 用 `fairygui-generator` 生成或修改 FairyGUI XML。
7. 用 `fairygui-ref-validator`、id-map 校验和固定验证项做闭环。
8. 用最多 3 轮 fix task 做自动修复。

所以这套方案的核心价值是：转换规则尽量脚本化，AI 只参与适合它的生成和解释环节；每个阶段都有明确输入输出、可审查文件、可重跑能力和校验边界。
