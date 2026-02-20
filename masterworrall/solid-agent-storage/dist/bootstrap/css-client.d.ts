import { CssAccount } from './types.js';
/**
 * Low-level HTTP client for the CSS v7 Account API.
 *
 * CSS v7 flow:
 * 1. POST /.account/account/ → creates account, returns cookie + controls
 * 2. POST controls.password.create → adds email/password login
 * 3. POST controls.account.pod → creates pod, returns pod URL + WebID
 * 4. POST controls.account.clientCredentials → creates client credentials
 */
export declare function createAccount(serverUrl: string): Promise<CssAccount>;
export declare function addPasswordLogin(serverUrl: string, cookie: string, email: string, password: string): Promise<void>;
export declare function createPod(serverUrl: string, cookie: string, name: string): Promise<{
    pod: string;
    webId: string;
}>;
export declare function createClientCredentials(serverUrl: string, cookie: string, name: string, webId: string): Promise<{
    id: string;
    secret: string;
}>;
