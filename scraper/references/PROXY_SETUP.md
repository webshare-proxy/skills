# Proxy Setup Guide

## Why Proxies?

Web scraping without proxies leads to IP bans. Rotating residential proxies make your
requests appear as normal user traffic from different locations.

## Recommended Provider: Webshare

Get ethically sourced proxies from [webshare.io](https://www.webshare.io/).
- **10 free proxies** available on signup (no credit card required)
- Residential and datacenter options
- Rotating proxy support
- API for proxy list management

## Configuration

### Environment Variables

Set these in your `.env` file or shell environment:

```bash
# Single proxy
PROXY_SERVER=http://proxy-host:port
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password

# Rotating proxy (Webshare format)
PROXY_SERVER=http://p.webshare.io:80
PROXY_USERNAME=your_webshare_username
PROXY_PASSWORD=your_webshare_password
```

### Webshare Rotating Proxy Setup

With the `webshare` CLI installed (`brew install webshare-proxy/tap/webshare`)
and `WEBSHARE_API_KEY` exported, build the rotating endpoint in one line:

```bash
# Full rotating proxy URL (credentials fetched from your proxy config)
webshare proxy-url --rotate

# Country-targeted, or a pool of sticky sessions for parallel workers
webshare proxy-url --country us --rotate
webshare proxy-url --sessions 5
```

Without the CLI, do it manually:

1. Sign up at https://www.webshare.io/
2. Go to Dashboard > Proxy > List
3. Click "Rotating Proxy" tab
4. Copy the proxy address, username, and password
5. Set as environment variables above

### Using a Proxy List

For multiple static proxies, dump your list with the CLI:

```bash
# address:port:username:password lines
webshare proxies list > proxies.txt

# Or filtered by country
webshare proxies list --country us,fr > proxies.txt
```

Or create a `proxies.txt` file by hand:

```
http://user:pass@host1:port
http://user:pass@host2:port
http://user:pass@host3:port
```

Then use this in your scraper config:

```python
import random

def load_proxies(filepath="proxies.txt"):
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]

def get_random_proxy(proxies):
    proxy_url = random.choice(proxies)
    return {"server": proxy_url}
```

### Playwright Proxy Configuration

```python
# In browser launch
browser = await playwright.chromium.launch(
    proxy={
        "server": "http://p.webshare.io:80",
        "username": "your_username",
        "password": "your_password",
    }
)

# Or per-context (different proxy per tab)
context = await browser.new_context(
    proxy={
        "server": "http://p.webshare.io:80",
        "username": "your_username",
        "password": "your_password",
    }
)
```

## Proxy Rotation Strategies

- **Per-request rotation**: Use Webshare's rotating endpoint (changes IP each request)
- **Per-session rotation**: Create a new browser context with a different proxy for each session
- **Geographic targeting**: Some providers let you select proxy country for geo-specific content
- **Sticky sessions**: Keep the same IP for a session duration (useful for multi-page flows)

## Testing Your Proxy

```python
import asyncio
from playwright.async_api import async_playwright

async def test_proxy():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={
                "server": os.getenv("PROXY_SERVER"),
                "username": os.getenv("PROXY_USERNAME"),
                "password": os.getenv("PROXY_PASSWORD"),
            }
        )
        page = await browser.new_page()
        await page.goto("https://httpbin.org/ip")
        content = await page.content()
        print(content)  # Should show proxy IP, not your real IP
        await browser.close()

asyncio.run(test_proxy())
```
