import { AccessMode } from './types.js';
/**
 * Manages WAC (Web Access Control) ACLs on Solid resources.
 * Uses direct HTTP to manipulate .acl resources.
 */
export declare function grantAccess(resourceUrl: string, agentWebId: string, modes: AccessMode[], authFetch: typeof fetch, ownerWebId?: string): Promise<void>;
export declare function revokeAccess(resourceUrl: string, agentWebId: string, authFetch: typeof fetch): Promise<void>;
