// ── Gateway WebSocket 連線管理 ──

import WebSocket from 'ws';

let gw = null;
let gwReady = false;
let gwPending = new Map();
let gwSeqId = 1;
let gwSessionKey = null;
let reconnectTimer = null;

let gatewayUrl = '';
let gatewayToken = '';
let configSessionKey = null;  // config 定義的 session key
let onChatEvent = null;  // 外部註冊的 chat 事件回呼

export function initGateway({ url, token, sessionKey, onChat }) {
  gatewayUrl = url;
  gatewayToken = token;
  configSessionKey = sessionKey;
  onChatEvent = onChat;
  connect();
}

export function isReady() { return gwReady; }
export function getSessionKey() { return gwSessionKey; }

function connect() {
  if (gw) { try { gw.close(); } catch {} }
  gwReady = false;

  gw = new WebSocket(gatewayUrl, { origin: 'http://localhost:8001' });

  gw.on('open', () => console.log('[GW] connected'));

  gw.on('message', (raw) => {
    const msg = JSON.parse(raw.toString());

    if (msg.event === 'connect.challenge') {
      gw.send(JSON.stringify({
        type: 'req',
        id: String(gwSeqId++),
        method: 'connect',
        params: {
          minProtocol: 3, maxProtocol: 3,
          client: { id: 'openclaw-control-ui', version: 'dev', platform: 'node', mode: 'webchat', instanceId: 'jarvis-backend-1' },
          role: 'operator',
          scopes: ['operator.admin', 'operator.approvals', 'operator.pairing'],
          auth: { token: gatewayToken },
          caps: [], userAgent: 'jarvis-backend/1.0', locale: 'zh-TW',
        },
      }));
      return;
    }

    if (msg.type === 'res' && msg.id) {
      if (msg.ok && msg.payload?.type === 'hello-ok') {
        gwReady = true;
        gwSessionKey = msg.payload?.session?.key || null;
        console.log('[GW] authenticated, session:', gwSessionKey);
      }
      const pending = gwPending.get(msg.id);
      if (pending) {
        gwPending.delete(msg.id);
        msg.ok ? pending.resolve(msg.payload || msg.result || {}) : pending.reject(msg.error || { message: 'unknown error' });
      }
      return;
    }

    if (msg.type === 'event' && msg.event === 'chat') {
      if (msg.payload?.sessionKey === configSessionKey && onChatEvent) {
        const p = msg.payload;
        const u = p.message?.usage;
        console.log(`[GW] jarvis: state=${p.state} model=${p.message?.model || '-'} usage=${u ? JSON.stringify(u) : 'none'}`);
        onChatEvent(msg.payload);
      }
    }

    const quietEvents = ['health', 'connect.challenge', 'tick', 'agent'];
    if (msg.type === 'event' && !quietEvents.includes(msg.event)) {
      console.log('[GW] event:', msg.event);
    }
  });

  gw.on('close', (code, reason) => {
    console.log('[GW] closed:', code, reason?.toString());
    gwReady = false;
    for (const [, pending] of gwPending) pending.reject(new Error('gateway disconnected'));
    gwPending.clear();
    if (!reconnectTimer) {
      reconnectTimer = setTimeout(() => { reconnectTimer = null; connect(); }, 3000);
    }
  });

  gw.on('error', (err) => console.error('[GW] error:', err.message));
}

export function gwRequest(method, params) {
  return new Promise((resolve, reject) => {
    if (!gw || !gwReady) return reject(new Error('gateway not connected'));
    const id = String(gwSeqId++);
    gwPending.set(id, { resolve, reject });
    gw.send(JSON.stringify({ type: 'req', id, method, params }));
    setTimeout(() => {
      if (gwPending.has(id)) { gwPending.delete(id); reject(new Error('timeout')); }
    }, 60000);
  });
}
