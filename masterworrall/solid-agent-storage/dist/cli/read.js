import { getAuthenticatedFetch } from '../auth/client-credentials.js';
import { initStore, loadCredentials } from './credentials-store.js';
import { requireArg, getServerUrl, getPassphrase } from './args.js';
const agent = requireArg('agent', 'Usage: read --agent <name> --url <resource-url>');
const url = requireArg('url', 'Usage: read --agent <name> --url <resource-url>');
const serverUrl = getServerUrl();
initStore(getPassphrase());
(async () => {
    const creds = loadCredentials(agent);
    const authFetch = await getAuthenticatedFetch(serverUrl, creds.id, creds.secret);
    const res = await authFetch(url);
    if (!res.ok) {
        console.error(JSON.stringify({ error: `HTTP ${res.status}`, body: await res.text() }));
        process.exit(1);
    }
    const contentType = res.headers.get('content-type') ?? 'application/octet-stream';
    const body = await res.text();
    console.log(JSON.stringify({
        status: 'ok',
        url,
        contentType,
        body,
    }));
})().catch((err) => {
    console.error(JSON.stringify({ error: String(err.message ?? err) }));
    process.exit(1);
});
//# sourceMappingURL=read.js.map