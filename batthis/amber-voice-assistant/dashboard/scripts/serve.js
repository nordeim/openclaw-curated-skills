#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

function parseArgs(argv) {
  const args = { port: 8787, host: '127.0.0.1' };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--port' && argv[i + 1]) args.port = Number(argv[++i]);
    else if (a === '--host' && argv[i + 1]) args.host = argv[++i];
    else if (a === '-h' || a === '--help') args.help = true;
  }
  return args;
}

function contentType(p) {
  if (p.endsWith('.html')) return 'text/html; charset=utf-8';
  if (p.endsWith('.css')) return 'text/css; charset=utf-8';
  if (p.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (p.endsWith('.json')) return 'application/json; charset=utf-8';
  if (p.endsWith('.svg')) return 'image/svg+xml';
  if (p.endsWith('.png')) return 'image/png';
  if (p.endsWith('.jpg') || p.endsWith('.jpeg')) return 'image/jpeg';
  return 'application/octet-stream';
}

const args = parseArgs(process.argv);
if (args.help) {
  console.log('Usage: node scripts/serve.js [--host 127.0.0.1] [--port 8787]');
  process.exit(0);
}

const root = path.resolve(__dirname, '..');

const server = http.createServer((req, res) => {
  const u = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  let pathname = decodeURIComponent(u.pathname);
  if (pathname === '/') pathname = '/index.html';

  const fsPath = path.resolve(root, '.' + pathname);
  if (!fsPath.startsWith(root + path.sep) && fsPath !== root) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Forbidden');
    return;
  }

  fs.readFile(fsPath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end('Not found');
      return;
    }
    res.writeHead(200, {
      'Content-Type': contentType(fsPath),
      'Cache-Control': 'no-store'
    });
    res.end(data);
  });
});

// Warn if binding to a non-loopback address (exposes call logs to the network)
const LOOPBACK_ADDRESSES = new Set(['127.0.0.1', '::1', 'localhost']);
if (!LOOPBACK_ADDRESSES.has(args.host)) {
  console.warn('');
  console.warn('⚠️  WARNING: Dashboard is binding to a non-loopback address (' + args.host + ').');
  console.warn('   This exposes call logs and transcripts to the network.');
  console.warn('   Use --host 127.0.0.1 (default) unless you explicitly need remote access.');
  console.warn('');
}

server.listen(args.port, args.host, () => {
  console.log(`Serving ${root}`);
  console.log(`Open: http://${args.host}:${args.port}/`);
});
