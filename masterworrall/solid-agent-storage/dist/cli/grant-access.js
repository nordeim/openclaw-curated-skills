import { getAuthenticatedFetch } from '../auth/client-credentials.js';
import { grantAccess } from '../sharing/acl-manager.js';
import { initStore, loadCredentials } from './credentials-store.js';
import { requireArg, getServerUrl, getPassphrase } from './args.js';
const agent = requireArg('agent', 'Usage: grant-access --agent <name> --resource <url> --grantee <webId> --modes <Read,Write,...>');
const resource = requireArg('resource', 'Usage: grant-access --agent <name> --resource <url> --grantee <webId> --modes <Read,Write,...>');
const grantee = requireArg('grantee', 'Usage: grant-access --agent <name> --resource <url> --grantee <webId> --modes <Read,Write,...>');
const modesStr = requireArg('modes', 'Usage: grant-access --agent <name> --resource <url> --grantee <webId> --modes <Read,Write,...>');
const serverUrl = getServerUrl();
const validModes = ['Read', 'Write', 'Append', 'Control'];
const modes = modesStr.split(',').map((m) => m.trim());
for (const mode of modes) {
    if (!validModes.includes(mode)) {
        console.error(JSON.stringify({ error: `Invalid mode "${mode}". Valid modes: ${validModes.join(', ')}` }));
        process.exit(1);
    }
}
initStore(getPassphrase());
(async () => {
    const creds = loadCredentials(agent);
    const authFetch = await getAuthenticatedFetch(serverUrl, creds.id, creds.secret);
    await grantAccess(resource, grantee, modes, authFetch, creds.webId);
    console.log(JSON.stringify({
        status: 'ok',
        resource,
        grantee,
        modes,
    }));
})().catch((err) => {
    console.error(JSON.stringify({ error: String(err.message ?? err) }));
    process.exit(1);
});
//# sourceMappingURL=grant-access.js.map