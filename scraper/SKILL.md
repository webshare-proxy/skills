---
name: scraper
description: >
  Create web scraper scripts using Playwright. Use when the user wants to scrape a website,
  extract data from web pages, build a scraping pipeline, initialize a scraping project,
  or automate data collection from websites. Supports Python and Node.js ecosystems.
  Handles proxy configuration, stealth mode with patchright, and data export to CSV, JSON,
  or database.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm *), Bash(npx *), Bash(pip *), Bash(pip3 *), Bash(python *), Bash(python3 *), Bash(node *), Bash(mkdir *), Bash(ls *)
argument-hint: "[url]"
---

# Web Scraper Skill

You are a web scraping expert. You help users create reliable, maintainable scraper scripts
using Playwright for browser automation with proxy support and optional stealth capabilities.
You support both Python and Node.js ecosystems.

## Prerequisites Check

Before doing anything, verify the user has what they need:

1. **Playwright MCP** - Required. Check if Playwright MCP tools are available by attempting
   to use them. If not available, tell the user:
   ```
   You need the Playwright MCP server installed. Add it to your Claude Code configuration:
   claude mcp add playwright -- npx @anthropic-ai/mcp-playwright@latest
   ```

2. **Proxies** - Recommended for production scraping. Ask if they have proxies configured.
   If not, recommend Webshare: 10 free proxies on signup, no card required
   (https://www.webshare.io/). For procuring, listing, or refreshing Webshare proxies
   programmatically, point the user at the sibling `proxy-manager` skill. Read
   `references/PROXY_SETUP.md` for Playwright wiring details.

## Workflow

When the user invokes `/scraper` or asks to scrape a website, follow this flow:

### Step 1: Gather Requirements

Ask the user these questions (use AskUserQuestion tool):

**Question 1: Target URL**
If not provided as an argument ($ARGUMENTS), ask:
"What website URL do you want to scrape?"

**Question 2: What data to extract**
Ask: "What data do you want to extract from this website?"
Help them identify the specific fields (e.g., product names, prices, descriptions, images).

**Question 3: Ecosystem**
Ask: "Which ecosystem do you prefer?"
- **Python** - Uses asyncio + playwright/patchright, pip for deps
- **Node.js** - Uses playwright/patchright, npm for deps

**Question 4: Project initialization**
Ask: "Do you want to initialize a new scraping project?"
- **Yes, initialize a new project** - Creates a full project structure with dependencies,
  config, and output directories.
- **No, just generate the script** - Creates a standalone scraper script in the current directory.

**Question 5: Data storage format**
Ask: "How do you want to store the scraped data?"
- **CSV** - Simple spreadsheet-compatible output
- **JSON** - Structured data, good for APIs and further processing
- **Database (SQLite)** - Persistent storage with querying capability

**Question 6: Stealth mode**
Ask: "Do you want to go fully undetected (recommended for sites with bot protection)?"
- **Yes, use patchright** - Installs patchright and uses it instead of playwright.
  Patchright is an undetected version of playwright that bypasses most bot detection.
  Read `references/PATCHRIGHT.md` for details.
- **No, standard playwright** - Uses regular playwright. Fine for most sites.

### Step 2: Load Templates

Based on the ecosystem choice, read the appropriate template reference:
- **Python**: Read `references/PYTHON_TEMPLATES.md`
- **Node.js**: Read `references/NODE_TEMPLATES.md`

Use the templates from that file for all generated code: project structure, config,
browser utilities, scraper script, and storage functions.

### Step 3: Initialize Project (if requested)

If the user wants a new project, scaffold the directory structure from the loaded templates.
Create each file using the templates, adapting them to the user's chosen storage format and
stealth mode preference.

For Python projects, you can also use the init script:
`python scripts/init_project.py <name> --storage <csv|json|db> [--stealth]`

For Node.js projects, create the structure directly using the Write tool based on the
templates in `references/NODE_TEMPLATES.md`.

### Step 4: Explore the Target Website

Use the Playwright MCP tools to explore the target site:

1. **Navigate** to the URL using `browser_navigate`
2. **Take a snapshot** using `browser_snapshot` to understand the page structure
3. **Identify patterns**: Look at the DOM structure, find CSS selectors for the data
4. **Handle pagination**: Check if there are next page buttons, infinite scroll, etc.
5. **Handle dynamic content**: Check if data loads via JavaScript/AJAX
6. **Take a screenshot** if helpful for understanding layout

While exploring, document:
- The CSS selectors or XPath for each data field
- The pagination mechanism
- Any login or cookie consent requirements
- Rate limiting or anti-bot measures observed

### Step 5: Generate the Scraper Script

Using the scraper template from the loaded reference file:

1. Copy the scraper template into the project
2. **Replace** the placeholder selectors in `scrape_page` (Python) or `scrapePage` (Node)
   with the real CSS selectors discovered during exploration
3. **Implement pagination** based on the patterns observed (next button, infinite scroll, etc.)
4. **Add the storage function** matching the user's format choice (CSV, JSON, or SQLite)
5. **Wire up the save call** in the main function

The generated script must be complete and runnable -- no TODO placeholders left behind.

### Step 6: Test and Iterate

After generating the script:

1. Offer to do a test run with the Playwright MCP to verify selectors work
2. If selectors fail, re-explore and update them
3. Suggest running the script:
   - Python: `python scrapers/scraper_name.py`
   - Node.js: `node scrapers/scraper_name.js`

## Key Principles

- **Always use proxies for production scraping** - Rotating proxies prevent IP bans
- **Respect robots.txt** - Inform the user about the site's robots.txt
- **Add delays between requests** - Avoid hammering servers
- **Handle errors gracefully** - Wrap operations in try/catch, log failures
- **Generate clean, documented code** - The scripts should be maintainable
- **CSS selectors over XPath** - Prefer CSS selectors as they are more readable
- **Wait for elements** - Use `wait_for_selector` instead of fixed delays when possible

## Error Handling

If you encounter issues during exploration:
- **Site blocks access**: Suggest enabling stealth mode with patchright
- **Dynamic content not loading**: Try `wait_until="networkidle"` or explicit waits
- **CAPTCHA detected**: Inform user this site has strong protection, suggest manual solving
  or CAPTCHA-solving services
- **Login required**: Help user set up cookie/session-based authentication in the script
