// OpenClaw Canvas Mini App
// Vanilla JS client for Telegram WebApp

(() => {
  const tg = window.Telegram?.WebApp;
  // Apply Telegram theme (light/dark)
  try {
    const theme = tg?.colorScheme || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  } catch (_) {}

  const contentEl = document.querySelector('.content-inner');
  const connDot = document.getElementById('connDot');
  const connText = document.getElementById('connText');
  const lastUpdatedEl = document.getElementById('lastUpdated');

  let jwt = null;
  let ws = null;
  let reconnectTimer = null;
  let lastUpdatedTs = null;
  let relativeTimer = null;

  // ---------- UI Helpers ----------
  function setStatus(state) {
    connDot.classList.remove('connected', 'connecting');
    if (state === 'connected') {
      connDot.classList.add('connected');
      connText.textContent = 'Connected';
    } else if (state === 'connecting' || state === 'reconnecting') {
      connDot.classList.add('connecting');
      connText.textContent = state === 'reconnecting' ? 'Reconnecting…' : 'Connecting…';
    } else {
      connText.textContent = 'Offline';
    }
  }

  function showCenter(message, withSpinner = false, buttonText = null, buttonHandler = null, useCard = true) {
    contentEl.innerHTML = '';
    const wrap = document.createElement('div');
    wrap.className = 'center fade-in';

    let holder = wrap;
    if (useCard) {
      const card = document.createElement('div');
      card.className = 'empty-card';
      wrap.appendChild(card);
      holder = card;
    }

    if (withSpinner) {
      const spinner = document.createElement('div');
      spinner.className = 'spinner';
      holder.appendChild(spinner);
    }

    const text = document.createElement('div');
    text.textContent = message;
    holder.appendChild(text);

    if (buttonText && buttonHandler) {
      const btn = document.createElement('button');
      btn.className = 'button';
      btn.textContent = buttonText;
      btn.addEventListener('click', buttonHandler);
      holder.appendChild(btn);
    }

    contentEl.appendChild(wrap);
  }

  function formatRelative(ts) {
    if (!ts) return '—';
    const delta = Math.max(0, Date.now() - ts);
    const sec = Math.floor(delta / 1000);
    if (sec < 5) return 'just now';
    if (sec < 60) return `${sec}s ago`;
    const min = Math.floor(sec / 60);
    if (min < 60) return `${min}m ago`;
    const hr = Math.floor(min / 60);
    if (hr < 24) return `${hr}h ago`;
    const days = Math.floor(hr / 24);
    return `${days}d ago`;
  }

  function updateLastUpdated(ts) {
    lastUpdatedTs = ts || Date.now();
    lastUpdatedEl.textContent = `Last updated ${formatRelative(lastUpdatedTs)}`;
    clearInterval(relativeTimer);
    relativeTimer = setInterval(() => {
      lastUpdatedEl.textContent = `Last updated ${formatRelative(lastUpdatedTs)}`;
    }, 30000);
  }

  // ---------- Markdown Renderer (minimal) ----------
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function renderMarkdown(md) {
    // Simple, safe markdown conversion
    const lines = md.split('\n');
    let html = '';
    let inCodeBlock = false;
    let listType = null; // 'ul' | 'ol'

    const closeList = () => {
      if (listType) {
        html += `</${listType}>`;
        listType = null;
      }
    };

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];

      // Code block (```) toggle
      if (line.trim().startsWith('```')) {
        if (!inCodeBlock) {
          closeList();
          inCodeBlock = true;
          html += '<pre><code>';
        } else {
          inCodeBlock = false;
          html += '</code></pre>';
        }
        continue;
      }

      if (inCodeBlock) {
        html += `${escapeHtml(line)}\n`;
        continue;
      }

      // Headings
      if (/^###\s+/.test(line)) {
        closeList();
        html += `<h3>${escapeHtml(line.replace(/^###\s+/, ''))}</h3>`;
        continue;
      }
      if (/^##\s+/.test(line)) {
        closeList();
        html += `<h2>${escapeHtml(line.replace(/^##\s+/, ''))}</h2>`;
        continue;
      }
      if (/^#\s+/.test(line)) {
        closeList();
        html += `<h1>${escapeHtml(line.replace(/^#\s+/, ''))}</h1>`;
        continue;
      }

      // Lists
      const ulMatch = /^-\s+/.test(line);
      const olMatch = /^\d+\.\s+/.test(line);
      if (ulMatch || olMatch) {
        const type = ulMatch ? 'ul' : 'ol';
        if (listType && listType !== type) closeList();
        if (!listType) {
          listType = type;
          html += `<${listType}>`;
        }
        const itemText = line.replace(ulMatch ? /^-\s+/ : /^\d+\.\s+/, '');
        html += `<li>${inlineMarkdown(escapeHtml(itemText))}</li>`;
        continue;
      } else {
        closeList();
      }

      // Paragraphs / blank
      if (line.trim() === '') {
        html += '<br />';
      } else {
        html += `<p>${inlineMarkdown(escapeHtml(line))}</p>`;
      }
    }

    closeList();
    return html;
  }

  function inlineMarkdown(text) {
    // bold **text**
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // italic *text*
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    // inline code `code`
    text = text.replace(/`(.+?)`/g, '<code>$1</code>');
    return text;
  }

  // ---------- Rendering ----------
  function renderA2UI(container, a2uiPayload) {
    // Optional A2UI runtime hook. If present, use it. Otherwise show JSON.
    const runtime = window.OpenClawA2UI || window.A2UI || null;
    if (runtime && typeof runtime.render === 'function') {
      try {
        runtime.render(container, a2uiPayload);
        return;
      } catch (_) {
        // fall through to JSON
      }
    }
    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(a2uiPayload, null, 2);
    container.appendChild(pre);
  }

  function renderPayload(payload) {
    if (!payload || payload.type === 'clear') {
      showCenter('Waiting for content…');
      return;
    }

    const { format, content } = payload;
    contentEl.innerHTML = '';

    const container = document.createElement('div');
    container.className = 'fade-in';

    if (format === 'html') {
      // Trusted HTML from server (agent only)
      container.innerHTML = content || '';
      // Execute inline scripts (Telegram WebView doesn't run scripts from innerHTML)
      container.querySelectorAll('script').forEach((oldScript) => {
        const s = document.createElement('script');
        if (oldScript.src) s.src = oldScript.src;
        s.type = oldScript.type || 'text/javascript';
        s.text = oldScript.textContent || '';
        oldScript.replaceWith(s);
      });
    } else if (format === 'markdown') {
      container.innerHTML = renderMarkdown(content || '');
    } else if (format === 'a2ui') {
      renderA2UI(container, content || {});
    } else {
      // text
      const pre = document.createElement('pre');
      pre.textContent = content || '';
      container.appendChild(pre);
    }

    contentEl.appendChild(container);
    updateLastUpdated(Date.now());
  }

  // ---------- Auth + Networking ----------
  async function authenticate() {
    const initData = tg?.initData || '';
    try {
      const res = await fetch('/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initData }),
      });

      if (!res.ok) throw new Error('auth_failed');
      const data = await res.json();
      if (!data?.token) throw new Error('no_token');
      jwt = data.token;
      return true;
    } catch (e) {
      return false;
    }
  }

  async function fetchState() {
    try {
      const res = await fetch(`/state?token=${encodeURIComponent(jwt)}`);
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  function connectWS() {
    if (!jwt) return;

    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${proto}//${location.host}/ws?token=${encodeURIComponent(jwt)}`;

    setStatus('connecting');
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'ping') return;
        if (msg.type === 'clear') {
          renderPayload({ type: 'clear' });
          return;
        }
        if (msg.type === 'canvas') {
          renderPayload(msg);
        }
      } catch (e) {
        // ignore malformed message
      }
    };

    ws.onerror = () => {
      setStatus('reconnecting');
      showCenter('Connection lost. Reconnecting…', true);
    };

    ws.onclose = () => {
      setStatus('reconnecting');
      showCenter('Connection lost. Reconnecting…', true);
      scheduleReconnect();
    };
  }

  function scheduleReconnect() {
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      connectWS();
    }, 3000);
  }

  // ---------- Boot ----------
  async function boot() {
    setStatus('connecting');
    showCenter('Connecting…', true, null, null, false);

    const authed = await authenticate();
    if (!authed) {
      setStatus('disconnected');
      showCenter('Access denied', false, 'Close', () => tg?.close?.());
      return;
    }

    // Fetch current state before WS connect
    const state = await fetchState();
    if (state) renderPayload(state);
    else showCenter('Waiting for content…');

    connectWS();
  }

  boot();
})();
