---
docId: "prompt-system-source-notes"
title: "提示系统整理"
sourceFile: "提示系统整理.md"
sourceType: "md"
publishStatus: "converted"
ingestMode: "archival"
updatedAt: "2026-07-02"
topics: ["信息提示系统", "提示队列", "配置表"]
---

# 提示系统整理

## 文档身份
- 原始文件：提示系统整理.md
- 文档类型：md
- 所属模块：信息提示系统、提示队列、配置表
- 状态：converted
- 入库模式：资料归档优先

## 资料摘要

提示系统整理 提示样式和位置参考 1.通用文本提示 2.战斗弱提示 3.常驻准星提示 4.短触发提示 5.获得物品提示 6.左侧信息弹窗提示 7.NPC文本提示 8.持续性提示 9.情报柜和科技升级等提示 10.抄家成功提示 11.任务提示 12.奖励提示 13.新手键位引导提示 GM指令 点击该GM指令，将显示上面...

## 原文结构转写

- 提示系统整理
- 提示样式和位置参考
- 1.通用文本提示
- 2.战斗弱提示
- 3.常驻准星提示
- 4.短触发提示
- 5.获得物品提示
- 6.左侧信息弹窗提示
- 7.NPC文本提示
- 8.持续性提示
- 9.情报柜和科技升级等提示
- 10.抄家成功提示
- 11.任务提示
- 12.奖励提示
- 13.新手键位引导提示
- GM指令
- 配置相关
- 05\_通用提示表插入链接
- 大厅杂项/错误码.xlsx
- 189\_持续性提示表.xlsx
- 192\_短触发目标提示表
- 193\_侧弹窗提示表
- 41\_道具\_总表
- 97\_系统\_研发表（原科技表）![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/93ae2bc6-ffb5-47a2-9b58-35a49acefade.png)
- 05\_通用提示表\_重要节点提示sheet
- 05\_通用提示表\_重要成就提示sheet
- FGUI资源路径
- 1.通用文本提示
- 2.战斗弱提示
- 3.常驻准星提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/f45aa297-e3f3-4b91-8df9-071998879acc.png)
- 4.短触发提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/3a2fd810-ab9c-4d15-b006-d56134fd5ba1.png)
- 5.获得物品提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/4d16506c-1838-4325-8d4c-9662f615c993.png)
- 6.左侧信息弹窗提示
- 7.Npc文本提示（目前只给新手引导使用）![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/791729ea-22d1-4050-b062-40febb47597c.png)
- 8.持续性提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/6bfbbab3-58cc-48eb-846f-489dd6067789.png)
- 9.情报柜和科技升级等提示
- 10.抄家成功提示
- 11.任务提示
- 12.奖励提示
- 13.新手键位引导提示

## 明确规则 / 决策

- | audioEvent | 音效配置，配置了就会在提示出现的时候播放对应音效 |
- | isGuideHide | 是否在引导教学隐藏，需要在设置中将设置为关才能进行隐藏![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/8a11d62c-e285-4f7a-a479-69e4d4bbd780.png) |
- | ToMoveDownTip | 从屏幕置顶往下移动像素（填0或者空不做处理，一般用于界面上只出现该提示，不建议用于连续出现不同位置提示） |
- | type | 提示类型：0，这个提示与持续提示ComOngoingTip同时出现的时候，优先显示他，需要暂时隐藏持续性提示，等他消失了，再显示持续性提示;1，该类提示只会同时显示两个，1表示第一个，2表示第二个。同类型覆盖 |
- | title | 标题，一般都需要填，除非是只有主文本的提示 |
- | subContent | 副文本，只能和标题搭配使用，不能只填副文本 |
- | constName | 程序常量名，暂时没用,和05\_通用提示表共用一份常量，一般程序定义，需注意不能重复。可以在CommonTipConst查重 |
- | constName | 程序常量名，和05\_通用提示表共用一份常量，一般程序定义，需注意不能重复。可以在CommonTipConst查重 |
- 为1，普通样式（移动端：无查看（跳转到背包进行定位物品），PC：无对应快捷键跳转）;
- 为2，重要物品样式（可查看，有对应快捷键跳转）
- 为1，普通样式（移动端：无查看（跳转到制造对应科技），PC：无对应快捷键跳转）;
- | type | 对应不同控制器，不同样式， <br>0, 情报柜升级;<br>1, 生存评级;<br>2, 一级科技升级完成， <br>3, 石质领地 |

## 案例经验

以下保留原文主体，供 AI 检索和人工回溯。

## 待确认 / AI 推论

- 暂无。

## 检索关键词

1.通用文本提示、2.战斗弱提示、3.常驻准星提示、4.短触发提示、5.获得物品提示、6.左侧信息弹窗提示、信息提示系统、提示样式和位置参考、提示系统整理、提示队列、配置表

## 来源定位

- 文件：提示系统整理.md
- 位置：按原文标题和段落回溯。

---

## 原文主体

# 提示系统整理

### 提示样式和位置参考

#### 1.通用文本提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/b09f5bf4-51d9-4d54-a8d9-e78ab0ec0537.png)

#### 2.战斗弱提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/28c5c4bc-0418-4353-b068-e0d4d958e29a.png)

#### 3.常驻准星提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/3e180e43-c0b0-403c-b592-19dea2b5fbc2.png)

#### 4.短触发提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/65317fcd-ea3b-478a-a133-58839c6a783d.png)

#### 5.获得物品提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/a3a48d3b-1a5d-4273-841a-01997252797d.png)

#### 6.左侧信息弹窗提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/19efd486-5ca2-42bb-9bbc-31e2764f41d1.png)

#### 7.NPC文本提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/7044974a-1110-46ab-bd2f-f688852a991d.png)

#### 8.持续性提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/5e4a7844-e202-459b-8adb-94eb0c8014e0.png)

#### 9.情报柜和科技升级等提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/de1b657b-4500-4fff-90ec-b64f132971eb.png)

#### 10.抄家成功提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/e767c37f-9f45-4c8d-aef7-d76fc04a9f50.png)

#### 11.任务提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/f9581156-630f-4ec5-9b08-c9dd2ffb19a6.png)

#### 12.奖励提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/3a656f46-5f90-40d1-92f6-2d8cdc375a24.png)

#### 13.新手键位引导提示

![70b27fc6395a4fc88075721a330351e5.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/af008878-2a6b-404a-82b9-6ca4639630f0.png)

#### GM指令

点击该GM指令，将显示上面相关提示（注：需在局内使用）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/b0baefe0-77a0-4e4d-bd4b-782928ca6c26.png)![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/f2d0d0e2-d721-4987-b319-15d986511e22.png)

### 配置相关

#### 05\_通用提示表插入链接

涉及提示：通用文本提示、战斗弱提示、物品获得提示、常驻准星提示、Npc文本提示（注：**不支持修改背景图片，支持修改背景颜色，使用**![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/73e63bbf-e615-4606-8a2e-712f06e3337e.png)**这种样式**）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/c406abb4-5d93-4e67-8f55-851919baf48a.png)

| 配置参数 | 说明 |
| --- | --- |
| id | 提示id |
| type | 已没有使用 |
| title | 已没有使用 |
| iconbackground | 已没有使用 |
| text | 提示内容文案 |
| constName | 程序常量名，代码调用的常量名 |
| time | 提示消失时间 |
| CD | 不再显示CD时间，填了后相同提示在CD内不会再展示，如果你发现某个提示出现后，在一段时间不会再出现了，检查下这个配置 |
| icon | Icon资源 |
| iconColor | Icon颜色 |
| bgColor | 底板颜色 |
| titleColor | 标题字体颜色 |
| fontColor | 文案字体颜色 |
| audioEvent | 音效配置，配置了就会在提示出现的时候播放对应音效 |
| isGuideHide | 是否在引导教学隐藏，需要在设置中将设置为关才能进行隐藏![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/8a11d62c-e285-4f7a-a479-69e4d4bbd780.png) |
| ToMoveDownTip | 从屏幕置顶往下移动像素（填0或者空不做处理，一般用于界面上只出现该提示，不建议用于连续出现不同位置提示） |

#### 大厅杂项/错误码.xlsx

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/4e58ee23-f180-46a2-8004-56bd5121dd0a.png)

| 配置参数 | 说明 |
| --- | --- |
| ID | 提示id |
| Module | 涉及到的模块 |
| Annotation | 注释，进行备注 |
| BattleUse | 是否局内使用 |
| style | 填MsgTip，调用通用提示 |
| text | 通用提示文案 |

#### 189\_持续性提示表.xlsx

涉及配置：持续性提示，新手键位引导提示（注：**不支持修改背景图片，支持修改背景颜色。不支持修改表格中只填了标题得文字颜色，会根据是否输入标题，主文本，副文本，选择不同得控制器**）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/46373514-1552-4e54-831a-7b09c15952d0.png)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/a7016d47-d972-44ce-9f19-be605ad16b95.png)

| 配置参数 | 说明 |
| --- | --- |
| ID | 提示id |
| type | 提示类型：0，这个提示与持续提示ComOngoingTip同时出现的时候，优先显示他，需要暂时隐藏持续性提示，等他消失了，再显示持续性提示;1，该类提示只会同时显示两个，1表示第一个，2表示第二个。同类型覆盖 |
| time | 消失时间 |
| title | 标题，一般都需要填，除非是只有主文本的提示 |
| mainContent | 主文本，支持只填主文本，一般情况下和标题搭配起来使用 |
| subContent | 副文本，只能和标题搭配使用，不能只填副文本 |
| showTime | 倒计时显示时长，一定是搭配副文本使用，显示在副文本里 |
| icon | icon资源 |
| iconColor | icon颜色 |
| bgColor | 底板颜色 |
| titleColor | 标题字体颜色 |
| mainContentColor | 主文本颜色 |
| subContentColor | 副文本颜色 |

#### 192\_短触发目标提示表

涉及提示：短触发提示（注：**支持修改背景图片，背景颜色**）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/5b3e575a-aa4c-4416-8ff5-5d537c63dcf0.png)

| 配置参数 | 说明 |
| --- | --- |
| id | 提示ID |
| type | 提示样式，填0：任务为这个样式![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/667b246f-acd2-4109-9160-96d11569b6cc.png)<br>填 1：炸家阶段为这个样式<br>![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/d339a58d-5a73-4880-b1c5-289bc274e442.png) |
| title | 标题 |
| constName | 程序常量名，暂时没用,和05\_通用提示表共用一份常量，一般程序定义，需注意不能重复。可以在CommonTipConst查重 |
| time | 消失时间 |
| icon | Icon资源路径 |
| BGUrl | 背景资源路径 |
| titleColor | 标题字体颜色 |
| BGColor | 默认填入#FFFFFF，不填为黑色 |
| isGuideHide | 是否在引导教学隐藏，需要在设置中将设置为关才能进行隐藏![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/8a11d62c-e285-4f7a-a479-69e4d4bbd780.png) |
| audioEvent | 音效配置，配置了就会在提示出现的时候播放对应音效 |

#### 193\_侧弹窗提示表

涉及提示：侧弹窗提示，侧弹窗倒计时提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/a6fc2cdd-5e45-48ba-a402-2e6e3f82f209.png)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/fd60c2d1-57fc-44bd-bf81-079a400cd3fa.png)

| 配置参数 | 说明 |
| --- | --- |
| id | 提示ID |
| name | 提示名称 |
| type | 提示样式 |
| title | 标题 |
| text | 文案 |
| constName | 程序常量名，和05\_通用提示表共用一份常量，一般程序定义，需注意不能重复。可以在CommonTipConst查重 |
| time | 消失时间 |
| CD | 不在显示CD |
| icon | Icon资源 |
| iconbackground | 强提示背景 |
| iconColor | Icon颜色 |
| bgColor | 底板颜色 |
| titleColor | 标题字体颜色 |
| fontColor | 文案字体颜色 |
| isShowTime | 是否显示通用玩法提示倒计时 |
| isGuideHide | 是否在引导教学隐藏，需要在设置中将设置为关才能进行隐藏![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/8a11d62c-e285-4f7a-a479-69e4d4bbd780.png) |

#### 41\_道具\_总表

涉及提示：侧弹窗提示（首次获得是否显示引导通知ID，

为0，不为首次获得，不显示提示 ；

为1，普通样式（移动端：无查看（跳转到背包进行定位物品），PC：无对应快捷键跳转）;

为2，重要物品样式（可查看，有对应快捷键跳转）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/1ae7c11d-65ab-4253-89b4-a495b948f87e.png?x-oss-process=image/crop,x_52,y_25,w_1850,h_876/ignore-error,1)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/929021a9-5ec5-4be1-b51b-526f3edff485.png)

#### 97\_系统\_研发表（原科技表）![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/93ae2bc6-ffb5-47a2-9b58-35a49acefade.png)

涉及提示：侧弹窗提示（首次获得是否显示引导通知ID，

为0，不为首次获得，不显示提示 ；

为1，普通样式（移动端：无查看（跳转到制造对应科技），PC：无对应快捷键跳转）;

为2，重要物品样式（可查看，有对应快捷键跳转）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/8a18c2ff-4c2e-4455-8d8f-0101f125a53c.png)

#### 05\_通用提示表\_重要节点提示sheet

涉及提示：情报柜和科技提示(**优先级高于持续性队列，如果有持续性消息，或者通用提示消息，均会被覆盖隐藏。只显示该提示。提示消失后才会出现其他通用提示和持续性提示，在侧弹窗队列当中**)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/3717e88d-a407-4308-826b-cda30678a01e.png)

| 配置参数 | 说明 |
| --- | --- |
| id | 可通过id显示提示 |
| type | 对应不同控制器，不同样式，  <br>0,  情报柜升级;<br>1,  生存评级;<br>2,  一级科技升级完成，  <br>3,  石质领地 |
| title | 标题 |
| text | 提示文本 |
| time | 显示时间 |
| interrupt | 是否强制打断上一个 |

#### 05\_通用提示表\_重要成就提示sheet

涉及提示：抄家相关提示(**优先级高于持续性队列，如果有持续性消息，或者通用提示消息，均会被覆盖隐藏。只显示该提示。提示消失后才会出现其他通用提示和持续性提示，在短触发队列当中**)

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/7d2aeb89-adb9-4382-bafa-c7805253b587.png)

| 配置参数 | 说明 |
| --- | --- |
| id | 可通过id显示提示 |
| title | 标题 |
| text | 提示文本 |
| time | 显示时间 |

### FGUI资源路径

#### 1.通用文本提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/4eef1ac6-a101-4d38-8340-2373fe3067de.png)

#### 2.战斗弱提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/f4fa3cdb-c0fb-4756-85c9-0d66dab31213.png)

#### 3.常驻准星提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/f45aa297-e3f3-4b91-8df9-071998879acc.png)

#### 4.短触发提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/3a2fd810-ab9c-4d15-b006-d56134fd5ba1.png)

#### 5.获得物品提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/4d16506c-1838-4325-8d4c-9662f615c993.png)

#### 6.左侧信息弹窗提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/fdec9e24-2ee8-4570-afa8-8e4db18d7a36.png)

#### 7.Npc文本提示（目前只给新手引导使用）![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/791729ea-22d1-4050-b062-40febb47597c.png)

#### 8.持续性提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/6bfbbab3-58cc-48eb-846f-489dd6067789.png)

#### 9.情报柜和科技升级等提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/6bf2060a-12a2-434e-946b-635c697461d4.png)

#### 10.抄家成功提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/29654231-b687-404e-8d32-6f67fe74b745.png)

#### 11.任务提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/51275741-96bb-4d7f-b9d5-dca31bf2a6c0.png)

#### 12.奖励提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/64aac406-9ec4-4da8-9d9e-c8975ae26afa.png)

#### 13.新手键位引导提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/cdb96b6c-46d6-414e-8570-f38b8c5970eb.png)

### 程序调用接口

#### 1.通用即时提示

（调用：Mc.MsgTips.+（对应提示方法），例如： Mc.MsgTips.ShowRealtimeWeakTip(24266)）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/dd9a7634-4e81-40fb-9640-a74701645b32.png)

#### 1.1错误码提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/d252144e-da2c-447e-ad95-daff92cd9bc8.png)

#### 2.战斗弱提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/0d61632a-e09c-4df2-b1fa-2ea83db1f64a.png)

#### 3.常驻准星提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/0fb76f4a-5f01-4537-92c7-d86b5e35813c.png)

#### 4.短触发提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/dde6aa28-b76a-45d7-accd-85c17f624037.png)

#### 5.获得道具

（一般情况下无需调用，服务器发了就会走这个）![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/4fdcc155-f19e-4e0f-b1c4-a1bb97f3fb8d.png)

#### 6.左侧信息弹窗提示![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/c668281b-f8f8-4c3b-8596-ab30505ee250.png)

#### 6.1科技提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/f07c2a1b-6a93-4ff5-8741-85452c4181c5.png?x-oss-process=image/crop,x_0,y_0,w_2005,h_638/ignore-error,1)

#### 6.2物品提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/d71cd844-d826-4302-ba7d-d25f28042c3c.png?x-oss-process=image/crop,x_0,y_0,w_1866,h_592/ignore-error,1)

#### 7.npc文本提示（目前只给新手引导使用）

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/5f686ce6-8bd0-47d3-b26e-b0f77b2821eb.png)

#### 8.持续性提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/51b17c2d-468c-4e6a-9c67-288d98949937.png)

#### 9.情报柜和科技升级等提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/43c442af-2ff9-4743-9c8d-056f5292055c.png)

#### 10.抄家成功提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/75b66680-ed13-433a-947f-b49f0f2b5031.png)

#### 11.任务提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/07372f3d-df30-468e-9b1a-4e24cf445ac8.png)

#### 12.奖励提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/7accc52d-dc97-4dab-91b2-be919ef2f650.png)

#### 13.新手键位引导提示

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/3BMqYybjx4ppKqwZ/img/10e2d3d5-c17b-4a45-8722-a2ebd118faed.png)
