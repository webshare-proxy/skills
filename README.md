# scraper-skill

An [Agent Skill](https://agentskills.io/) for creating web scraper scripts using Playwright. Works with Claude Code, Cursor, and any agent that supports the open Agent Skills standard.

Give it a URL, and it will explore the website using Playwright MCP, identify the data structure, and generate a production-ready scraping script with proxy support, data storage, and optional stealth mode.

Supports both **Python** and **Node.js** ecosystems.

## Installation

### Using the skills CLI (recommended)

```bash
npx skills add user/scraper-skill
```

### Manual installation (Claude Code)

Clone into your personal skills directory:

```bash
git clone https://github.com/user/scraper-skill.git ~/.claude/skills/scraper
```

Or for project-level:

```bash
git clone https://github.com/user/scraper-skill.git .claude/skills/scraper
```

## Prerequisites

### 1. Playwright MCP Server

You need the Playwright MCP server installed for Claude Code to browse websites:

```bash
claude mcp add playwright -- npx @anthropic-ai/mcp-playwright@latest
```

### 2. Proxies (recommended)

For production scraping, you need rotating proxies to avoid IP bans.

**Recommended: [Webshare](https://www.webshare.io/)** - ethically sourced proxies with **10 free proxies** on signup (no credit card required).

1. Sign up at [webshare.io](https://www.webshare.io/)
2. Go to Dashboard > Proxy > List > Rotating Proxy
3. Copy your proxy credentials
4. Set environment variables:
   ```bash
   export PROXY_SERVER=http://p.webshare.io:80
   export PROXY_USERNAME=your_username
   export PROXY_PASSWORD=your_password
   ```

### 3. Runtime

Install the runtime for your chosen ecosystem:

**Python:**
```bash
pip install playwright
python -m playwright install chromium
```

**Node.js:**
```bash
npm install playwright
npx playwright install chromium
```

## Usage

Invoke the skill with a URL:

```
/scraper https://example.com/products
```

Or just ask naturally:

```
Scrape the product listings from https://example.com/products
```

The skill will:

1. **Ask what data to extract** - specify the fields you need (names, prices, etc.)
2. **Ask your ecosystem preference** - Python or Node.js
3. **Ask about project setup** - initialize a full project or generate a standalone script
4. **Ask about data storage** - CSV, JSON, or SQLite database
5. **Ask about stealth mode** - use patchright for sites with bot protection
6. **Explore the website** - uses Playwright MCP to navigate and identify page structure
7. **Generate a scraper script** - produces a ready-to-run script with:
   - Proxy rotation support
   - Pagination handling
   - Error handling
   - Your chosen data storage format

## Project Structure

When you choose to initialize a project, the skill creates:

**Python:**
```
my-scraper/
├── scrapers/           # Your scraper scripts
├── output/             # Scraped data (csv/, json/, or db/)
├── config/
│   └── config.py
├── utils/
│   ├── browser.py
│   └── storage.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

**Node.js:**
```
my-scraper/
├── scrapers/           # Your scraper scripts
├── output/             # Scraped data (csv/, json/, or db/)
├── config/
│   └── config.js
├── utils/
│   ├── browser.js
│   └── storage.js
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

## Features

- **Python & Node.js support** - choose your preferred ecosystem
- **Playwright MCP integration** - explores websites interactively to find the right selectors
- **Proxy support** - built-in rotating proxy configuration with Webshare
- **Stealth mode** - optional patchright integration for bypassing bot detection
- **Multiple storage formats** - CSV, JSON, or SQLite database
- **Project scaffolding** - full project structure with utilities and config
- **Production-ready scripts** - generated code includes error handling, pagination, and delays

## Stealth Mode (Patchright)

For websites with bot protection (Cloudflare, DataDome, etc.), the skill can use [patchright](https://github.com/nickoala/patchright) - an undetected version of Playwright that bypasses common detection:

**Python:**
```bash
pip install patchright
python -m patchright install chromium
```

**Node.js:**
```bash
npm install patchright
npx patchright install chromium
```

When stealth mode is enabled, the generated scripts automatically use patchright imports instead of playwright.

## License

MIT
