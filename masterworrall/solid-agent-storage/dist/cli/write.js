import { getAuthenticatedFetch } from '../auth/client-credentials.js';
import { initStore, loadCredentials } from './credentials-store.js';
import { requireArg, getArg, getServerUrl, getPassphrase } from './args.js';
const agent = requireArg('agent', 'Usage: write --agent <name> --url <resource-url> --content <data> [--content-type <type>]');
const url = requireArg('url', 'Usage: write --agent <name> --url <resource-url> --content <data> [--content-type <type>]');
const content = requireArg('content', 'Usage: write --agent <name> --url <resource-url> --content <data> [--content-type <type>]');
const contentType = getArg('content-type') ?? 'text/turtle';
const serverUrl = getServerUrl();
initStore(getPassphrase());
(async () => {
    const creds = loadCredentials(agent);
    const authFetch = await getAuthenticatedFetch(serverUrl, creds.id, creds.secret);
    const res = await authFetch(url, {
        method: 'PUT',
        headers: { 'content-type': contentType },
        body: content,
    });
    if (!res.ok) {
        console.error(JSON.stringify({ error: `HTTP ${res.status}`, body: await res.text() }));
        process.exit(1);
    }
    console.log(JSON.stringify({
        status: 'ok',
        url,
        contentType,
        httpStatus: res.status,
    }));
})().catch((err) => {
    console.error(JSON.stringify({ error: String(err.message ?? err) }));
    process.exit(1);
});
//# sourceMappingURL=write.js.map