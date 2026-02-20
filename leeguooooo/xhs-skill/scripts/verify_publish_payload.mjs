#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { readFile } from 'node:fs/promises';
import { getImageSize } from '../lib/image.mjs';

function usage() {
  return `verify_publish_payload

Usage:
  node ./scripts/verify_publish_payload.mjs --in <payloadJsonPath> [--mode hot] [--json]

Payload JSON example:
{
  "topic": "今日热点：......",
  "source": {
    "name": "央视新闻",
    "url": "https://...",
    "date": "2026-02-12"
  },
  "post": {
    "title": "标题",
    "body": "正文",
    "tags": ["#热点", "#小红书"],
    "media": ["/abs/path/cover.png"]
  }
}
`;
}

function todayISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function isScreenshotLike(path) {
  if (!path) return false;
  const s = String(path).toLowerCase();
  return (
    s.includes('screenshot') ||
    s.includes('screen_shot') ||
    s.includes('xhs_login') ||
    s.includes('login_qr') ||
    s.includes('after_click')
  );
}

function str(v) {
  return String(v || '').trim();
}

function isValidDateYYYYMMDD(v) {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

function isHttpUrl(v) {
  return /^https?:\/\//i.test(v);
}

function pickArray(v) {
  return Array.isArray(v) ? v : [];
}

function hasLiteralBackslashN(body) {
  const s = String(body || '');
  return s.includes('\\n');
}

function hasSlashNToken(body) {
  const s = String(body || '');
  return /(^|\s)\/n(\s|$)/.test(s);
}

function containsLinkLike(text) {
  const s = String(text || '').trim();
  if (!s) return false;
  if (/https?:\/\//i.test(s)) return true;
  if (/www\./i.test(s)) return true;
  // very rough domain detection; intentionally strict to avoid accidental bans
  if (/\b[a-z0-9-]+\.(com|cn|net|org|io|me|co|app|dev)\b/i.test(s)) return true;
  return false;
}

function isImagePath(p) {
  const s = String(p || '').toLowerCase();
  return s.endsWith('.png') || s.endsWith('.jpg') || s.endsWith('.jpeg');
}

async function checkMediaDims(media) {
  const images = media.filter(isImagePath);
  const results = [];
  for (const p of images) {
    try {
      const { width, height, format } = await getImageSize(p);
      const ratio = width / height;
      results.push({ path: p, ok: true, width, height, ratio, format });
    } catch (e) {
      results.push({ path: p, ok: false, error: e?.message || String(e) });
    }
  }

  // Strict-ish: expect portrait 3:4 assets for XHS cards (prefer 1242x1660).
  const ratioTarget = 3 / 4;
  const ratioTol = 0.02;
  const bad = results.filter((r) => r.ok && Math.abs(r.ratio - ratioTarget) > ratioTol);
  const parseFailed = results.filter((r) => !r.ok);

  const hasAny = images.length > 0;
  const ok = !hasAny || (bad.length === 0 && parseFailed.length === 0);

  const perfect = results.filter((r) => r.ok && r.width === 1242 && r.height === 1660);
  return {
    ok,
    value: {
      checked_images: images.length,
      passed: results.filter((r) => r.ok).length,
      parse_failed: parseFailed.length,
      ratio_bad: bad.length,
      perfect_1242x1660: perfect.length,
      details: results.slice(0, 12), // keep output bounded
    },
  };
}

async function buildChecks(payload, mode) {
  const topic = str(payload?.topic);
  const sourceName = str(payload?.source?.name);
  const sourceUrl = str(payload?.source?.url);
  const sourceDate = str(payload?.source?.date);

  const title = str(payload?.post?.title);
  const body = str(payload?.post?.body);
  const tagsRaw = pickArray(payload?.post?.tags).map((x) => str(x)).filter(Boolean);
  const tags = tagsRaw.filter((x) => x.startsWith('#'));
  const media = pickArray(payload?.post?.media).map((x) => str(x)).filter(Boolean);

  const titleLen = [...title].length;
  const bodyLen = [...body].length;
  const screenshotOnly = media.length > 0 && media.every((x) => isScreenshotLike(x));
  const hotMode = mode === 'hot';
  const hasBackslashN = hasLiteralBackslashN(body);
  const hasSlashN = hasSlashNToken(body);
  const mediaDims = await checkMediaDims(media);
  const linkInTitle = containsLinkLike(title);
  const linkInBody = containsLinkLike(body);
  const linkInTags = tagsRaw.some((t) => containsLinkLike(t));
  const linkInMediaPath = media.some((p) => containsLinkLike(p) || String(p).includes('://'));

  const checks = {
    has_topic: {
      ok: topic.length >= 4,
      value: topic || null,
    },
    has_source: {
      ok: !!sourceName && isHttpUrl(sourceUrl) && isValidDateYYYYMMDD(sourceDate),
      value: { name: sourceName || null, url: sourceUrl || null, date: sourceDate || null },
    },
    title_ok: {
      ok: titleLen >= 8 && titleLen <= 20,
      value: { title: title || null, length: titleLen },
    },
    body_ok: {
      ok: bodyLen >= 80,
      value: { length: bodyLen },
    },
    body_newline_normalized: {
      // Allow literal "\\n" in payload (we can normalize before writing), but forbid "/n" token.
      ok: !hasSlashN,
      value: {
        has_literal_backslash_n: hasBackslashN,
        has_slash_n_token: hasSlashN,
      },
    },
    tags_ok: {
      ok: tags.length >= 3,
      value: { count: tags.length, tags },
    },
    no_links_in_content: {
      ok: !(linkInTitle || linkInBody || linkInTags),
      value: {
        title: linkInTitle,
        body: linkInBody,
        tags: linkInTags,
      },
    },
    no_links_in_media_path: {
      ok: !linkInMediaPath,
      value: linkInMediaPath ? media : null,
    },
    media_ok: {
      ok: media.length >= 1 && !screenshotOnly,
      value: { count: media.length, screenshot_only: screenshotOnly, media },
    },
    media_dim_ok: mediaDims,
    hot_source_is_today: {
      ok: !hotMode || sourceDate === todayISO(),
      value: { required_date: hotMode ? todayISO() : null, source_date: sourceDate || null },
    },
  };

  return checks;
}

async function main(argv) {
  const { values } = parseArgs({
    args: argv,
    options: {
      in: { type: 'string' },
      mode: { type: 'string', default: 'normal' },
      json: { type: 'boolean', default: true },
      help: { type: 'boolean', default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    console.log(usage());
    return;
  }

  if (!values.in) {
    throw new Error('Missing --in <payloadJsonPath>');
  }

  const raw = await readFile(values.in, 'utf8');
  const payload = JSON.parse(raw);
  const mode = str(values.mode || 'normal').toLowerCase();
  const checks = await buildChecks(payload, mode);

  const missing = Object.entries(checks)
    .filter(([, item]) => !item.ok)
    .map(([key]) => key);

  const result = {
    task: 'xhs_publish_payload_validate',
    ok: missing.length === 0,
    mode,
    checks,
    missing,
  };

  if (values.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`ok: ${result.ok}`);
    console.log(`missing: ${missing.join(', ') || '(none)'}`);
  }

  if (!result.ok) {
    process.exitCode = 2;
  }
}

main(process.argv.slice(2)).catch((e) => {
  console.error(e?.message || String(e));
  process.exitCode = 1;
});
