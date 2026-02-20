/**
 * Low-level HTTP client for the CSS v7 Account API.
 *
 * CSS v7 flow:
 * 1. POST /.account/account/ → creates account, returns cookie + controls
 * 2. POST controls.password.create → adds email/password login
 * 3. POST controls.account.pod → creates pod, returns pod URL + WebID
 * 4. POST controls.account.clientCredentials → creates client credentials
 */
export async function createAccount(serverUrl) {
    const res = await fetch(`${serverUrl}/.account/account/`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: '{}',
    });
    if (!res.ok) {
        throw new Error(`Failed to create account: ${res.status} ${await res.text()}`);
    }
    const cookie = res.headers.get('set-cookie');
    if (!cookie) {
        throw new Error('No cookie returned from account creation');
    }
    const json = await res.json();
    return { cookie, accountUrl: `${serverUrl}/.account/` };
}
export async function addPasswordLogin(serverUrl, cookie, email, password) {
    const controls = await getControls(serverUrl, cookie);
    const passwordUrl = controls.password?.create;
    if (!passwordUrl) {
        throw new Error('Password creation endpoint not found in controls');
    }
    const res = await fetch(passwordUrl, {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            cookie,
        },
        body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
        throw new Error(`Failed to add password login: ${res.status} ${await res.text()}`);
    }
}
export async function createPod(serverUrl, cookie, name) {
    const controls = await getControls(serverUrl, cookie);
    const podUrl = controls.account?.pod;
    if (!podUrl) {
        throw new Error('Pod creation endpoint not found in controls');
    }
    const res = await fetch(podUrl, {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            cookie,
        },
        body: JSON.stringify({ name }),
    });
    if (!res.ok) {
        throw new Error(`Failed to create pod: ${res.status} ${await res.text()}`);
    }
    const json = await res.json();
    return { pod: json.pod, webId: json.webId };
}
export async function createClientCredentials(serverUrl, cookie, name, webId) {
    const controls = await getControls(serverUrl, cookie);
    const credUrl = controls.account?.clientCredentials;
    if (!credUrl) {
        throw new Error('Client credentials endpoint not found in controls');
    }
    const res = await fetch(credUrl, {
        method: 'POST',
        headers: {
            'content-type': 'application/json',
            cookie,
        },
        body: JSON.stringify({ name, webId }),
    });
    if (!res.ok) {
        throw new Error(`Failed to create client credentials: ${res.status} ${await res.text()}`);
    }
    const json = await res.json();
    return { id: json.id, secret: json.secret };
}
async function getControls(serverUrl, cookie) {
    const res = await fetch(`${serverUrl}/.account/`, {
        headers: { cookie },
    });
    if (!res.ok) {
        throw new Error(`Failed to get account controls: ${res.status}`);
    }
    const json = await res.json();
    return json.controls ?? json;
}
//# sourceMappingURL=css-client.js.map