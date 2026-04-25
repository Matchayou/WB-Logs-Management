# W&B Logs Management

A lightweight single-file web app for browsing and comparing your [Weights & Biases](https://wandb.ai) training runs — no cloud, no install, runs entirely in your browser.

**[▶ Open Online](https://matchayou.github.io/WB-Logs-Management)**

---

## Features

- Browse runs across multiple W&B projects in one place
- Training curves, Config, Summary, Logs, and Overview tabs per run
- Compare runs side-by-side (charts, params diff, custom config)
- Multi-select tag & state filters, per-project sort/field preferences
- Command-line args auto-parsed into Config view
- All data stays local — nothing is stored outside your browser

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

---

## W&B API Key

Get your key at [wandb.ai/settings](https://wandb.ai/settings).  
It is stored only in your browser's `localStorage` and never sent anywhere except directly to `api.wandb.ai` via the local proxy.
