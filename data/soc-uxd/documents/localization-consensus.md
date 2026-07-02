---
docId: "localization-consensus"
title: "本地化设计共识与落地规范"
sourceFile: "本地化设计共识与落地规范.md"
sourceType: "md"
publishStatus: "converted"
ingestMode: "archival"
updatedAt: "2026-07-02"
topics: ["多语言规范", "本地化", "合规风险", "文本适配"]
---

# 本地化设计共识与落地规范

## 文档身份
- 原始文件：本地化设计共识与落地规范.md
- 文档类型：md
- 所属模块：多语言规范、本地化、合规风险、文本适配
- 状态：converted
- 入库模式：资料归档优先

## 资料摘要

本地化设计共识与落地规范 本地化目的 规避文化、法规、舆论风险：保证上线无阻、审核通过、避免争议； 打破语言壁垒，保证多语言适配：让不同语种玩家顺畅理解与操作； 提供本土化内容，提升用户体验：增强用户认同感，促进商业表现。 本地化设计要求 规避风险 作为UX和GUI，与策划合作产出无风险的多语言内容 打破语言壁垒（重...

## 原文结构转写

- 本地化设计共识与落地规范
- 本地化目的
- 本地化设计要求
- 规避风险
- 打破语言壁垒（重要）
- 2.1 设计：
- 2.1.1 文本长度对比
- 2.1.2 设计注意事项
- 2.1.3 大小写规范
- 2.1.4 文本间距、字号差异
- 2.2 拼接：
- 2.3 验证：
- 3. 本土化内容
- 3.1 不同地区可能需要不同的美术资源
- 3.1.1 相同使用场景的资源，使用地区的后缀进行区分：
- 3.1.2 部分海外资源可以统一使用Eng后缀的资源
- 3.2 在后期需要留意可能的工作

## 明确规则 / 决策

- **规避文化、法规、舆论风险**：保证上线无阻、审核通过、避免争议；
- | 必要共识 | 遵守各地法规，增加法定展示与流程，避免文化禁忌与符号误用 |
- | **文化敏感性**<br>后续推进 | 提出潜在文化风险（图标、颜色、行为设定、节日元素） | 规划替换策略：哪些是可模块替换内容，哪些不能通用 | 设计图素/符号具备替换性与文化差异适配空间 |
- | 目标语言 | 长度趋势 | 建议预留比例（相对中文） |
- UI 设计中短文本更容易因语言差异带来页面溢出，建议对这些元素留出**2倍于中文的空间**。对于较长文本，**留出起码1.5倍于中文的空间**。如果后续对其他语言有拓展需求，极端情况需要考虑**3倍于**中文的空间
- 日语、中文、泰语等语言对垂直空间需求不同，应确保行高和段间距足够，避免显示拥挤。
- 使用九宫格可扩展背景、自动换行机制，确保不同长度文本都能适配布局。
- 不要按照中⽂最⼩的⽂本⻓度设计，必须要考虑到本地化后对排版的影响。
- 避免横向空间预留太少，纵向空间预留空间过多，⼀个完整的句⼦被拆开换⾏，不符合阅读习惯。避免⾏尾出现过⻓数字折⾏。
- 多行文本在有限空间的展示，需要考虑**裁切+滑动框**
- 需要规范使⽤⽂本⼤⼩写
- 避免全⼤写（ALL CAPS），除⾮⽤于强调或特殊场景。

## 案例经验

以下保留原文主体，供 AI 检索和人工回溯。

## 待确认 / AI 推论

- | 后期计划 | 能提供本地化替换素材、事件内容，以提升当地用户的文化融入与感知认同 |
- | **法规要求**<br>后续推进 | 提出目标市场合规清单（例如隐私条款、年龄限制标识、退款流程等） | 设计界面流程节点：弹窗、入口、标识、阻断提示... | 规范样式表现：字号、可读性、位置、风格统一 |
- | **文化敏感性**<br>后续推进 | 提出潜在文化风险（图标、颜色、行为设定、节日元素） | 规划替换策略：哪些是可模块替换内容，哪些不能通用 | 设计图素/符号具备替换性与文化差异适配空间 |
- | 德语（目前无，只做参考） | 长，结构复杂 | 2.0x至3.0x |
- UI 设计中短文本更容易因语言差异带来页面溢出，建议对这些元素留出**2倍于中文的空间**。对于较长文本，**留出起码1.5倍于中文的空间**。如果后续对其他语言有拓展需求，极端情况需要考虑**3倍于**中文的空间

## 检索关键词

2.1 设计：、2.1.1 文本长度对比、2.1.2 设计注意事项、合规风险、多语言规范、打破语言壁垒（重要）、文本适配、本地化、本地化目的、本地化设计共识与落地规范、本地化设计要求、规避风险

## 来源定位

- 文件：本地化设计共识与落地规范.md
- 位置：按原文标题和段落回溯。

---

## 原文主体

# 本地化设计共识与落地规范

# 本地化目的

*   **规避文化、法规、舆论风险**：保证上线无阻、审核通过、避免争议；


*   **打破语言壁垒，保证多语言适配**：让不同语种玩家顺畅理解与操作；


*   **提供本土化内容，提升用户体验**：增强用户认同感，促进商业表现。


# 本地化设计要求

| 目的 | 设计要求 |
| --- | --- |
| 必要共识 | 遵守各地法规，增加法定展示与流程，避免文化禁忌与符号误用 |
| 核心需求 | 保证多语言适配，防止文本溢出、重叠、误读等影响体验的问题 |
| 后期计划 | 能提供本地化替换素材、事件内容，以提升当地用户的文化融入与感知认同 |

##  规避风险

作为UX和GUI，与策划合作产出无风险的多语言内容

| 风险维度 | 策划职责 | 交互设计职责 | GUI（视觉）职责 |
| --- | --- | --- | --- |
| **法规要求**<br>后续推进 | 提出目标市场合规清单（例如隐私条款、年龄限制标识、退款流程等） | 设计界面流程节点：弹窗、入口、标识、阻断提示... | 规范样式表现：字号、可读性、位置、风格统一 |
| **文化敏感性**<br>后续推进 | 提出潜在文化风险（图标、颜色、行为设定、节日元素） | 规划替换策略：哪些是可模块替换内容，哪些不能通用 | 设计图素/符号具备替换性与文化差异适配空间 |
| **多语言适配** | 配置流畅无语病的中文内容；<br>规划语言范围、内容优先级、审核流程 | 控件容错、断行策略、占位词规范 | 文字框适配、RTL 支持、装饰元素多语通用性... |

##   打破语言壁垒（重要）

防止文本表意错误的问题，以及超框、显示不完全、重叠等问题

### 2.1 设计：

#### 2.1.1 文本长度对比

| 目标语言 | 长度趋势 | 建议预留比例（相对中文） |
| --- | --- | --- |
| 英语 | 较中文略长 | 1.2× 至 1.5× |
| 日语 | 较中文短，字符宽占位不变 | 0.9×（最保守） — 据需可为 1.0× |
| 泰语 | 略长，结构复杂 | 1.5× 至 2.2× |
| 德语（目前无，只做参考） | 长，结构复杂 | 2.0x至3.0x |
| 俄语 | 长，结构复杂 | 2.0x至3.0x |

*   **短文本（按钮、标题）扩展更显著**
    UI 设计中短文本更容易因语言差异带来页面溢出，建议对这些元素留出**2倍于中文的空间**。对于较长文本，**留出起码1.5倍于中文的空间**。如果后续对其他语言有拓展需求，极端情况需要考虑**3倍于**中文的空间


*   **行高与间距要灵活**
    日语、中文、泰语等语言对垂直空间需求不同，应确保行高和段间距足够，避免显示拥挤。


*   **可拉伸或适配布局设计**
    使用九宫格可扩展背景、自动换行机制，确保不同长度文本都能适配布局。


#### 2.1.2 设计注意事项

*   不要按照中⽂最⼩的⽂本⻓度设计，必须要考虑到本地化后对排版的影响。


![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/25b17dc4-0300-418b-8455-7fd52b7270d3.png)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/1e5c96ba-9f34-4fdb-b545-e36cf4069387.png)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/8efd2827-adbb-40d8-9c31-9272f28f5cbb.png)

在设计阶段预留好⾜够的空间，否则会出现超框或截断的情况

*   避免横向空间预留太少，纵向空间预留空间过多，⼀个完整的句⼦被拆开换⾏，不符合阅读习惯。避免⾏尾出现过⻓数字折⾏。


![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/45570b96-fc09-4702-b948-ff1f50088474.png)

*   跟随文本的底图要九宫拉长

    ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/ccc6d1dd-bfa5-41c8-80a7-d4c10e24fdb1.png)

*    多行文本在有限空间的展示，需要考虑**裁切+滑动框**

    ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/cc37b398-0fd3-4e26-bead-a0c3cccdd9e9.png)

*   可在设计时将可能出错的文本的适配方式直接展示在设计稿上


![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/de303374-c047-421c-978f-9caf448fa4ad.png)

#### 2.1.3 大小写规范

需要规范使⽤⽂本⼤⼩写

**标题与按钮：**

*   使⽤标题式⼤⼩写（Title Case），即每个单词⾸字⺟⼤写（如“New Match”）。

*   避免全⼤写（ALL CAPS），除⾮⽤于强调或特殊场景。


**句子与段落：**

*   使⽤句⼦式⼤⼩写，即⾸字⺟⼤写，其余⼩写（如“Welcome to the game”）


**专有名词：**

*   遵循⽬标语⾔的专有名词⼤⼩写规则（如“iPhone”）。


#### 2.1.4 文本间距、字号差异

待更新

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/a5104457-f803-423a-83a7-ae97aa500b2a.png)

### 2.2 拼接：

合理运用说明文本适配方式：

| 适配方式 | 图例 | 对应FGUI选项 | 对应Figma选项 |
| --- | --- | --- | --- |
| 基本适配 |  |  |  |
| 长度自适应<br>通常也会搭配底图拉三宫/九宫关联文本伸长，以及文本两侧icon关联位移 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/701110cc-e3ce-444f-ad6b-a2d5675b6c9e.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/d49569e0-856e-4772-b5ec-f3e11f5215da.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/179ccdfb-31de-4e44-b451-b45c1f0012ab.png) |
| 高度自适应 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/58e788cc-32db-4c7a-9cf9-fc91779e6dd6.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/4e72f420-3000-4883-9fa2-97ca34a62eac.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/a8b8ad86-f5e0-4f19-985c-4742dbf1e81f.png) |
| **收缩**<br>限定高宽，超出之后收缩字符大小<br>**建议作为适配的默认选项（当前适配默认截断）** | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/95e36f33-f3bd-422b-8c7b-dcdc42681cb1.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/41b7ef35-448f-41b6-8905-b2246944f5e4.png) | \- |
| 省略号<br>超出文本框的部分用省略号代替 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/67abb31f-1eec-408c-998d-3b0b8c4526cd.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/e780302e-7f8c-4653-8550-a36522a62a63.png) | \- |
| 滚动<br>跑马灯等特殊形式，或者少数多语言无法以合适方式适配的情况 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/b687d0b3-458a-401e-ab1c-4d328089e0b1.png) |  |  |
| 截断（强烈不推荐）<br>不做任何处理，超出的文本被隐藏--一般来说不会使用到 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/0f474af6-6eb6-43e1-8942-40310afcde8a.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/ef11d5fd-66f6-4238-b0d0-9defd373f162.png) | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/e643a8d6-f4bf-4db8-99bb-0e0225ca4794.png) |
| 综合适配 |  |  |  |
| 上下滑动<br>文本高度自适应，整个视窗裁切配合滑动框 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/13dcfb3c-c791-4cc1-a8c7-65ae86f2fe7c.png) | \- | \- |
| 长度自适应，但在一定长度之后收缩字符大小<br>**（暂时未实现，后期可根据需要提需）** | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/b95283cb-ce30-40e8-9d61-bca648b6609a.png) | \- | \- |

### 2.3 验证：

figma验证工具、Unity伪本地化语言工具

*   **Figma 阶段**：可使用伪本地化插件 / 多语对比切换 / ai填充文本检查溢出

    | 插件/方式 | 图例 |
    | --- | --- |
    | 可使用类似Pseudo Localizator的插件实现文本替换 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/3dc09171-ad3a-4ab2-b057-58b28bcc237d.png) |
    | 可使用Figma自带的翻译功能翻译文本为目标语言（也可使用其他翻译插件） | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/2414b2ab-c631-4f00-aa09-55a7abf62ee1.png) |
    | 可使用Figma自带的文本替代功能，将文本延长至原本的两倍 | ![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/302127de-282d-4cf1-aadf-c10c59016ef8.png) |

*   **Unity 工程**：接入伪本地化语言（字符替换 + 膨胀）


[《伪本地化工具需求文档（旧版）》](https://alidocs.dingtalk.com/i/nodes/MNDoBb60VLr6X3EvFxRev9Gk8lemrZQ3?utm_scene=team_space)

## 3. 本土化内容

### 3.1 不同地区可能需要不同的美术资源

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/69182b0d-d7ce-4c1f-9fff-dc91d7ce80d8.png)

#### 3.1.1 相同使用场景的资源，使用地区的后缀进行区分：

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/63ddbcce-45a5-42f6-b22b-db818bbab880.png)UiGuideView\_new\_Chs

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/WgZOZA8DG8MV9qLX/img/a906158c-82ce-40bf-a384-c96f9155800e.png)  UiGuideView\_new\_Eng

#### 3.1.2 部分海外资源可以统一使用Eng后缀的资源

比如上图的【新】红点，在功能不做拓展的前提下，海外统一使用【NEW】字样也是可接受的做法。

### 3.2 在后期需要留意可能的工作

| 类别 | GUI 视觉 | 交互设计 |
| --- | --- | --- |
| 节日活动 | Banner 图支持地区替换 | 活动入口结构抽象化 |
| 商业图素 | 礼包卡、标签图层可变 | 组件预设不同版本结构 |
| 剧情图文/语音 | 对话/字幕区支持多语言 | 同步文本语音分轨、可替换 |
