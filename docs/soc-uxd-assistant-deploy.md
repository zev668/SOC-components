# SOC UXD 问答助手部署说明

SOC UXD 网站发布在 GitHub Pages 上，是静态页面。浏览器直接请求 OpenAI 容易遇到跨域或网络拦截，表现为 `Failed to fetch`。因此问答助手采用“本地检索 + 中转转发”的结构：

1. 前端先在浏览器里检索 `soc-uxd.html` 内置的知识库文档和组件清单。
2. 前端把“问题 + 相关片段 + 使用者自己的 OpenAI API Key”发给 SOC UXD 问答中转服务。
3. 中转服务只转发请求到 OpenAI Responses API，不保存使用者的 Key。

## 前端配置

打开网站后，点右上角“问答助手”：

- `我的 OpenAI API Key`：由使用者输入自己的 Key。
- `模型`：默认 `gpt-4.1-mini`。
- `SOC UXD 问答中转服务地址`：填写部署后的 Worker URL。
- `测试连接`：保存当前 Key、模型和中转地址后，发一个最小请求确认能否连接模型。

也可以在浏览器控制台写入中转地址：

```js
localStorage.setItem("socAssistantProxyUrl", "https://your-worker.example.workers.dev");
```

没有中转地址时，助手仍会展示本地检索依据，但不会生成自然语言回答。

## Cloudflare Worker 部署

中转模板在：

```text
workers/soc-uxd-assistant-worker.js
```

Worker 支持两种 Key 来源：

- 推荐：用户在网页里输入自己的 Key，前端通过 `Authorization: Bearer ...` 发给 Worker，Worker 只转发，不保存。
- 可选：如果团队希望统一付费，也可以在 Worker 环境变量配置 `OPENAI_API_KEY` 作为兜底。

可选环境变量：

```text
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGIN=https://zev668.github.io
OPENAI_API_KEY=团队统一 Key，可不填
```

## 请求格式

前端会向中转服务发送：

```json
{
  "model": "gpt-4.1-mini",
  "question": "Toast 和强提示怎么选？",
  "contexts": [
    {
      "title": "信息提示系统",
      "file": "web-docs/prompt-system.page.md",
      "href": "data/soc-uxd/web-docs/prompt-system.page.md",
      "text": "知识库片段..."
    }
  ],
  "input": [
    {
      "role": "system",
      "content": [
        {
          "type": "input_text",
          "text": "你是连接了 SOC UXD 知识库记忆的 ChatGPT..."
        }
      ]
    }
  ]
}
```

请求头：

```text
Authorization: Bearer 使用者自己的 OpenAI API Key
Content-Type: application/json
```

中转返回：

```json
{
  "answer": "基于知识库的回答...",
  "rawId": "resp_..."
}
```

## 安全约束

- 前端默认只把用户 Key 存在当前标签页会话中；勾选“记住到本机浏览器”后才写入本机浏览器。
- 中转服务不保存用户 Key，只使用当前请求头转发。
- Worker 默认只允许 `https://zev668.github.io` 调用。
- 回答提示词要求“只依据传入片段回答”，避免脱离知识库自由发挥。
