---
name: dropboxbusiness
description: |
  Dropbox Business API integration with managed OAuth. Manage team members, groups, team folders, devices, and audit logs for Dropbox Business teams.
  Use this skill when users want to administer Dropbox Business teams, manage members, create groups, handle team folders, or access audit logs.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai" 
    requires:
      env:
        - MATON_API_KEY
---

# Dropbox Business

Access the Dropbox Business API with managed OAuth authentication. Manage team administration including members, groups, team folders, devices, linked apps, and audit logs.

## Quick Start

```bash
# Get team info
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/dropbox-business/2/team/get_info', data=b'null', method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/dropbox-business/2/{endpoint-path}
```

Replace `{endpoint-path}` with the actual Dropbox Business API endpoint path. The gateway proxies requests to `api.dropboxapi.com` and automatically injects your OAuth token.

**IMPORTANT:** Dropbox Business API uses **POST** for almost all endpoints, including read operations. Request bodies should be JSON (use `null` for endpoints with no parameters).

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Dropbox Business OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=dropbox-business&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'dropbox-business'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection_id": "09062f57-98a9-49f2-9e63-b2a7e03a9d7a",
  "status": "PENDING",
  "url": "https://connect.maton.ai/?session_token=...",
  "app": "dropbox-business"
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
urllib.request.urlopen(req)
print("Deleted")
EOF
```

### Specifying Connection

If you have multiple Dropbox Business connections, specify which one to use with the `Maton-Connection` header:

```python
req.add_header('Maton-Connection', '{connection_id}')
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Team Information

#### Get Team Info

Retrieves information about the team including license usage and policies.

```bash
POST /dropbox-business/2/team/get_info
Content-Type: application/json

null
```

**Response:**
```json
{
  "name": "My Company",
  "team_id": "dbtid:AAC...",
  "num_licensed_users": 10,
  "num_provisioned_users": 5,
  "num_used_licenses": 5,
  "policies": {
    "sharing": {...},
    "emm_state": {".tag": "disabled"},
    "office_addin": {".tag": "enabled"}
  }
}
```

#### Get Team Features

```bash
POST /dropbox-business/2/team/features/get_values
Content-Type: application/json

{
  "features": [{".tag": "upload_api_rate_limit"}]
}
```

### Team Members

#### List Members

```bash
POST /dropbox-business/2/team/members/list
Content-Type: application/json

{
  "limit": 100
}
```

**Response:**
```json
{
  "members": [
    {
      "profile": {
        "team_member_id": "dbmid:AAA...",
        "account_id": "dbid:AAC...",
        "email": "user@company.com",
        "email_verified": true,
        "status": {".tag": "active"},
        "name": {
          "given_name": "John",
          "surname": "Doe",
          "display_name": "John Doe"
        },
        "membership_type": {".tag": "full"},
        "joined_on": "2026-01-15T10:00:00Z"
      },
      "role": {".tag": "team_admin"}
    }
  ],
  "cursor": "AAQ...",
  "has_more": false
}
```

#### Continue Listing Members

```bash
POST /dropbox-business/2/team/members/list/continue
Content-Type: application/json

{
  "cursor": "AAQ..."
}
```

#### Get Member Info

```bash
POST /dropbox-business/2/team/members/get_info
Content-Type: application/json

{
  "members": [{".tag": "email", "email": "user@company.com"}]
}
```

Alternative selectors:
- `{".tag": "team_member_id", "team_member_id": "dbmid:AAA..."}`
- `{".tag": "external_id", "external_id": "..."}`

#### Add Member

```bash
POST /dropbox-business/2/team/members/add
Content-Type: application/json

{
  "new_members": [
    {
      "member_email": "newuser@company.com",
      "member_given_name": "Jane",
      "member_surname": "Smith",
      "send_welcome_email": true,
      "role": {".tag": "member_only"}
    }
  ]
}
```

#### Suspend Member

```bash
POST /dropbox-business/2/team/members/suspend
Content-Type: application/json

{
  "user": {".tag": "email", "email": "user@company.com"},
  "wipe_data": false
}
```

#### Unsuspend Member

```bash
POST /dropbox-business/2/team/members/unsuspend
Content-Type: application/json

{
  "user": {".tag": "email", "email": "user@company.com"}
}
```

#### Remove Member

```bash
POST /dropbox-business/2/team/members/remove
Content-Type: application/json

{
  "user": {".tag": "email", "email": "user@company.com"},
  "wipe_data": true,
  "transfer_dest_id": {".tag": "email", "email": "admin@company.com"},
  "keep_account": false
}
```

### Groups

#### List Groups

```bash
POST /dropbox-business/2/team/groups/list
Content-Type: application/json

{
  "limit": 100
}
```

**Response:**
```json
{
  "groups": [
    {
      "group_name": "Engineering",
      "group_id": "g:1d31f47b...",
      "member_count": 5,
      "group_management_type": {".tag": "company_managed"}
    }
  ],
  "cursor": "AAZ...",
  "has_more": false
}
```

#### Get Group Info

```bash
POST /dropbox-business/2/team/groups/get_info
Content-Type: application/json

{
  ".tag": "group_ids",
  "group_ids": ["g:1d31f47b..."]
}
```

#### Create Group

```bash
POST /dropbox-business/2/team/groups/create
Content-Type: application/json

{
  "group_name": "Marketing Team",
  "group_management_type": {".tag": "company_managed"}
}
```

#### Add Members to Group

```bash
POST /dropbox-business/2/team/groups/members/add
Content-Type: application/json

{
  "group": {".tag": "group_id", "group_id": "g:1d31f47b..."},
  "members": [
    {
      "user": {".tag": "email", "email": "user@company.com"},
      "access_type": {".tag": "member"}
    }
  ],
  "return_members": true
}
```

#### Remove Members from Group

```bash
POST /dropbox-business/2/team/groups/members/remove
Content-Type: application/json

{
  "group": {".tag": "group_id", "group_id": "g:1d31f47b..."},
  "users": [{".tag": "email", "email": "user@company.com"}],
  "return_members": true
}
```

#### Delete Group

```bash
POST /dropbox-business/2/team/groups/delete
Content-Type: application/json

{
  ".tag": "group_id",
  "group_id": "g:1d31f47b..."
}
```

### Team Folders

#### List Team Folders

```bash
POST /dropbox-business/2/team/team_folder/list
Content-Type: application/json

{
  "limit": 100
}
```

**Response:**
```json
{
  "team_folders": [
    {
      "team_folder_id": "13646676387",
      "name": "Company Documents",
      "status": {".tag": "active"},
      "is_team_shared_dropbox": false,
      "sync_setting": {".tag": "default"}
    }
  ],
  "cursor": "AAb...",
  "has_more": false
}
```

#### Get Team Folder Info

```bash
POST /dropbox-business/2/team/team_folder/get_info
Content-Type: application/json

{
  "team_folder_ids": ["13646676387"]
}
```

#### Create Team Folder

```bash
POST /dropbox-business/2/team/team_folder/create
Content-Type: application/json

{
  "name": "New Team Folder",
  "sync_setting": {".tag": "default"}
}
```

#### Rename Team Folder

```bash
POST /dropbox-business/2/team/team_folder/rename
Content-Type: application/json

{
  "team_folder_id": "13646676387",
  "name": "Renamed Folder"
}
```

#### Archive Team Folder

```bash
POST /dropbox-business/2/team/team_folder/archive
Content-Type: application/json

{
  "team_folder_id": "13646676387",
  "force_async_off": false
}
```

#### Permanently Delete Team Folder

```bash
POST /dropbox-business/2/team/team_folder/permanently_delete
Content-Type: application/json

{
  "team_folder_id": "13646676387"
}
```

### Namespaces

#### List Namespaces

```bash
POST /dropbox-business/2/team/namespaces/list
Content-Type: application/json

{
  "limit": 100
}
```

**Response:**
```json
{
  "namespaces": [
    {
      "name": "Team Folder",
      "namespace_id": "13646676387",
      "namespace_type": {".tag": "team_folder"}
    },
    {
      "name": "Root",
      "namespace_id": "13646219987",
      "namespace_type": {".tag": "team_member_folder"},
      "team_member_id": "dbmid:AAA..."
    }
  ],
  "cursor": "AAY...",
  "has_more": false
}
```

### Devices

#### List All Members' Devices

```bash
POST /dropbox-business/2/team/devices/list_members_devices
Content-Type: application/json

{}
```

**Response:**
```json
{
  "devices": [
    {
      "team_member_id": "dbmid:AAA...",
      "web_sessions": [
        {
          "session_id": "dbwsid:...",
          "ip_address": "192.168.1.1",
          "country": "United States",
          "created": "2026-02-15T08:26:33Z",
          "user_agent": "Mozilla/5.0...",
          "os": "Mac OS X",
          "browser": "Chrome"
        }
      ],
      "desktop_clients": [],
      "mobile_clients": []
    }
  ],
  "has_more": false
}
```

#### List Member Devices

```bash
POST /dropbox-business/2/team/devices/list_member_devices
Content-Type: application/json

{
  "team_member_id": "dbmid:AAA..."
}
```

#### Revoke Device Session

```bash
POST /dropbox-business/2/team/devices/revoke_device_session
Content-Type: application/json

{
  ".tag": "web_session",
  "session_id": "dbwsid:...",
  "team_member_id": "dbmid:AAA..."
}
```

### Linked Apps

#### List Members' Linked Apps

```bash
POST /dropbox-business/2/team/linked_apps/list_members_linked_apps
Content-Type: application/json

{}
```

**Response:**
```json
{
  "apps": [
    {
      "team_member_id": "dbmid:AAA...",
      "linked_api_apps": [
        {
          "app_id": "...",
          "app_name": "Third Party App",
          "linked": "2026-01-15T10:00:00Z"
        }
      ]
    }
  ],
  "has_more": false
}
```

#### Revoke Linked App

```bash
POST /dropbox-business/2/team/linked_apps/revoke_linked_app
Content-Type: application/json

{
  "app_id": "...",
  "team_member_id": "dbmid:AAA..."
}
```

### Audit Log (Team Log)

#### Get Events

```bash
POST /dropbox-business/2/team_log/get_events
Content-Type: application/json

{
  "limit": 100,
  "category": {".tag": "members"}
}
```

**Response:**
```json
{
  "events": [
    {
      "timestamp": "2026-02-15T08:27:36Z",
      "event_category": {".tag": "members"},
      "actor": {
        ".tag": "admin",
        "admin": {
          "account_id": "dbid:AAC...",
          "display_name": "Admin User",
          "email": "admin@company.com"
        }
      },
      "event_type": {
        ".tag": "member_add_name",
        "description": "Added team member name"
      },
      "details": {...}
    }
  ],
  "cursor": "...",
  "has_more": false
}
```

**Event Categories:**
- `apps` - Third-party app events
- `comments` - Comment events
- `devices` - Device events
- `domains` - Domain events
- `file_operations` - File and folder events
- `file_requests` - File request events
- `groups` - Group events
- `logins` - Login events
- `members` - Member events
- `paper` - Paper events
- `passwords` - Password events
- `reports` - Report events
- `sharing` - Sharing events
- `showcase` - Showcase events
- `sso` - SSO events
- `team_folders` - Team folder events
- `team_policies` - Policy events
- `team_profile` - Team profile events
- `tfa` - Two-factor auth events

#### Continue Getting Events

```bash
POST /dropbox-business/2/team_log/get_events/continue
Content-Type: application/json

{
  "cursor": "..."
}
```

## Pagination

Dropbox Business uses cursor-based pagination. List endpoints return a `cursor` and `has_more` field.

**Initial Request:**
```bash
POST /dropbox-business/2/team/members/list
Content-Type: application/json

{
  "limit": 100
}
```

**Response:**
```json
{
  "members": [...],
  "cursor": "AAQ...",
  "has_more": true
}
```

**Continue with cursor:**
```bash
POST /dropbox-business/2/team/members/list/continue
Content-Type: application/json

{
  "cursor": "AAQ..."
}
```

## Code Examples

### JavaScript

```javascript
async function listTeamMembers() {
  const response = await fetch(
    'https://gateway.maton.ai/dropbox-business/2/team/members/list',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ limit: 100 })
    }
  );
  return await response.json();
}
```

### Python

```python
import os
import json
import urllib.request

def list_team_members():
    url = 'https://gateway.maton.ai/dropbox-business/2/team/members/list'
    data = json.dumps({'limit': 100}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    req.add_header('Content-Type', 'application/json')
    return json.load(urllib.request.urlopen(req))

def get_team_info():
    url = 'https://gateway.maton.ai/dropbox-business/2/team/get_info'
    req = urllib.request.Request(url, data=b'null', method='POST')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    req.add_header('Content-Type', 'application/json')
    return json.load(urllib.request.urlopen(req))
```

## Notes

- **POST for Everything**: Dropbox Business API uses POST for almost all endpoints, including read operations
- **JSON Body Required**: Even for endpoints with no parameters, send `null` as the request body
- **Tag Format**: Many fields use `.tag` to indicate the type (e.g., `{".tag": "email", "email": "..."}`)
- **Member Selectors**: Use `.tag` with `email`, `team_member_id`, or `external_id` to identify members
- **Async Operations**: Some operations (like group member changes) may be async; check `team/groups/job_status/get`
- **IMPORTANT**: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or invalid parameters |
| 401 | Invalid API key or expired token |
| 403 | Permission denied (requires team admin) |
| 404 | Resource not found |
| 409 | Conflict (e.g., member already exists) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Dropbox API |

### Response Error Format

```json
{
  "error_summary": "member_not_found/...",
  "error": {
    ".tag": "member_not_found"
  }
}
```

## Resources

- [Dropbox Business API Documentation](https://www.dropbox.com/developers/documentation/http/teams)
- [Team Administration Guide](https://developers.dropbox.com/dbx-team-administration-guide)
- [Team Files Guide](https://developers.dropbox.com/dbx-team-files-guide)
- [Authentication Types](https://www.dropbox.com/developers/reference/auth-types)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
