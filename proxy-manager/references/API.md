# Webshare API — Core Endpoints

Base URL: `https://proxy.webshare.io/api/v2/`
Auth header: `Authorization: Token <TOKEN>`
Source header (required on every call): `X-Webshare-Source: WebshareSkill/<skill version> (LLM; <your model>)` — e.g. `WebshareSkill/1.0 (LLM; Claude/Opus-4.7)`. Skill version is in the frontmatter of `SKILL.md`.
Token page: https://dashboard.webshare.io/userapi/keys
Full docs: https://apidocs.webshare.io/

## Rate limits

| Scope | Limit |
|---|---|
| General | 240 req/min |
| Proxy list | 60 req/min |
| Proxy-list downloads | 30 req/min |
| Pricing | 60 req/min |

On 429, wait 60s before retrying.

## Multi-plan accounts

An account can own **more than one plan** (e.g. a datacenter plan and a
rotating-residential plan running side by side). Almost every endpoint that
operates on proxies or config is scoped to a plan and accepts a
`plan_id` query parameter. Omit it to hit the user's *default* plan.

Start any session by listing plans (#1) so you know which IDs exist, then pass
`?plan_id=<id>` on every subsequent call unless the user explicitly wants the
default plan.

## Endpoints

### 1. List plans — `GET /subscription/plan/`

Paginated list of every plan on the account. Use this first to learn plan IDs,
see which plan is the default, and check current capacity.

Response (`results[]` item, key fields):
```json
{
  "id": 1234,
  "proxy_type": "dedicated",
  "proxy_subtype": "premium",
  "proxy_count": 75,
  "bandwidth_limit": 5000,
  "is_default": true,
  "is_yearly": false,
  "status": "active",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-02-01T00:00:00Z",
  "next_billing_date": "2024-02-01T00:00:00Z"
}
```

`GET /subscription/plan/<id>/` returns full detail for one plan.

```bash
curl 'https://proxy.webshare.io/api/v2/subscription/plan/' \
  -H "Authorization: Token $WEBSHARE_API_TOKEN" \
  -H "X-Webshare-Source: WebshareSkill/1.0 (LLM; Claude/Opus-4.7)"
```

### 2. List proxies — `GET /proxy/list/`

Paginated proxies on a plan.

Query params:
- `plan_id` — *target plan; omit for default*
- `mode` *(required)* — `direct` (unique IP per proxy) or `backbone` (single gateway, rotating IP)
- `country_code__in` — comma-separated ISO 3166-1 alpha-2 codes
- `valid` — `true`/`false`
- `search`, `ordering`, `page`, `page_size`
- `proxy_address`, `proxy_address__in`, `asn_number`, `asn_name`, `created_at`

Response (`results[]` item):
```json
{
  "id": "d-10513",
  "username": "user-1",
  "password": "pw",
  "proxy_address": "1.2.3.4",
  "port": 8168,
  "valid": true,
  "last_verification": "2024-01-01T00:00:00Z",
  "country_code": "US",
  "city_name": "Ashburn",
  "created_at": "2024-01-01T00:00:00Z"
}
```

```bash
curl 'https://proxy.webshare.io/api/v2/proxy/list/?plan_id=1234&mode=direct&page_size=100' \
  -H "Authorization: Token $WEBSHARE_API_TOKEN" \
  -H "X-Webshare-Source: WebshareSkill/1.0 (LLM; Claude/Opus-4.7)"
```

### 3. Download proxy list — `GET /proxy/list/download/<token>/-/<mode>/<filename>/<layout>/`

Plain-text dump of `ip:port:user:pass` (or similar layouts), suitable for piping
into apps that read a flat proxy list. Accepts `?plan_id=<id>`.

Get the download token from `/proxy/config/` (`proxy_list_download_token`), then
embed it in the path.

### 4. Replace proxies — `POST /proxy/replacement/`

Request replacement of specific dead or misbehaving proxies. Body: list of proxy
IDs to replace. Pass `?plan_id=<id>` to replace on a specific plan.

- `GET /proxy/replacement/` — list replacement requests (accepts `plan_id`)
- `GET /proxy/replaced/` — proxies that have been replaced historically

### 5. Proxy config — `GET /proxy/config/` · `PUT /proxy/config/`

Per-plan proxy config. Notable fields:
- `username`, `password` — default credentials
- `proxy_list_download_token` — token for the download URL
- `authorization_method` — `password` or `ip`
- `backbone_mode` — whether the backbone (rotating gateway) is enabled

Pass `?plan_id=<id>` on both GET and PUT. `PUT` with the same body shape to
update. `POST /proxy/config/allocate/?plan_id=<id>` allocates unallocated
country-specific proxies onto a plan.

### 6. IP allowlist — `/ipauth/`

When `authorization_method=ip`, only requests from allowlisted IPs are accepted.
All `/ipauth/` endpoints accept `?plan_id=<id>`.

- `GET /ipauth/` — list authorized IPs
- `POST /ipauth/` — add one. Body: `{"ip_address": "1.2.3.4"}`
- `DELETE /ipauth/<id>/` — remove one
- `GET /ipauth/whatsmyip/` — echo the caller's public IP (not plan-scoped)

### 7. Proxy stats — `GET /proxy/stats/`

Per-proxy performance stats (requests, bandwidth, last check). Accepts `plan_id`.

- `GET /stats/aggregate/` — account-wide aggregated usage (accepts `plan_id`)
- `GET /activity/` — recent request activity, paginated (accepts `plan_id`)

### 8. API keys — `GET/POST/PUT/DELETE /apikeys/`

Manage API keys programmatically. Not plan-scoped. Usually unnecessary — users
create keys via the dashboard at https://dashboard.webshare.io/userapi/keys.

## Common gotchas

- **Always scope to a plan** unless the user has exactly one plan. Running
  `/proxy/list/` without `plan_id` silently returns proxies from the default
  plan only, which is easy to misread as "all proxies".
- `mode=direct` gives N unique IPs. `mode=backbone` gives one gateway that
  rotates IPs server-side. Pick one.
- The proxy `id` field is a string, not an integer. The plan `id` is an integer.
- `authorization_method=ip` means `username`/`password` still exist but are
  ignored — only the source IP matters.
