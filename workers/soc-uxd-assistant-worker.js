const DEFAULT_ALLOWED_ORIGIN = "https://zev668.github.io";

function corsHeaders(origin, env) {
  const allowed = env.ALLOWED_ORIGIN || DEFAULT_ALLOWED_ORIGIN;
  const allowOrigin = origin === allowed ? origin : allowed;
  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin"
  };
}

function jsonResponse(body, status, origin, env) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...corsHeaders(origin, env),
      "Content-Type": "application/json; charset=utf-8"
    }
  });
}

function compactContexts(contexts) {
  return (Array.isArray(contexts) ? contexts : []).slice(0, 9).map((item, index) => {
    const title = String(item.title || `来源 ${index + 1}`).slice(0, 120);
    const file = String(item.file || "").slice(0, 160);
    const href = String(item.href || "").slice(0, 240);
    const text = String(item.text || "").slice(0, 1400);
    return `【${index + 1}】${title}\n文件：${file}\n链接：${href}\n片段：${text}`;
  });
}

function extractResponseText(data) {
  if (typeof data.output_text === "string") return data.output_text;
  const parts = [];
  for (const item of data.output || []) {
    for (const content of item.content || []) {
      if (content.type === "output_text" && content.text) parts.push(content.text);
    }
  }
  return parts.join("\n").trim();
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin, env) });
    }
    if (request.method !== "POST") {
      return jsonResponse({ error: "Method not allowed" }, 405, origin, env);
    }
    if (!env.OPENAI_API_KEY) {
      return jsonResponse({ error: "Server is missing its OpenAI API key." }, 500, origin, env);
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return jsonResponse({ error: "Invalid JSON body." }, 400, origin, env);
    }

    const question = String(payload.question || "").trim();
    const contexts = compactContexts(payload.contexts);
    if (!question) {
      return jsonResponse({ error: "Question is required." }, 400, origin, env);
    }
    if (!contexts.length) {
      return jsonResponse({ error: "At least one context snippet is required." }, 400, origin, env);
    }

    const input = [
      {
        role: "system",
        content:
          "你是 SOC UXD 知识库问答助手。只依据用户提供的知识库片段回答；如果依据不足，先说明不足，再给出需要补充的资料。回答要简洁、可执行，并在关键结论后标注来源编号，例如【1】。"
      },
      {
        role: "user",
        content: `问题：${question}\n\n知识库片段：\n${contexts.join("\n\n")}`
      }
    ];

    const upstream = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: env.OPENAI_MODEL || "gpt-4.1-mini",
        input
      })
    });

    const data = await upstream.json().catch(() => ({}));
    if (!upstream.ok) {
      return jsonResponse(
        { error: data.error?.message || `OpenAI request failed with ${upstream.status}.` },
        upstream.status,
        origin,
        env
      );
    }

    return jsonResponse({ answer: extractResponseText(data), rawId: data.id || "" }, 200, origin, env);
  }
};
