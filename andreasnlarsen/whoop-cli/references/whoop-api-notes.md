# WHOOP API notes

## OAuth

- Auth URL: `https://api.prod.whoop.com/oauth/oauth2/auth`
- Token URL: `https://api.prod.whoop.com/oauth/oauth2/token`
- Refresh uses token endpoint (`grant_type=refresh_token`)

Common scopes:
- `read:recovery`
- `read:cycles`
- `read:workout`
- `read:sleep`
- `read:profile`
- `read:body_measurement`
- `offline` (for refresh token)

## API behavior

- Pagination commonly uses `next_token`.
- Collection endpoints accept `limit`, `start`, `end`, and `nextToken`.
- Use Bearer auth header with access token.

## Webhooks

- v2 webhooks use UUID IDs.
- Validate signature with HMAC-SHA256 over: `timestamp + raw_body`
- Headers:
  - `X-WHOOP-Signature`
  - `X-WHOOP-Signature-Timestamp`

## Canonical docs

- https://developer.whoop.com/api/
- https://developer.whoop.com/docs/developing/oauth/
- https://developer.whoop.com/docs/developing/webhooks/
- https://developer.whoop.com/docs/developing/getting-started/
