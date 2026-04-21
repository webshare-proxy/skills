# Webshare API — Core Endpoints

Base URL: `https://proxy.webshare.io/api/v2/`
Auth header: `Authorization: Token <TOKEN>`
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

## Endpoints

### 1. List proxies — `GET /proxy/list/`

Paginated proxies on the current plan.

Query params:
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
curl 'https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page_size=100' \
  -H "Authorization: Token $WEBSHARE_API_TOKEN"
```

### 2. Download proxy list — `GET /proxy/list/download/<token>/-/<mode>/<filename>/<layout>/`

Plain-text file of `ip:port:user:pass` (or similar layouts). Get the download
token from `/proxy/config/` (`proxy_list_download_token` field), then use it in
the path. Useful for piping into apps that read a flat list.

### 3. On-demand refresh — `POST /proxy/list/ondemand_refresh/`

Trigger a refresh of the rotating proxy pool outside the automatic schedule.
Consumes an on-demand refresh credit from the plan. Empty body.

### 4. Replace proxies — `POST /proxy/replacement/`

Request replacement of specific bad proxies. Body: list of proxy IDs. Also:
- `GET /proxy/replacement/` — list replacement requests
- `GET /proxy/replaced/` — proxies that have been replaced historically

### 5. Proxy config — `GET /proxy/config/` · `PUT /proxy/config/`

Current account-wide proxy config. Notable fields:
- `username`, `password` — default credentials
- `proxy_list_download_token` — token for the download URL
- `authorization_method` — `password` or `ip`
- `backbone_mode` — whether backbone (rotating gateway) is enabled

`PUT` with the same body to update. `POST /proxy/config/allocate/` allocates
unallocated country-specific proxies onto the plan.

### 6. IP allowlist — `/ipauth/`

When `authorization_method` is `ip`, requests are accepted only from allowlisted IPs.

- `GET /ipauth/` — list authorized IPs
- `POST /ipauth/` — add one. Body: `{"ip_address": "1.2.3.4"}`
- `DELETE /ipauth/<id>/` — remove one
- `GET /ipauth/whatsmyip/` — echo the caller's public IP

### 7. Proxy stats — `GET /proxy/stats/`

Per-proxy performance stats (requests, bandwidth, last check). Also:
- `GET /stats/aggregate/` — account-wide aggregated usage
- `GET /activity/` — recent request activity (paginated)

### 8. Subscription plan — `GET /subscription/plan/`

Current plan: status, pricing, proxy counts, bandwidth caps, feature flags.
`GET /subscription/plan/<id>/` for a specific plan.

### 9. Pricing — `GET /subscription/pricing/`

Price lookup for a given configuration. Use this before `upgrade` / `purchase`
to show the user the cost of a change.

### 10. Upgrade plan — `POST /subscription/plan/<id>/upgrade/`

Changes proxy count / bandwidth / countries / features on an existing plan,
with prorated billing. Body includes the new config plus `payment_method` and
`recaptcha`. Returns Stripe payment details if a charge is required.

For new purchases (not upgrades) the dashboard express-checkout flow is the
simplest path — see `scripts/express_checkout.py`. The API's
`POST /subscription/purchase/` exists but requires payment tokens.

### 11. API keys — `GET/POST/PUT/DELETE /apikeys/`

Manage API keys programmatically. Usually unnecessary — users create keys via
the dashboard at https://dashboard.webshare.io/userapi/keys.

## Common gotchas

- `mode=direct` gives you N unique IPs. `mode=backbone` gives one gateway that
  rotates IPs server-side. Pick one.
- The `id` field is a string, not an integer.
- `authorization_method=ip` means the `username`/`password` still exist but are
  ignored — only the source IP matters.
- After `ondemand_refresh`, wait a few seconds before re-listing; the list is
  eventually consistent.
