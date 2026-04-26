# W&B Logs Management

A lightweight single-file web app for browsing and comparing your [Weights & Biases](https://wandb.ai) training runs — no cloud, no install, runs entirely in your browser.
<img width="2500" height="1276" alt="58654da30baf805d8ff52673bec169c1" src="https://github.com/user-attachments/assets/b55f7dd7-6955-40ea-9222-c43b113c1b6a" />

**[▶ Open Online](https://matchayou.github.io/WB-Logs-Management)**

---

## Features

- Browse runs across multiple W&B projects in one place
- Training curves, Config, Summary, Logs, and Overview tabs per run
- Compare runs side-by-side (charts, params diff, custom config)
- Save compare records with comments and reopen them later
- Multi-select tag & state filters, per-project sort/field preferences
- Command-line args auto-parsed into Config view
- Bilingual UI: switch between Chinese and English in Settings
- Local annotations and settings are stored in project-side JSON files via the local proxy

---

## Usage

### Option A — Online (no install)

1. Open the link above
2. Click **Settings**, enter your W&B API Key and entity/project names
3. Start the local proxy (required to bypass CORS):

```bash
python proxy.py
```

4. In Settings → set **Custom Proxy URL** to `http://localhost:8080`

Note: compare records, run annotations, and app settings that need file persistence require the local proxy.

---

### Option B — One-click local launcher

Requires Python 3 (no extra packages needed).

```bash
git clone https://github.com/Matchayou/WB-Logs-Management.git
cd W-B_Logs_Management
python run.py
```

This starts the proxy automatically and opens the app in your browser.  
Set **Custom Proxy URL** to `http://localhost:8080` in Settings on first run.

---

## Files

| File | Description |
|------|-------------|
| `index.html` | The entire app (single file, no build step) |
| `proxy.py` | Local CORS proxy (stdlib only, no pip install) |
| `run.py` | One-click launcher: starts proxy + opens browser |
| `app_settings.json` | Local app settings persisted next to the project |
| `run_annotations.json` | Local run notes, tags, favorites, aliases, and custom configs |
| `compare_sessions.json` | Saved compare records and comments |

These JSON files are ignored by git via `.gitignore` so local data is not committed by default.

---

## W&B API Key

Get your key at [wandb.ai/settings](https://wandb.ai/settings).  
It is sent only to `api.wandb.ai` through the local proxy. When file persistence is enabled, app settings are also stored locally in `app_settings.json` on your machine.
