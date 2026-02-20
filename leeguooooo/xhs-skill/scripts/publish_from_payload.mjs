#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { readFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function usage() {
  return `publish_from_payload

Goal:
  Read data/publish_payload*.json and run a serial publish flow via agent-browser:
  open -> ensure 图文 -> upload -> fill title -> fill ProseMirror body -> (optional) publish -> readback checks.

Usage:
  node ./scripts/publish_from_payload.mjs --payload ./data/publish_payload.json [--mode hot] [--session xhs] [--confirm] [--json]

Notes:
  - By default this script DOES NOT click "发布". Use --confirm to actually submit.
  - It will hard-fail if title/body contain link-like text (http/www/domain).
  - It appends hashtags into the body to avoid fragile tag widgets.
`;
}

function str(v) {
  return String(v || '').trim();
}

function containsLinkLike(text) {
  const s = String(text || '').trim();
  if (!s) return false;
  if (/https?:\/\//i.test(s)) return true;
  if (/www\./i.test(s)) return true;
  if (/\b[a-z0-9-]+\.(com|cn|net|org|io|me|co|app|dev)\b/i.test(s)) return true;
  return false;
}

function normalizeBodyText(body) {
  // JSON payload may contain literal "\\n" (two chars). Convert to actual newlines.
  return String(body || '').replaceAll('\\n', '\n');
}

function uniqHashtags(tags) {
  const out = [];
  const seen = new Set();
  for (const t of tags) {
    const v = str(t);
    if (!v) continue;
    const x = v.startsWith('#') ? v : `#${v}`;
    const k = x.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k);
    out.push(x);
  }
  return out;
}

function parseFirstJsonObject(text) {
  const s = String(text || '').trim();
  if (!s) return null;
  const i = s.indexOf('{');
  const j = s.lastIndexOf('}');
  if (i < 0 || j <= i) return null;
  try {
    return JSON.parse(s.slice(i, j + 1));
  } catch {
    return null;
  }
}

function run(cmd, args, { stdinText } = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: ['pipe', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    p.stdout.on('data', (d) => (out += d));
    p.stderr.on('data', (d) => (err += d));
    p.on('error', reject);
    p.on('close', (code) => {
      resolve({ code: code ?? 1, stdout: out, stderr: err });
    });
    if (stdinText) p.stdin.write(stdinText);
    p.stdin.end();
  });
}

async function ab(session, args, { allowFail = false } = {}) {
  const full = [];
  if (session) full.push('--session', session);
  full.push(...args);
  const r = await run('agent-browser', full);
  if (!allowFail && r.code !== 0) {
    const msg = `agent-browser failed: ${args.join(' ')}\n${r.stderr || r.stdout}`;
    throw new Error(msg.trim());
  }
  return r;
}

function extractRefsFromSnapshotJson(obj) {
  // agent-browser snapshot --json output formats have changed over time.
  // Newer builds may return: { success:true, data:{ refs:{ e1:{name,role}, ... }, snapshot:"... [ref=e1]" } }
  // Older builds may embed refs as "@e123" tokens inside a tree. Normalize both to "@eN".
  if (obj && typeof obj === 'object' && obj.data && typeof obj.data === 'object') {
    const refsMap = obj.data.refs;
    if (refsMap && typeof refsMap === 'object' && !Array.isArray(refsMap)) {
      const out = [];
      for (const [k, v] of Object.entries(refsMap)) {
        const key = String(k || '').trim();
        if (!/^e\d+$/i.test(key)) continue;
        out.push({
          ref: `@${key}`,
          role: typeof v?.role === 'string' ? v.role : undefined,
          name:
            typeof v?.name === 'string'
              ? v.name
              : typeof v?.text === 'string'
                ? v.text
                : typeof v?.label === 'string'
                  ? v.label
                  : undefined,
        });
      }
      if (out.length) return out;
    }
  }

  const out = [];
  const seen = new Set();
  const maxNodes = 5000;
  let visited = 0;

  const push = (ref, meta) => {
    if (!ref || typeof ref !== 'string') return;
    let r = ref.trim();
    if (/^e\d+$/i.test(r)) r = `@${r}`;
    if (!/^@e\d+$/i.test(r)) return;
    if (seen.has(r)) return;
    seen.add(r);
    out.push({ ref: r, ...meta });
  };

  const walk = (v, meta) => {
    if (visited++ > maxNodes) return;
    if (v === null || v === undefined) return;
    const t = typeof v;
    if (t === 'string') {
      // Sometimes refs appear embedded in strings; capture exact tokens only.
      if (/^(@)?e\d+$/i.test(v.trim())) push(v.trim(), meta);
      return;
    }
    if (t !== 'object') return;

    if (Array.isArray(v)) {
      for (const it of v) walk(it, meta);
      return;
    }

    const nextMeta = { ...meta };
    for (const [k, val] of Object.entries(v)) {
      if (k === 'ref' && typeof val === 'string') push(val, nextMeta);
      if (k === 'role' && typeof val === 'string') nextMeta.role = val;
      if ((k === 'name' || k === 'text' || k === 'label') && typeof val === 'string') nextMeta.name = val;
    }

    for (const val of Object.values(v)) walk(val, nextMeta);
  };

  walk(obj, {});
  return out;
}

function pickBestUploadRef(refs) {
  if (!refs.length) return null;
  const score = (r) => {
    const name = String(r.name || '');
    const role = String(r.role || '').toLowerCase();
    let s = 0;
    if (/上传|选择|添加|导入/.test(name)) s += 5;
    if (/图片|图文|封面|相册|照片/.test(name)) s += 3;
    if (/文件|file/i.test(name)) s += 2;
    if (/视频/.test(name)) s -= 6;
    if (role === 'button') s += 2;
    if (role === 'textbox') s += 1;
    return s;
  };
  let best = refs[0];
  let bestScore = score(best);
  for (const r of refs.slice(1)) {
    const sc = score(r);
    if (sc > bestScore) {
      best = r;
      bestScore = sc;
    }
  }
  return best.ref;
}

async function verifyPayload(payloadPath, mode) {
  const verifyScript = path.join(__dirname, 'verify_publish_payload.mjs');
  const r = await run(process.execPath, [
    verifyScript,
    '--in',
    payloadPath,
    ...(mode ? ['--mode', mode] : []),
    '--json',
  ]);
  const txt = (r.stdout || '').trim();
  const parsed = txt ? parseFirstJsonObject(txt) : null;
  return { code: r.code, result: parsed, raw: { stdout: r.stdout, stderr: r.stderr } };
}

function jsFillProseMirror(body) {
  // Keep it self-contained, no selectors beyond "ProseMirror + contenteditable".
  const b = JSON.stringify(String(body || ''));
  return `
(() => {
  const body = ${b};
  const root =
    document.querySelector('.ProseMirror[contenteditable="true"]') ||
    document.querySelector('[contenteditable="true"].ProseMirror') ||
    document.querySelector('.ProseMirror');
  if (!root) return JSON.stringify({ ok: false, error: 'ProseMirror not found' });
  root.focus();

  // Replace content with <p> per line. This is more stable than execCommand on ProseMirror.
  const lines = body.split('\\n');
  root.innerHTML = '';
  for (const line of lines) {
    const p = document.createElement('p');
    p.textContent = line.length ? line : '\\u00A0';
    root.appendChild(p);
  }

  root.dispatchEvent(new Event('input', { bubbles: true }));
  root.dispatchEvent(new Event('change', { bubbles: true }));

  const readback = (root.innerText || '').trimEnd();
  return JSON.stringify({ ok: true, len: readback.length, has_literal_backslash_n: readback.includes('\\\\n'), readback });
})()
`.trim();
}

function jsReadback() {
  return `
(() => {
  const titleEl =
    document.querySelector('input[maxlength]') ||
    document.querySelector('input[placeholder*="标题"]') ||
    document.querySelector('input[type="text"]');
  const title = titleEl ? String(titleEl.value || '') : '';

  const pm =
    document.querySelector('.ProseMirror[contenteditable="true"]') ||
    document.querySelector('[contenteditable="true"].ProseMirror') ||
    document.querySelector('.ProseMirror');
  const body = pm ? String(pm.innerText || '') : '';

  const fileInputs = Array.from(document.querySelectorAll('input[type="file"]')).map((i) => ({
    accept: i.accept || '',
    multiple: !!i.multiple,
    disabled: !!i.disabled,
    visible: !!(i.offsetWidth || i.offsetHeight || i.getClientRects().length),
  }));

  return JSON.stringify({ ok: true, title, body, body_len: body.trim().length, file_inputs: fileInputs });
})()
`.trim();
}

function jsSelectBestFileInput({ expectMultiple }) {
  const m = expectMultiple ? 'true' : 'false';
  return `
(() => {
  const expectMultiple = ${m};
  const inputs = Array.from(document.querySelectorAll('input[type="file"]'));
  if (!inputs.length) return JSON.stringify({ ok: false, error: 'No input[type=file] found' });

  const visible = (el) => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const norm = (s) => String(s || '').toLowerCase();

  let best = null;
  let bestScore = -1e9;
  let bestIndex = -1;

  for (let i = 0; i < inputs.length; i++) {
    const el = inputs[i];
    if (!el) continue;
    const accept = norm(el.accept);
    const disabled = !!el.disabled;
    const multi = !!el.multiple;
    const vis = visible(el);

    let score = 0;
    if (!disabled) score += 5;
    if (accept.includes('image') || accept.includes('png') || accept.includes('jpg') || accept.includes('jpeg')) score += 4;
    if (accept.includes('video') || accept.includes('mp4') || accept.includes('mov')) score -= 8;
    if (expectMultiple && multi) score += 3;
    if (expectMultiple && !multi) score -= 2;
    if (!expectMultiple && !multi) score += 1;
    if (vis) score += 1;

    if (score > bestScore) {
      bestScore = score;
      best = el;
      bestIndex = i;
    }
  }

  if (!best) return JSON.stringify({ ok: false, error: 'No suitable file input found' });

  // Tag it so agent-browser upload can target it reliably.
  best.id = 'xhs_skill_upload_input';
  best.setAttribute('data-xhs-skill', 'upload');

  return JSON.stringify({
    ok: true,
    count: inputs.length,
    chosen: {
      index: bestIndex,
      accept: best.accept || '',
      multiple: !!best.multiple,
      disabled: !!best.disabled,
      visible: ${'!!(best.offsetWidth || best.offsetHeight || best.getClientRects().length)'}
    }
  });
})()
`.trim();
}

async function main(argv) {
  const { values } = parseArgs({
    args: argv,
    options: {
      payload: { type: 'string' },
      mode: { type: 'string', default: 'normal' },
      session: { type: 'string' },
      confirm: { type: 'boolean', default: false },
      json: { type: 'boolean', default: true },
      help: { type: 'boolean', default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(usage());
    return;
  }

  const payloadPath = str(values.payload) || './data/publish_payload.json';
  const mode = str(values.mode || 'normal').toLowerCase();
  const session = str(values.session);
  const confirm = !!values.confirm;

  // 1) Validate payload (gate)
  const verified = await verifyPayload(payloadPath, mode === 'hot' ? 'hot' : 'normal');
  if (!verified.result || verified.result.ok !== true) {
    const out = {
      task: 'xhs_publish_auto',
      ok: false,
      stage: 'payload_validate',
      payload: payloadPath,
      verify: verified.result,
    };
    console.log(JSON.stringify(out, null, 2));
    process.exitCode = 2;
    return;
  }

  // 2) Load payload
  const raw = await readFile(payloadPath, 'utf8');
  const payload = JSON.parse(raw);
  const title = str(payload?.post?.title);
  const media = Array.isArray(payload?.post?.media) ? payload.post.media.map((x) => str(x)).filter(Boolean) : [];
  const tags = uniqHashtags(Array.isArray(payload?.post?.tags) ? payload.post.tags : []);
  let body = normalizeBodyText(payload?.post?.body || '');

  // Link ban: absolutely forbid link-like tokens in published fields.
  if (containsLinkLike(title) || containsLinkLike(body) || tags.some((t) => containsLinkLike(t))) {
    const out = {
      task: 'xhs_publish_auto',
      ok: false,
      stage: 'content_gate',
      error: 'Links are forbidden in title/body/tags (risk of ban). Remove http/www/domain-like text.',
    };
    console.log(JSON.stringify(out, null, 2));
    process.exitCode = 2;
    return;
  }

  // Append hashtags to body to avoid fragile tag widget behavior.
  const hashLine = tags.length ? `\n\n${tags.join(' ')}` : '';
  if (hashLine && !body.includes(tags[0])) body += hashLine;

  // 3) Open publish page
  await ab(session, ['open', 'https://creator.xiaohongshu.com/creator/publish']);
  await ab(session, ['wait', '--load', 'networkidle']);

  // 4) Ensure 图文 mode (best-effort)
  const tryTab = async (name) => {
    await ab(session, ['find', 'role', 'tab', 'click', '--name', name], { allowFail: true });
    await ab(session, ['find', 'text', name, 'click'], { allowFail: true });
  };
  await tryTab('图文');
  await tryTab('图文笔记');

  // 5) Preflight: file input should accept images and allow multiple when needed
  const pre = await ab(session, ['eval', jsReadback()]);
  const preJson = parseFirstJsonObject(pre.stdout) || {};
  const inputs = Array.isArray(preJson.file_inputs) ? preJson.file_inputs : [];
  const anyVisible = inputs.find((x) => x && x.visible);
  if (media.length > 1 && anyVisible && anyVisible.multiple === false) {
    // Likely stuck in video tab. Try switching again.
    await tryTab('图文');
    await ab(session, ['wait', 600]);
  }

  // 6) Upload media
  if (media.length === 0) {
    throw new Error('No media in payload. Refuse to publish without images/videos.');
  }

  // Prefer uploading through an actual <input type="file"> (uploading to a button ref will fail).
  // We first select the best candidate input and tag it with a stable id.
  const sel = await ab(session, ['eval', jsSelectBestFileInput({ expectMultiple: media.length > 1 })], { allowFail: true });
  const selJson = parseFirstJsonObject(sel.stdout) || {};
  if (selJson.ok) {
    await ab(session, ['upload', '#xhs_skill_upload_input', ...media]);
  } else {
    // Fallback: try generic selector (agent-browser supports CSS selectors here).
    const r = await ab(session, ['upload', 'input[type=file]', ...media], { allowFail: true });
    if (r.code !== 0) {
      throw new Error(
        `Upload failed: no usable input[type=file]. selector_error=${selJson.error || 'unknown'}`
      );
    }
  }

  await ab(session, ['wait', '--load', 'networkidle']);
  await ab(session, ['wait', Math.min(15000, 1000 * Math.max(2, media.length * 2))]);

  // 7) Fill title (best-effort locators)
  await ab(session, ['find', 'role', 'textbox', 'fill', '--name', '标题', title], { allowFail: true });
  await ab(session, ['find', 'label', '标题', 'fill', title], { allowFail: true });
  await ab(session, ['eval', `(() => { const el=document.querySelector('input[placeholder*="标题"]')||document.querySelector('input[maxlength]'); if(!el) return 'NO_TITLE_INPUT'; el.focus(); el.value=${JSON.stringify(title)}; el.dispatchEvent(new Event('input',{bubbles:true})); return 'OK'; })()`], { allowFail: true });

  // 8) Fill ProseMirror body + immediate readback
  const fill = await ab(session, ['eval', jsFillProseMirror(body)]);
  const fillJson = parseFirstJsonObject(fill.stdout) || {};
  if (!fillJson.ok) {
    throw new Error(`Failed to fill ProseMirror: ${fillJson.error || 'unknown'}`);
  }

  const rb = await ab(session, ['eval', jsReadback()]);
  const rbJson = parseFirstJsonObject(rb.stdout) || {};
  const rbTitle = str(rbJson.title);
  const rbBody = String(rbJson.body || '');

  const rbHasLiteralBackslashN = rbBody.includes('\\n');
  const rbHasLink = containsLinkLike(rbTitle) || containsLinkLike(rbBody) || containsLinkLike(tags.join(' '));

  const contentChecks = {
    title_len: [...rbTitle].length,
    body_len: [...rbBody.trim()].length,
    has_literal_backslash_n: rbHasLiteralBackslashN,
    has_link_like: rbHasLink,
  };

  if (contentChecks.title_len === 0 || contentChecks.body_len < 80) {
    throw new Error('Readback failed: title/body not written correctly (empty or too short). Abort before publish.');
  }
  if (contentChecks.title_len > 20) {
    throw new Error('Readback failed: title > 20 chars. Abort before publish.');
  }
  if (contentChecks.has_literal_backslash_n) {
    throw new Error('Readback failed: body still contains literal "\\\\n". Abort before publish.');
  }
  if (contentChecks.has_link_like) {
    throw new Error('Readback failed: link-like content detected. Abort before publish.');
  }

  // 9) Stop here unless explicitly confirmed
  if (!confirm) {
    const out = {
      task: 'xhs_publish_auto',
      ok: true,
      published: false,
      ready_to_publish: true,
      payload: payloadPath,
      mode,
      content_checks: contentChecks,
      note: 'Run again with --confirm to actually click publish.',
    };
    console.log(JSON.stringify(out, null, 2));
    return;
  }

  // 10) Click publish (strict button name)
  await ab(session, ['find', 'role', 'button', 'click', '--name', '发布'], { allowFail: true });
  await ab(session, ['find', 'role', 'button', 'click', '--name', '发布笔记'], { allowFail: true });
  await ab(session, ['wait', '--load', 'networkidle']);
  await ab(session, ['wait', 1200]);

  const url = await ab(session, ['get', 'url']);
  const resultUrl = str(url.stdout);

  const out = {
    task: 'xhs_publish_auto',
    ok: true,
    published: true,
    verified_after_publish: false,
    result_url: resultUrl || null,
    payload: payloadPath,
    mode,
    content_checks: contentChecks,
    warning:
      'Post-publish readback is best-effort and depends on current creator center routes. If needed, open note manager and re-open edit page to verify.',
  };
  console.log(JSON.stringify(out, null, 2));
}

main(process.argv.slice(2)).catch((e) => {
  const out = { task: 'xhs_publish_auto', ok: false, error: e?.message || String(e) };
  try {
    console.log(JSON.stringify(out, null, 2));
  } catch {
    console.log(String(out.error));
  }
  process.exitCode = 1;
});
