# Troubleshooting

## Common Errors

### "No passphrase provided"

**Cause:** The `INTERITION_PASSPHRASE` environment variable is not set.

**Fix:**
```bash
export INTERITION_PASSPHRASE="your-passphrase-here"
```

### "No credentials found for agent X"

**Cause:** The agent hasn't been provisioned yet, or credentials are stored under a different name.

**Fix:**
1. Check existing agents: `scripts/status.sh`
2. Provision the agent: `scripts/provision.sh --name <agent-name>`

### "Invalid passphrase — cannot decrypt credentials"

**Cause:** The `INTERITION_PASSPHRASE` value doesn't match the one used when the agent was provisioned.

**Fix:** Use the same passphrase that was set when `provision.sh` was first run. If you've lost the passphrase, you'll need to re-provision the agent (which creates a new WebID and Pod).

### "HTTP 401 Unauthorized"

**Cause:** The agent's access token has expired or the client credentials are invalid.

**Fix:** Client credentials don't expire, but the access token is refreshed automatically. If this persists, re-provision the agent.

### "HTTP 404 Not Found"

**Cause:** The resource doesn't exist at that URL.

**Fix:**
- Check the URL is correct (including trailing slashes for containers)
- Write data to the URL first before reading it
- Container URLs must end with `/`

### "HTTP 409 Conflict"

**Cause:** Trying to create a resource that already exists, or a naming conflict.

**Fix:** Use PUT (write command) to overwrite, or choose a different URL.

### "ECONNREFUSED"

**Cause:** The Solid server is not running.

**Fix:**
1. Start the server: `docker-compose up -d`
2. Verify it's running: `curl http://localhost:3000/`
3. Check `SOLID_SERVER_URL` matches the server address

## Data Format Issues

### Turtle syntax errors

If writing Turtle data and getting 400 errors, check:
- Prefixes are declared with `@prefix`
- Statements end with `.`
- URIs are wrapped in `<angle-brackets>`
- Strings are wrapped in `"double-quotes"`

### Content type mismatch

When writing data, ensure `--content-type` matches the actual data format:
- Turtle: `text/turtle`
- Plain text: `text/plain`
- JSON: `application/json`
- JSON-LD: `application/ld+json`
