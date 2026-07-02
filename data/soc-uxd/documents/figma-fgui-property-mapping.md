---
docId: "figma-fgui-property-mapping"
title: "Figma 到 FGUI 属性映射"
sourceFile: "figma-fgui-property-mapping.md"
sourceType: "md"
publishStatus: "converted"
ingestMode: "archival"
updatedAt: "2026-07-02"
topics: ["Figma 到 FGUI 工作流", "属性映射"]
---

# Figma 到 FGUI 属性映射

## 文档身份
- 原始文件：figma-fgui-property-mapping.md
- 文档类型：md
- 所属模块：Figma 到 FGUI 工作流、属性映射
- 状态：converted
- 入库模式：资料归档优先

## 资料摘要

Figma 与 FairyGUI 设计属性映射对照表 更新时间：2026-06-25 阅读范围 本表基于以下官方文档整理： Figma 官方帮助中心：Design 类别，包含 29 个分区、182 篇文章。 FairyGUI 官方教程：Editor tutorial，覆盖 Project、Package、Object...

## 原文结构转写

- Figma 与 FairyGUI 设计属性映射对照表
- 1. 阅读范围
- 2. 映射等级说明
- 3. 总体概念映射
- 4. 几何与层级属性
- 5. 布局与响应式属性
- 6. 视觉样式属性
- 7. 图像、图形与矢量
- 8. 文本属性
- 9. 组件、状态与复用
- 10. 交互、原型与动效
- 11. 资源、样式、变量与发布
- 12. 不建议直接映射的 Figma 能力
- 13. 转换优先级建议
- 14. 关键结论
- 15. 官方来源

## 明确规则 / 决策

- 本文目标不是逐字翻译文档，而是从“将 Figma 设计转换/实现为 FGUI 界面”的角度，整理两套设计属性之间的对应关系。
- | 近似 | 两边概念接近，但细节、平台表现或运行时行为不同，需要转换规则。 |
- | 重构 | FGUI 没有等价的一等属性，需要拆成多个对象、导出图片、写代码或自定义组件。 |
- | Page | Package / 编辑组织 | 近似 | Figma Page 通常需要按资源包或模块拆为 FGUI Package。 |
- | Layer name | Name | 直映 | FGUI 可通过 GetChild(name) 访问；建议转换时生成稳定且不重复的语义名。 |
- | Section | 无运行时等价 | 无 | Figma Section 多为画布组织和交付辅助，不应直接生成运行时 UI。 |
- | Rotation | Rotation | 近似 | Figma 设计面板正角度与 FGUI 正角度方向相反时，需要转换符号。 |
- | Absolute position in auto layout | 手工 Position / 脱离布局处理 | 近似 | FGUI 没有同名 auto layout 机制，需要单独定位。 |
- | Constraints: Left and Right | Relation: Left + Right / Width | 近似 | 需要同时维护左右边距和宽度变化。 |
- | Constraints: Top and Bottom | Relation: Top + Bottom / Height | 近似 | 需要同时维护上下边距和高度变化。 |
- | Auto layout: horizontal | List single row / horizontal flow / 手工 Relation | 近似 | 列表型内容优先 GList；普通容器需要重建布局逻辑。 |
- | Fill opacity | Alpha 或颜色 alpha | 近似 | 需要区分对象整体透明度和单个颜色透明度。 |

## 案例经验

以下保留原文主体，供 AI 检索和人工回溯。

## 待确认 / AI 推论

- 暂无。

## 检索关键词

1. 阅读范围、2. 映射等级说明、3. 总体概念映射、4. 几何与层级属性、5. 布局与响应式属性、6. 视觉样式属性、7. 图像、图形与矢量、Figma 与 FairyGUI 设计属性映射对照表、Figma 到 FGUI 属性映射、Figma 到 FGUI 工作流、属性映射

## 来源定位

- 文件：figma-fgui-property-mapping.md
- 位置：按原文标题和段落回溯。

---

## 原文主体

# Figma 与 FairyGUI 设计属性映射对照表

更新时间：2026-06-25

## 1. 阅读范围

本表基于以下官方文档整理：

- Figma 官方帮助中心：Design 类别，包含 29 个分区、182 篇文章。
- FairyGUI 官方教程：Editor tutorial，覆盖 Project、Package、Object、Component、Relation、Controller、Text、Image、Graph、Transition、List、Publish 等页面。

本文目标不是逐字翻译文档，而是从“将 Figma 设计转换/实现为 FGUI 界面”的角度，整理两套设计属性之间的对应关系。

## 2. 映射等级说明

| 映射等级 | 含义 |
|---|---|
| 直映 | 两边都有语义和行为接近的属性，转换时通常可直接映射。 |
| 近似 | 两边概念接近，但细节、平台表现或运行时行为不同，需要转换规则。 |
| 重构 | FGUI 没有等价的一等属性，需要拆成多个对象、导出图片、写代码或自定义组件。 |
| 无 | 属于设计协作、编辑辅助或 Figma 特有能力，通常不进入 FGUI 运行时 UI。 |

## 3. 总体概念映射

| Figma 概念 | FGUI 概念 | 映射等级 | 转换说明 |
|---|---|---:|---|
| File | Project | 近似 | Figma 文件偏设计资产容器；FGUI Project 是编辑器工程。 |
| Page | Package / 编辑组织 | 近似 | Figma Page 通常需要按资源包或模块拆为 FGUI Package。 |
| Canvas | Stage / 编辑区 | 近似 | Canvas 是设计工作区；FGUI Stage 是组件编辑和预览区域。 |
| Top-level Frame | Component / GComponent | 直映 | Figma 顶层 Frame 通常映射为一个 FGUI 组件或界面根组件。 |
| Nested Frame | 子 Component / Group | 近似 | 有裁剪、滚动、状态、复用需求时用 Component；纯组织可用 Group。 |
| Layer hierarchy | Display list | 直映 | Figma 图层树映射 FGUI 显示列表；同父级内顺序决定遮挡关系。 |
| Layer name | Name | 直映 | FGUI 可通过 GetChild(name) 访问；建议转换时生成稳定且不重复的语义名。 |
| Parent / Child / Sibling | Container / Child display object | 直映 | 两边都用父子层级表达包含关系。 |
| Section | 无运行时等价 | 无 | Figma Section 多为画布组织和交付辅助，不应直接生成运行时 UI。 |

## 4. 几何与层级属性

| Figma 设计属性 | FGUI 设计属性 | 映射等级 | 转换说明 |
|---|---|---:|---|
| X / Y | Position | 直映 | 都表示父容器坐标系下的位置。 |
| Width / Height | Size | 直映 | 基础宽高可直接映射。 |
| Min / Max size | smallest size / biggest size | 近似 | FGUI 组件支持尺寸限制；Figma 中该语义常与 auto layout 或 constraints 结合。 |
| Aspect ratio lock | Keep ratio | 近似 | FGUI Keep ratio 是编辑辅助，运行时不一定保持比例。 |
| Scale | Scale | 直映 | 可映射，但 FGUI 文档明确区分 Scale 与 Size；UI 转换通常优先改 Size。 |
| Rotation | Rotation | 近似 | Figma 设计面板正角度与 FGUI 正角度方向相反时，需要转换符号。 |
| Pivot / transform origin | Axis / As anchor | 近似 | Figma 旋转中心通常以选区中心为主；FGUI 可显式设置轴点和锚点。 |
| Opacity | Alpha | 直映 | Figma 0-100%，FGUI 0-1。 |
| Visible / Hidden | Invisible | 直映 | 静态隐藏可用 Invisible。 |
| Lock layer | 编辑器锁定 | 无 | 只影响编辑，不是运行时属性。 |
| Layer order | Display list order | 直映 | FGUI 同父级显示列表中，索引越大越靠前显示。 |
| Absolute position in auto layout | 手工 Position / 脱离布局处理 | 近似 | FGUI 没有同名 auto layout 机制，需要单独定位。 |
| Clip content | Overflow handling: hide | 直映 | Figma Frame 裁剪可映射为 FGUI 组件 overflow hide。 |
| Overflow scroll | Overflow handling: vertical / horizontal / free scroll | 直映 | Figma 原型滚动区域可映射为 FGUI 滚动容器。 |

## 5. 布局与响应式属性

| Figma 属性/机制 | FGUI 属性/机制 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Constraints: Left | Relation: Left -> Left | 直映 | 保持与父容器左边的距离。 |
| Constraints: Right | Relation: Right -> Right | 直映 | 保持与父容器右边的距离。 |
| Constraints: Left and Right | Relation: Left + Right / Width | 近似 | 需要同时维护左右边距和宽度变化。 |
| Constraints: Top | Relation: Top -> Top | 直映 | 保持与父容器顶部距离。 |
| Constraints: Bottom | Relation: Bottom -> Bottom | 直映 | 保持与父容器底部距离。 |
| Constraints: Top and Bottom | Relation: Top + Bottom / Height | 近似 | 需要同时维护上下边距和高度变化。 |
| Constraints: Center | Relation: Center / Middle | 近似 | 可用居中关系表达，但需注意初始位置仍要手动设置。 |
| Constraints: Scale | 百分比 Relation / Controller 百分比坐标 | 近似 | FGUI 支持部分百分比记录，但要按具体关系系统重建。 |
| Auto layout: horizontal | List single row / horizontal flow / 手工 Relation | 近似 | 列表型内容优先 GList；普通容器需要重建布局逻辑。 |
| Auto layout: vertical | List single column / vertical flow / 手工 Relation | 近似 | 列表、菜单、表单更适合用 GList；普通面板用 Relation。 |
| Auto layout: wrap | List flow / pagination | 近似 | 可用 FGUI List 横向/纵向流近似，但不完全等价。 |
| Auto layout: grid | List flow / 自定义布局 | 重构 | Figma grid auto layout 支持行列、span、track resize；FGUI 需按业务重建。 |
| Padding | List / Component 内边距结构 | 近似 | FGUI 没有统一 auto layout padding；通常通过容器尺寸和子节点坐标体现。 |
| Gap between items | List line spacing / column gap / 手工间距 | 近似 | 列表可映射；普通 Frame 需计算坐标。 |
| Alignment in auto layout | Aligned / Relation / List alignment | 近似 | 需区分文本对齐、列表对齐和容器内对象对齐。 |
| Hug contents | Auto size / List autosize / 文本自动尺寸 | 近似 | FGUI 支持文本自动尺寸和 List autosize，但不等价于通用 Hug。 |
| Fill container | Relation Size / Width / Height | 近似 | 通常用 Relation 跟随父容器尺寸。 |
| Layout guides | 无运行时等价 | 无 | 仅作设计辅助。 |

## 6. 视觉样式属性

| Figma 属性 | FGUI 属性 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Solid fill | Graph fill color / Image colour / Text colour | 直映 | 按节点类型分别映射。 |
| Fill opacity | Alpha 或颜色 alpha | 近似 | 需要区分对象整体透明度和单个颜色透明度。 |
| Multiple fills | 多子节点叠加 / 烘焙图片 | 重构 | FGUI 单个基础对象不等价支持 Figma 多填充栈。 |
| Gradient fill | 图片资源 / 自定义 shader | 重构 | 常规做法是导出位图，或由目标引擎自定义渲染。 |
| Pattern fill | 图片资源 / 平铺图像 | 重构 | 简单平铺可用 Image tile；复杂 pattern 建议烘焙。 |
| Image fill | Image / Loader URL | 近似 | Figma 图像填充需要转为 FGUI 资源引用。 |
| Video fill | MovieClip / Loader / 引擎侧视频 | 重构 | 取决于目标运行时是否支持视频。 |
| Stroke color / weight | Graph line color / line size | 直映 | 基础描边可直接映射。 |
| Individual strokes | 拆分为多个 Graph 线条 | 重构 | FGUI Graph 不直接等价支持每边独立描边。 |
| Dashed stroke | 烘焙图片 / 自定义绘制 | 重构 | FGUI Graph 基础线条不完整覆盖 Figma 虚线描边。 |
| Stroke caps / arrows | 额外图形节点 / 图片资源 | 重构 | 箭头和端点样式需拆节点或切图。 |
| Variable width stroke | 图片 / 自定义矢量 | 重构 | Figma Draw 高级描边通常需要烘焙。 |
| Corner radius | Graph fillet / 圆角矩形 | 近似 | 基础矩形可映射；图片圆角通常要 mask 或切图。 |
| Blend mode | BlendMode | 近似 | FGUI 支持部分混合模式，但不同引擎表现和成本不同。 |
| Layer blur / background blur | Filter / 烘焙 | 近似 | FGUI 支持模糊滤镜，但组件级滤镜可能有性能成本。 |
| Drop shadow | Filter / 文本 projection / 烘焙 | 近似 | 文本阴影可近似；复杂阴影建议导出图片或自定义效果。 |
| Inner shadow | 烘焙图片 / 自定义效果 | 重构 | FGUI 无完全等价基础属性。 |
| Noise effect | 图片 / shader | 重构 | 需要资源化或自定义渲染。 |
| Grayscale | Grayed / Color filter | 直映 | FGUI 有 Grayed，也可通过 Controller 控制状态。 |

## 7. 图像、图形与矢量

| Figma 属性/对象 | FGUI 属性/对象 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Rectangle | Graph Rectangle | 直映 | 可映射填充、描边、圆角。 |
| Ellipse | Graph Circle | 近似 | 圆/椭圆基础可映射。 |
| Polygon / star | Graph Polygon / Regular Polygon | 近似 | 简单多边形可映射，复杂编辑点需转换。 |
| Vector network | Graph / 图片 / 自定义路径 | 重构 | FGUI Graph 不等价支持 Figma 完整 vector network。 |
| Boolean operations | 烘焙为图片或矢量资源 | 重构 | 建议在转换前展平或导出。 |
| Pencil / Draw illustrations | 图片资源 | 重构 | 高级插画工具输出通常应作为图像资源。 |
| Image crop | 预裁切资源 / Loader fill processing | 近似 | 按实际填充策略选择 show all、borderless、fit width/height 等。 |
| Image fit / fill | Loader Fill processing | 近似 | Figma fit/fill 与 FGUI Loader 填充策略语义接近但需逐项校准。 |
| Image smoothing | Allow smoothing | 直映 | 可映射到 FGUI 图像资源属性。 |
| Nine-slice scaling | Scale 9 grid / Zoom with Nine Palace | 直映 | Figma 如果使用 9-slice 语义，应映射为 FGUI 九宫格缩放。 |
| Tile image | Zoom using tiles / tile | 近似 | 可映射，但需注意资源边缘重复和纹理设置。 |
| Image tint | Image colour / Loader colour | 直映 | FGUI 支持图像颜色调整。 |
| Brightness | brightness | 直映 | FGUI Image / Loader 有 brightness。 |
| Flip | Flip | 直映 | 图像翻转可映射。 |

## 8. 文本属性

| Figma 文本属性 | FGUI 文本属性 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Text content | text / title | 直映 | 普通文本映射 Text；Label/Button 映射 title。 |
| Font family | font | 近似 | 动态字体需确保目标平台存在；位图字体需使用对应资源 URL。 |
| Font size | font size | 直映 | 位图字体需允许动态字号变化。 |
| Font weight | bold / 字体资源 | 近似 | 常见 bold 可映射；多字重字体族需按资源处理。 |
| Italic | italic | 直映 | 可映射。 |
| Underline | underline | 直映 | 可映射。 |
| Strikethrough | UBB / RichText / 自定义 | 近似 | FGUI 普通 Text 工具栏未完全等价覆盖。 |
| Text color | colour | 直映 | 位图字体需允许动态颜色变化。 |
| Line height | Line spacing | 近似 | Figma line height 与 FGUI 行间距口径可能不同。 |
| Letter spacing | Kerning | 近似 | FGUI 文档说明部分 H5 引擎不支持。 |
| Horizontal alignment | Aligned | 直映 | 可映射。 |
| Vertical alignment | Aligned | 直映 | 可映射。 |
| Auto width | Auto size: Auto width and height | 近似 | FGUI 该模式宽高都会随文本增长。 |
| Auto height / wrap | Auto size: Automatic height | 直映 | 固定宽度、自动换行、增长高度。 |
| Fixed size | Auto size: no | 直映 | 固定宽高，不自动扩展。 |
| Auto shrink | Auto size: Automatic shrink | 直映 | FGUI 支持自动缩小。 |
| Single line | Single line | 直映 | 可映射。 |
| Mixed text styles | UBB / RichText | 近似 | 复杂混排建议转 RichText；普通文本平台支持有限。 |
| Text stroke | Stroke | 直映 | FGUI 支持文本描边，但不同引擎效果可能不同。 |
| Text shadow | projection | 近似 | FGUI projection 是简化阴影效果。 |
| Input text | GTextInput | 直映 | Figma 输入框视觉需要映射为 FGUI 输入文本组件。 |
| Placeholder / input restrictions | GTextInput 设置 | 近似 | 需按目标平台支持转换。 |

## 9. 组件、状态与复用

| Figma 属性/机制 | FGUI 属性/机制 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Component | Component resource / GComponent | 直映 | Figma 主组件可映射为 FGUI 组件资源。 |
| Instance | Component instance | 近似 | Figma override 需转换为子节点属性、Controller 或暴露属性。 |
| Component set | Component + Controller | 近似 | 一组 variants 通常映射为一个组件加控制器页面。 |
| Variant property | Controller page / Controller value | 近似 | variant 属性值可映射为 Controller 的 page。 |
| Boolean component property | Display control / Controller | 近似 | 显隐类布尔值适合用 Controller display control。 |
| Text component property | Text control | 近似 | FGUI Controller 支持 text control。 |
| Instance swap property | Icon control / URL / 子组件替换 | 重构 | 需要按 loader、icon 或子组件替换策略实现。 |
| Exposed nested property | Export as component property | 近似 | FGUI 支持导出子组件控制器作为组件属性。 |
| Interactive component | Controller + Button linkage + Transition | 近似 | Figma 交互组件需要重建为 FGUI 控制器、按钮联动和动效。 |
| Disabled state | Grayed / Touchable / Controller | 近似 | 可通过 grayed、touchable 和状态控制组合。 |
| Button variants | GButton mode / selected state / Controller | 近似 | 普通按钮、单选、复选可落到 FGUI Button。 |
| Slot | 子组件占位 / Graph placeholder | 近似 | FGUI 可用空 Graph 作为占位，或约定子组件替换。 |
| Custom data | Custom data | 直映 | FGUI 支持自定义数据发布到描述文件。 |

## 10. 交互、原型与动效

| Figma 原型/动效属性 | FGUI 对应机制 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Prototype flow | 运行时代码 / 页面跳转逻辑 | 重构 | Figma 原型是演示逻辑，FGUI 需要代码或框架路由实现。 |
| Trigger: click/tap | Button event / touch event | 近似 | 可转换为运行时事件绑定。 |
| Trigger: hover/press | Button state / Controller | 近似 | 常见按钮状态可映射。 |
| Navigate to frame | 打开 Component / Window / 切换页面 | 重构 | 需要由运行时代码承接。 |
| Overlay | Window / Popup | 近似 | 弹窗、菜单、浮层可映射。 |
| Back / close overlay | Window close / Popup hide | 近似 | 需要运行时行为。 |
| Scroll behavior | ScrollPane | 直映 | 滚动区域可映射。 |
| Fixed objects in scroll | Relation / 独立层级 / sortingOrder | 近似 | 需按滚动容器结构拆层。 |
| Smart animate | Transition | 近似 | 位移、缩放、透明度、旋转、颜色等可映射。 |
| Dissolve / move in / push | Transition / 运行时代码 | 近似 | 可用 Transition 或页面切换代码实现。 |
| Animated GIF | MovieClip / Loader | 近似 | 取决于资源发布与目标引擎支持。 |
| Video in prototype | 引擎侧视频组件 / 自定义 Loader | 重构 | FGUI Editor 基础控件不完全等价。 |
| Export animations | Transition / MovieClip / 外部视频 | 重构 | 要区分运行时动效与导出视频。 |
| State management for prototypes | Controller / 运行时状态 | 近似 | 设计原型状态需转换为真实状态模型。 |

## 11. 资源、样式、变量与发布

| Figma 机制 | FGUI 机制 | 映射等级 | 转换说明 |
|---|---|---:|---|
| Color style | 资源规范 / 代码常量 / 默认属性 | 重构 | FGUI 没有 Figma style 的一等价物。 |
| Text style | 文本默认属性 / 代码生成规范 | 重构 | 可在转换器中作为样式表处理。 |
| Effect style | 滤镜/烘焙规则 | 重构 | 需按支持范围转换。 |
| Layout guide style | 无运行时等价 | 无 | 仅设计辅助。 |
| Variables | Controller / Branch / 自定义配置 | 重构 | Figma variables 可用于颜色、数字、文本、布尔等；FGUI 无完全等价物。 |
| Variable modes | Branch / Controller pages / 配置表 | 重构 | 主题、多语言、平台差异可分别映射到不同机制。 |
| Library | Package / 跨包引用 | 近似 | Figma library 的复用可对应 FGUI package 资源复用。 |
| Published component | Exported resource | 近似 | FGUI 资源需设置 export，才能跨包访问或动态创建。 |
| Import images | Resource library import | 直映 | 图片、声音、movieclip、文本等导入 FGUI 资源库。 |
| Static export PNG/JPG/SVG/PDF | Publish / 资源导出 | 近似 | Figma export 是设计资产输出；FGUI publish 是运行时包发布。 |
| Export scale | 高清资源 / @2x / 发布设置 | 近似 | 需结合 FGUI 高清资源选择和图集设置。 |
| Atlas packing | Publish atlas settings | 直映 | FGUI 发布流程中有图集和图片质量配置。 |
| i18n | i18n text export/import | 直映 | FGUI 官方支持文本导出翻译再加载。 |
| Branching | Project branch | 近似 | Figma branch 是协作分支；FGUI branch 更偏项目差异和多态资源。 |

## 12. 不建议直接映射的 Figma 能力

以下 Figma 能力通常不应作为 FGUI 运行时属性生成：

| Figma 能力 | 处理建议 |
|---|---|
| Comments | 忽略，或作为转换报告备注。 |
| Multiplayer cursors / spotlight | 忽略。 |
| Viewer history | 忽略。 |
| Branch review | 忽略，或作为设计流程信息。 |
| Canvas background color | 一般不进入组件；如需要可转为舞台预览或根背景。 |
| Layer lock | 仅编辑态信息，忽略。 |
| Layout guides | 仅设计辅助，忽略。 |
| Dev Mode inspect 信息 | 可辅助转换，但不是 UI 运行时属性。 |
| Figma AI / Agent 操作 | 不映射。 |

## 13. 转换优先级建议

1. 先转换结构：Frame、Component、Group、Layer hierarchy。
2. 再转换几何：Position、Size、Rotation、Alpha、Clip。
3. 再转换视觉：Fill、Stroke、Image、Text、Effect。
4. 再转换布局：Constraints 优先映射 Relation；Auto layout 按 List、Relation 或手工布局拆解。
5. 再转换状态：Variants 和 component properties 优先映射 Controller。
6. 最后转换交互：Prototype 逻辑不要直接照搬，需要按 FGUI 运行时事件、Window、Popup、Transition 重建。

## 14. 关键结论

- Figma 的基础图层属性和 FGUI 的 GObject 通用属性匹配度较高。
- Figma Frame 与 FGUI Component 是最重要的一组结构映射。
- Figma Constraints 与 FGUI Relation 是最自然的一组响应式映射。
- Figma Variants 与 FGUI Controller 可以建立稳定映射，但需要规则化命名。
- Figma Auto layout 不能简单等价到 FGUI；列表型场景用 GList，其他场景需要 Relation 或转换器计算布局。
- Figma 高级视觉能力，例如多重填充、复杂描边、矢量网络、背景模糊、变量系统，通常需要烘焙图片、拆节点、写代码或做资源规范。

## 15. 官方来源

Figma 官方文档：

- [Figma Design category](https://help.figma.com/hc/en-us/categories/360002042553)
- [Frames in Figma Design](https://help.figma.com/hc/en-us/articles/360041539473-Frames-in-Figma-Design)
- [Guide to auto layout](https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout)
- [Apply constraints to define how layers resize](https://help.figma.com/hc/en-us/articles/360039957734-Apply-constraints-to-define-how-layers-resize)
- [Guide to fills](https://help.figma.com/hc/en-us/articles/360041003694-Guide-to-fills)
- [Apply and adjust stroke properties](https://help.figma.com/hc/en-us/articles/360049283914-Apply-and-adjust-stroke-properties)
- [Explore text properties](https://help.figma.com/hc/en-us/articles/360039956634-Explore-text-properties)
- [Guide to components in Figma](https://help.figma.com/hc/en-us/articles/360038662654-Guide-to-components-in-Figma)
- [Create and use variants](https://help.figma.com/hc/en-us/articles/360056440594-Create-and-use-variants)
- [Guide to variables in Figma](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
- [Guide to prototyping in Figma](https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma)

FairyGUI 官方文档：

- [Editor tutorial](https://www.fairygui.com/docs/editor)
- [Object](https://www.fairygui.com/docs/editor/object)
- [Component](https://www.fairygui.com/docs/editor/component)
- [Relation](https://www.fairygui.com/docs/editor/relation)
- [Controller](https://www.fairygui.com/docs/editor/controller)
- [Text](https://www.fairygui.com/docs/editor/text)
- [Image](https://www.fairygui.com/docs/editor/image)
- [Graph](https://www.fairygui.com/docs/editor/graph)
- [Loader](https://www.fairygui.com/docs/editor/loader)
- [Button](https://www.fairygui.com/docs/editor/button)
- [List](https://www.fairygui.com/docs/editor/list)
- [ScrollPane](https://www.fairygui.com/docs/editor/scrollpane)
- [Transition](https://www.fairygui.com/docs/editor/transition)
- [Publish](https://www.fairygui.com/docs/editor/publish)
- [Project Settings](https://www.fairygui.com/docs/editor/project_settings)
