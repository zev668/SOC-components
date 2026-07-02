const http = require('http');

const PORT = Number(process.env.SOC_UXD_BRIDGE_PORT || 8787);
const HOST = '127.0.0.1';
const UPSTREAM_URL = process.env.SOC_UXD_GATEWAY_URL || 'http://token.wd.com/v1/chat/completions';
const ALLOWED_ORIGINS = new Set([
  'https://zev668.github.io',
  'http://127.0.0.1:8123',
  'http://localhost:8123',
]);

function corsHeaders(origin) {
  const allowOrigin = ALLOWED_ORIGINS.has(origin) ? origin : 'https://zev668.github.io';
  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Private-Network': 'true',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function sendJson(res, status, origin, body) {
  res.writeHead(status, {
    ...corsHeaders(origin),
    'Content-Type': 'application/json; charset=utf-8',
  });
  res.end(JSON.stringify(body));
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return Buffer.concat(chunks).toString('utf8');
}

async function proxyChat(req, res, origin) {
  const body = await readBody(req);
  const upstream = await fetch(UPSTREAM_URL, {
    method: 'POST',
    headers: {
      'Content-Type': req.headers['content-type'] || 'application/json',
      'Authorization': req.headers.authorization || '',
    },
    body,
  });
  const text = await upstream.text();
  res.writeHead(upstream.status, {
    ...corsHeaders(origin),
    'Content-Type': upstream.headers.get('content-type') || 'application/json; charset=utf-8',
  });
  res.end(text);
}

const server = http.createServer(async (req, res) => {
  const origin = req.headers.origin || '';
  if (req.method === 'OPTIONS') {
    res.writeHead(204, corsHeaders(origin));
    res.end();
    return;
  }
  if (req.method === 'GET' && req.url === '/health') {
    sendJson(res, 200, origin, { ok: true, upstream: UPSTREAM_URL });
    return;
  }
  if (req.method === 'POST' && req.url === '/v1/chat/completions') {
    try {
      await proxyChat(req, res, origin);
    } catch (error) {
      sendJson(res, 502, origin, {
        error: {
          message: `本机连接服务无法访问公司模型网关：${error && error.message ? error.message : String(error)}`,
        },
      });
    }
    return;
  }
  sendJson(res, 404, origin, { error: { message: 'Not found' } });
});

server.listen(PORT, HOST, () => {
  console.log(`SOC UXD local bridge listening on http://${HOST}:${PORT}`);
  console.log(`Forwarding requests to ${UPSTREAM_URL}`);
});
