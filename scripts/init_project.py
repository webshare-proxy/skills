#!/usr/bin/env python3
"""
Initialize a new scraping project with proper directory structure and boilerplate.

Usage:
    python init_project.py <project_name> [--storage csv|json|db] [--stealth]

Arguments:
    project_name    Name of the project directory to create
    --storage       Data storage format: csv, json, or db (default: json)
    --stealth       Use patchright instead of playwright for stealth mode
"""

import argparse
import os
import sys


def create_dir(path):
    os.makedirs(path, exist_ok=True)


def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created {path}")


def init_project(project_name, storage="json", stealth=False):
    base = project_name

    if os.path.exists(base):
        print(f"Error: Directory '{base}' already exists.")
        sys.exit(1)

    print(f"Initializing scraper project: {base}")
    print(f"  Storage: {storage}")
    print(f"  Stealth: {'patchright' if stealth else 'playwright'}")
    print()

    # Create directories
    for d in [
        f"{base}/scrapers",
        f"{base}/output/csv",
        f"{base}/output/json",
        f"{base}/output/db",
        f"{base}/config",
        f"{base}/utils",
    ]:
        create_dir(d)
        print(f"  Created {d}/")

    # --- requirements.txt ---
    playwright_dep = "patchright>=1.0.0" if stealth else "playwright>=1.40.0"
    deps = [
        playwright_dep,
        "python-dotenv>=1.0.0",
    ]
    if storage == "db":
        # sqlite3 is built-in, no extra dep needed
        pass
    write_file(f"{base}/requirements.txt", "\n".join(deps) + "\n")

    # --- .env.example ---
    write_file(
        f"{base}/.env.example",
        """# Proxy configuration (get proxies from https://www.webshare.io/)
PROXY_SERVER=http://p.webshare.io:80
PROXY_USERNAME=
PROXY_PASSWORD=

# Scraper settings
HEADLESS=true
REQUEST_DELAY=1.0
MAX_PAGES=10
""",
    )

    # --- .gitignore ---
    write_file(
        f"{base}/.gitignore",
        """.env
output/
__pycache__/
*.pyc
.venv/
venv/
""",
    )

    # --- config/config.py ---
    write_file(
        f"{base}/config/config.py",
        '''"""Scraper configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

PROXY_SERVER = os.getenv("PROXY_SERVER", "")
PROXY_USERNAME = os.getenv("PROXY_USERNAME", "")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "10"))

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
VIEWPORT = {"width": 1920, "height": 1080}


def get_proxy_config():
    """Return proxy config dict for Playwright, or None if not set."""
    if not PROXY_SERVER:
        return None
    return {
        "server": PROXY_SERVER,
        "username": PROXY_USERNAME,
        "password": PROXY_PASSWORD,
    }
''',
    )

    # --- utils/__init__.py ---
    write_file(f"{base}/utils/__init__.py", "")

    # --- utils/browser.py ---
    pw_import = (
        "from patchright.async_api import async_playwright"
        if stealth
        else "from playwright.async_api import async_playwright"
    )
    write_file(
        f"{base}/utils/browser.py",
        f'''"""Browser setup utilities with proxy support."""

{pw_import}
from config.config import get_proxy_config, HEADLESS, USER_AGENT, VIEWPORT


async def create_browser(playwright):
    """Launch a browser instance with proxy configuration."""
    proxy = get_proxy_config()
    browser = await playwright.chromium.launch(
        headless=HEADLESS,
        proxy=proxy,
    )
    context = await browser.new_context(
        user_agent=USER_AGENT,
        viewport=VIEWPORT,
        locale="en-US",
    )
    return browser, context


async def create_page(context):
    """Create a new page with standard settings."""
    page = await context.new_page()
    page.set_default_timeout(30000)
    return page
''',
    )

    # --- utils/storage.py ---
    storage_code = '''"""Data storage utilities."""

import csv
import json
import os
from datetime import datetime

'''

    if storage == "csv" or storage == "all":
        storage_code += '''
def save_to_csv(data, output_dir="output/csv", filename=None):
    """Save scraped data to a CSV file."""
    os.makedirs(output_dir, exist_ok=True)
    if not data:
        print("No data to save.")
        return None
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scrape_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} items to {filepath}")
    return filepath

'''

    if storage == "json" or storage == "all":
        storage_code += '''
def save_to_json(data, output_dir="output/json", filename=None):
    """Save scraped data to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scrape_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} items to {filepath}")
    return filepath

'''

    if storage == "db" or storage == "all":
        storage_code += '''
import sqlite3


def save_to_db(data, db_path="output/db/scraper.db", table_name="scraped_data"):
    """Save scraped data to a SQLite database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if not data:
        print("No data to save.")
        return None
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    columns = list(data[0].keys())
    col_defs = ", ".join(f\'"{col}" TEXT\' for col in columns)
    cursor.execute(
        f\'CREATE TABLE IF NOT EXISTS "{table_name}" \'
        f"(id INTEGER PRIMARY KEY AUTOINCREMENT, "
        f"scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, {col_defs})"
    )
    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(f\'"{col}"\' for col in columns)
    for item in data:
        values = [str(item.get(col, "")) for col in columns]
        cursor.execute(
            f\'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})\',
            values,
        )
    conn.commit()
    conn.close()
    print(f"Saved {len(data)} items to {db_path} (table: {table_name})")
    return db_path

'''

    write_file(f"{base}/utils/storage.py", storage_code)

    # --- config/__init__.py ---
    write_file(f"{base}/config/__init__.py", "")

    # --- scrapers/__init__.py ---
    write_file(f"{base}/scrapers/__init__.py", "")

    # --- README.md ---
    write_file(
        f"{base}/README.md",
        f"""# {project_name}

Web scraper project generated by [scraper-skill](https://github.com/user/scraper-skill).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   {"python -m patchright install chromium" if stealth else "python -m playwright install chromium"}
   ```

2. Configure proxies:
   ```bash
   cp .env.example .env
   # Edit .env with your proxy credentials
   # Get free proxies at https://www.webshare.io/
   ```

3. Run a scraper:
   ```bash
   python -m scrapers.example --url "https://example.com"
   ```

## Project Structure

```
{project_name}/
├── scrapers/       # Scraper scripts
├── output/         # Scraped data ({storage})
├── config/         # Configuration
├── utils/          # Browser & storage utilities
└── requirements.txt
```

## Adding a New Scraper

Create a new file in `scrapers/` and use the browser/storage utilities:

```python
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.browser import create_browser, create_page
from utils.storage import save_to_{"csv" if storage == "csv" else "json" if storage == "json" else "db"}
{pw_import}


async def scrape(url):
    async with async_playwright() as p:
        browser, context = await create_browser(p)
        page = await create_page(context)
        await page.goto(url, wait_until="networkidle")

        # Your scraping logic here
        data = []

        await browser.close()
    return data


if __name__ == "__main__":
    data = asyncio.run(scrape("https://example.com"))
    print(f"Scraped {{len(data)}} items")
```
""",
    )

    print(f"\nProject '{base}' initialized successfully!")
    print(f"\nNext steps:")
    print(f"  cd {base}")
    print(f"  pip install -r requirements.txt")
    if stealth:
        print(f"  python -m patchright install chromium")
    else:
        print(f"  python -m playwright install chromium")
    print(f"  cp .env.example .env")
    print(f"  # Edit .env with your proxy credentials")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize a scraping project")
    parser.add_argument("project_name", help="Name of the project directory")
    parser.add_argument(
        "--storage",
        choices=["csv", "json", "db"],
        default="json",
        help="Data storage format (default: json)",
    )
    parser.add_argument(
        "--stealth",
        action="store_true",
        help="Use patchright for stealth mode",
    )
    args = parser.parse_args()
    init_project(args.project_name, args.storage, args.stealth)
