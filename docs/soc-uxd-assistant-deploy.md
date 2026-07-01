# SOC UXD 问答助手部署说明

SOC UXD 网站发布在 GitHub Pages 上，是静态页面。问答助手不能把服务端密钥写进前端，所以采用两段式：

1. 前端在浏览器里检索 `soc-uxd.html` 内置的知识库文档和组件清单，选出相关片段。
2. 前端把“问题 + 相关片段”发给安全代理，由代理调用 OpenAI Responses API。

## 前端配置

打开网站后，点右上角“问答助手”，在底部填写代理地址并保存。

也可以在浏览器控制台写入：

```js
localStorage.setItem("socAssistantApiUrl", "https://your-worker.example.workers.dev");
```

没有配置代理地址时，助手仍会展示本地检索依据，但不会生成综合回答。

## Cloudflare Worker 部署

代理模板在：

```text
workers/soc-uxd-assistant-worker.js
```

部署后需要配置环境变量：

```text
OPENAI_API_KEY=你的服务端密钥
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGIN=https://zev668.github.io
```

`OPENAI_MODEL` 可以按项目预算和质量要求调整；前端不依赖具体模型名。

## 请求格式

前端会向代理发送：

```json
{
  "question": "Toast 和强提示怎么选？",
  "siteUrl": "https://zev668.github.io/SOC-components/soc-uxd.html",
  "contexts": [
    {
      "title": "信息提示系统",
      "file": "web-docs/prompt-system.page.md",
      "href": "data/soc-uxd/web-docs/prompt-system.page.md",
      "text": "知识库片段..."
    }
  ]
}
```

代理返回：

```json
{
  "answer": "基于知识库的回答...",
  "rawId": "resp_..."
}
```

## 安全约束

- 服务端密钥只放在 Worker / Serverless 环境变量里。
- 前端只保存代理 URL，不保存服务端密钥。
- 代理默认只允许 `https://zev668.github.io` 调用。
- 回答提示词要求“只依据传入片段回答”，避免脱离知识库自由发挥。

## 官方参考

- Responses API: https://developers.openai.com/api/reference/responses/overview/
- OpenAI API quickstart: https://developers.openai.com/api/docs/quickstart/
