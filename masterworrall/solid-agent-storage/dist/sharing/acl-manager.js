/**
 * Manages WAC (Web Access Control) ACLs on Solid resources.
 * Uses direct HTTP to manipulate .acl resources.
 */
export async function grantAccess(resourceUrl, agentWebId, modes, authFetch, ownerWebId) {
    const aclUrl = await getAclUrl(resourceUrl, authFetch);
    const existingAcl = await fetchAclContent(aclUrl, authFetch);
    // Build a new ACL rule for the agent
    const ruleName = `agent-${agentWebId.replace(/[^a-zA-Z0-9]/g, '_')}`;
    const modeUris = modes.map((m) => `acl:${m}`).join(', ');
    const newRule = `
<#${ruleName}>
    a acl:Authorization;
    acl:agent <${agentWebId}>;
    acl:accessTo <${resourceUrl}>;
    acl:mode ${modeUris}.
`;
    // Append the new rule to existing ACL (or create new with owner rule if empty)
    const aclContent = existingAcl
        ? `${existingAcl}\n${newRule}`
        : buildBaseAcl(resourceUrl, ownerWebId) + newRule;
    const res = await authFetch(aclUrl, {
        method: 'PUT',
        headers: { 'content-type': 'text/turtle' },
        body: aclContent,
    });
    if (!res.ok) {
        throw new Error(`Failed to grant access: ${res.status} ${await res.text()}`);
    }
}
export async function revokeAccess(resourceUrl, agentWebId, authFetch) {
    const aclUrl = await getAclUrl(resourceUrl, authFetch);
    const existingAcl = await fetchAclContent(aclUrl, authFetch);
    if (!existingAcl)
        return; // No ACL means no access to revoke
    // Remove rules that reference this agent
    // Simple approach: rebuild without lines referencing the agent
    const lines = existingAcl.split('\n');
    const filtered = [];
    let skipBlock = false;
    for (const line of lines) {
        if (line.trim().startsWith('<#agent-') && line.includes(agentWebId.replace(/[^a-zA-Z0-9]/g, '_'))) {
            skipBlock = true;
            continue;
        }
        if (skipBlock && line.trim() === '') {
            skipBlock = false;
            continue;
        }
        if (skipBlock && !line.trim().startsWith('<#')) {
            continue;
        }
        if (skipBlock) {
            skipBlock = false; // New block started
        }
        filtered.push(line);
    }
    const newAcl = filtered.join('\n');
    const res = await authFetch(aclUrl, {
        method: 'PUT',
        headers: { 'content-type': 'text/turtle' },
        body: newAcl,
    });
    if (!res.ok) {
        throw new Error(`Failed to revoke access: ${res.status} ${await res.text()}`);
    }
}
async function getAclUrl(resourceUrl, authFetch) {
    const res = await authFetch(resourceUrl, { method: 'HEAD' });
    const linkHeader = res.headers.get('link');
    if (linkHeader) {
        const aclMatch = linkHeader.match(/<([^>]+)>;\s*rel="acl"/);
        if (aclMatch) {
            return new URL(aclMatch[1], resourceUrl).href;
        }
    }
    // Default convention: append .acl
    return `${resourceUrl}.acl`;
}
async function fetchAclContent(aclUrl, authFetch) {
    const res = await authFetch(aclUrl);
    if (res.ok)
        return res.text();
    if (res.status === 404)
        return null;
    throw new Error(`Failed to fetch ACL: ${res.status}`);
}
function buildBaseAcl(resourceUrl, ownerWebId) {
    let base = `@prefix acl: <http://www.w3.org/ns/auth/acl#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.

`;
    // Always include an owner rule so the Pod owner retains full access
    if (ownerWebId) {
        base += `<#owner>
    a acl:Authorization;
    acl:agent <${ownerWebId}>;
    acl:accessTo <${resourceUrl}>;
    acl:mode acl:Read, acl:Write, acl:Control.

`;
    }
    return base;
}
//# sourceMappingURL=acl-manager.js.map