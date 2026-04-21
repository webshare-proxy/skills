# Patchright - Undetected Playwright

## What is Patchright?

[Patchright](https://github.com/nickoala/patchright) is a patched version of Playwright that
bypasses most bot detection systems. It modifies Playwright's browser automation to avoid
common detection fingerprints like:

- `navigator.webdriver` flag
- Automation-related JavaScript properties
- Chrome DevTools Protocol detection
- Headless browser detection signatures

## When to Use

Use patchright when:
- The target site uses Cloudflare, DataDome, or similar bot protection
- You get blocked or see CAPTCHAs with regular Playwright
- The site checks for automation fingerprints
- You need to appear as a regular browser user

## Python Setup

```bash
pip install patchright
python -m patchright install chromium
```

Drop-in replacement -- just change the import:

```python
# Standard playwright
# from playwright.async_api import async_playwright

# Patchright (undetected)
from patchright.async_api import async_playwright
```

### Auto-fallback pattern (Python)

```python
try:
    from patchright.async_api import async_playwright
except ImportError:
    from playwright.async_api import async_playwright
```

## Node.js Setup

```bash
npm install patchright
npx patchright install chromium
```

Drop-in replacement -- just change the require:

```javascript
// Standard playwright
// const { chromium } = require("playwright");

// Patchright (undetected)
const { chromium } = require("patchright");
```

### Auto-fallback pattern (Node.js)

```javascript
let playwright;
try {
  playwright = require("patchright");
} catch {
  playwright = require("playwright");
}
```

## Combined with Proxies

For maximum stealth, combine patchright with rotating proxies. The API is identical to
Playwright in both Python and Node.js -- just swap the import/require.

## Detection Test

Test your stealth setup against common detection sites:

```
https://bot.sannysoft.com/
```

Navigate to the page and check `navigator.webdriver` -- it should be `false` or `undefined`.
