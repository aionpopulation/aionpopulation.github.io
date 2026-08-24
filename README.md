# Aion Private Server Population Tracker

Compares live player counts across 5 Aion private servers on a single static page.
Data is scraped every 30 minutes via GitHub Actions and committed back as `data.json`.
The page reads `data.json` directly — no server needed.

## Setup

### 1. Create a GitHub repo
Push this folder to a new **public** GitHub repository.

### 2. Enable GitHub Pages
Settings → Pages → Source: **Deploy from a branch** → Branch: `main`, folder: `/ (root)`.
Your site will be at `https://<you>.github.io/<repo-name>/`.

### 3. Trigger the first scrape
Actions → **Scrape Server Population** → **Run workflow**.
After that it runs automatically every 30 minutes.

## Files

| File | Purpose |
|---|---|
| `index.html` | Static page — reads `data.json` and renders the comparison |
| `data.json` | Scraped population data — auto-updated by Actions |
| `scrape.py` | Python scraper — one function per server |
| `.github/workflows/scrape.yml` | Cron job that runs the scraper and commits `data.json` |

## Data sources (all confirmed via HAR)

| Server | Method | Notes |
|---|---|---|
| EuroAion | HTML regex — `ONLINE <n>` in navbar | Includes Elyos/Asmodian % |
| AionEmpire | HTML regex — `Онлайн <n>` in navbar | |
| OriginAion | JSON API — `GET /api/server-status` | |
| AionRiftShade | Discord API — `GET discord.com/api/v9/invites/VpjnUAPzhF?with_counts=true` | Shows Discord online members, not in-game count. Flagged in the UI. |
| AionDestiny | JSON API — `GET /api/online` | Includes light (Elyos) / dark (Asmodian) counts |
