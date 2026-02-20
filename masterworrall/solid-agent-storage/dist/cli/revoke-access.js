import { getAuthenticatedFetch } from '../auth/client-credentials.js';
import { revokeAccess } from '../sharing/acl-manager.js';
import { initStore, loadCredentials } from './credentials-store.js';
import { requireArg, getServerUrl, getPassphrase } from './args.js';
const agent = requireArg('agent', 'Usage: revoke-access --agent <name> --resource <url> --grantee <webId>');
const resource = requireArg('resource', 'Usage: revoke-access --agent <name> --resource <url> --grantee <webId>');
const grantee = requireArg('grantee', 'Usage: revoke-access --agent <name> --resource <url> --grantee <webId>');
const serverUrl = getServerUrl();
initStore(getPassphrase());
(async () => {
    const creds = loadCredentials(agent);
    const authFetch = await getAuthenticatedFetch(serverUrl, creds.id, creds.secret);
    await revokeAccess(resource, grantee, authFetch);
    console.log(JSON.stringify({
        status: 'ok',
        resource,
        grantee,
    }));
})().catch((err) => {
    console.error(JSON.stringify({ error: String(err.message ?? err) }));
    process.exit(1);
});
//# sourceMappingURL=revoke-access.js.map