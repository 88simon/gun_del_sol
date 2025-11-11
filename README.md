# Gun Del Sol

[![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)
[![Backend CI](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/Backend%20CI/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions)

> **Note:** Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub username and repository name.

Gun Del Sol pairs an AutoHotkey action wheel with a local Solana intelligence backend. One hand stays on the mouse while the backend handles watchlists, Helius-powered analysis, CSV exports, and WebSocket notifications for the Next.js dashboard.

## Components

| Path | Purpose |
| --- | --- |
| `action_wheel.ahk` | Main AutoHotkey v2 script (radial menu, clipboard capture, Solscan helpers) |
| `action_wheel_settings.ini` | Auto-generated user settings for the wheel |
| `start.bat` | Launches the action wheel, FastAPI backend (5003), and Next.js dashboard (3000) |
| `start_backend.bat` | Starts only the FastAPI backend service |
| `start_frontend.bat` | Starts the dashboard located in `../gun-del-sol-web` |
| `backend/` | Modular FastAPI backend with routers, services, WebSocket support, Helius integration, SQLite storage, and configs |
| `docs/` | Security guides and audits |
| `tools/` | Utilities such as `test_mouse_buttons.ahk` |
| `userscripts/` | Browser helpers (for example `defined-fi-autosearch.user.js`) |
| `Lib/` | AutoHotkey libraries bundled with the script |

## Requirements

- Windows 10 or later
- AutoHotkey v2.x
- Mouse with side buttons (XButton1/XButton2) recommended
- Python 3.9+ for the backend services
- Node.js 18+ if you run the external Next.js dashboard
- Helius API key (free tier works) for on-box token analysis

## Quick Start

### Action Wheel Only
1. Install AutoHotkey v2 from https://www.autohotkey.com/.
2. Double-click `action_wheel.ahk` (or run `start.bat` and close the backend windows you do not need).
3. Look for the green H tray icon, then press the default wheel hotkey (backtick `` ` ``) to open the radial menu.
4. Configure hotkeys or wheel slices any time via `Tray icon -> Settings`. Changes persist to `action_wheel_settings.ini`.

### Full Stack (Action Wheel + Backend + Dashboard)
1. Install Python 3.10+ and run:
   ```bash
   # Production
   pip install -r backend/requirements.txt

   # Development (includes testing and linting tools)
   pip install -r backend/requirements-dev.txt
   ```
2. Copy `backend/config.example.json` to `backend/config.json`, set `helius_api_key`, and tune default thresholds if needed.
3. Start everything with `start.bat`, or run `start_backend.bat` and `start_frontend.bat` separately. The frontend expects the companion repo at `../gun-del-sol-web`.
4. Open http://localhost:3000 for the dashboard, http://localhost:5003 for the REST API health check. WebSocket connections use the same port at `ws://localhost:5003/ws`.

## Wheel Menu

- Default hotkey: backtick `` ` `` (change via the Settings dialog).
- Mouse usage: hold the hotkey, glide toward an action, and release or click to run it.
- Keyboard usage: press number keys 1-6 while the wheel is open.
- Cancel: press Esc or select the Cancel slice.

Default slices (all configurable):
1. **Solscan** – open the hovered address in Solscan.
2. **Exclude** – add the hovered address to Solscan filters.
3. **Monitor** – register the address with the local backend.
4. **Defined.fi** – trigger the Tampermonkey helper for token pivots.
5. **Analyze** – send the token to the backend for early-bidder analysis.
6. **Cancel** – dismiss the wheel.

## Backend Monitoring and Analysis

- **Modular FastAPI backend** (`backend/app/`) with organized routers and services:
  - `/analyze/*` - Token analysis jobs and status
  - `/api/tokens/*` - Token history, trash, CSV/Axiom exports
  - `/multi-token-wallets` - Wallet tracking across tokens
  - `/wallets/*` - Wallet tagging and balance refresh
  - `/codex` - Tagged wallet database
  - `/register`, `/addresses` - Watchlist management
  - `/webhooks/*` - Webhook configuration
  - `/api/settings` - API configuration
- `backend/helius_api.py` wraps Helius endpoints plus local heuristics to score buyers.
- State lives in JSON files and the SQLite database inside `backend/`. All sensitive outputs (`analysis_results/`, `axiom_exports/`, `config.json`, databases) remain git-ignored.
- Configure via environment variables (`HELIUS_API_KEY`, `API_RATE_DELAY`, etc.) or `backend/config.json`.
- Full API documentation available at http://localhost:5003/docs when running.

## Real-time Notifications

- Unified WebSocket support in FastAPI at `ws://localhost:5003/ws`.
- Broadcasts `analysis_start`, `analysis_complete`, and other real-time events.
- Dashboard and other clients maintain a single connection for instant updates without polling.

## Customization

- **Hotkeys and slices:** `Tray icon -> Settings`.
- **Wheel visuals:** edit `action_wheel.ahk` (search for `WheelConfig`).
- **Backend presets:** adjust `backend/api_settings.json` or call the `/api/settings` endpoint.
- **Tampermonkey helper:** tweak selectors in `userscripts/defined-fi-autosearch.user.js`.

## Development & CI

Gun Del Sol includes comprehensive CI/CD pipelines with GitHub Actions for the backend:

- **Automated Testing:** Backend tests with pytest and coverage reporting
- **Code Quality:** Black, isort, flake8 for Python code formatting and linting
- **OpenAPI Schema:** Auto-exports API schema and generates TypeScript types
- **Multi-version Testing:** Tests across Python 3.10, 3.11, and 3.12

> **Note:** The frontend ([gun-del-sol-web](../gun-del-sol-web)) has its own separate CI pipeline in its repository.

**Quick commands:**
```bash
# Install dev dependencies (includes pytest, black, isort, flake8)
pip install -r backend/requirements-dev.txt

# Run all backend CI checks locally (before pushing)
run_ci_checks.bat  # Windows
./run_ci_checks.sh # Unix/Linux/macOS

# Fix formatting issues
cd backend && black . && isort .

# Run tests
cd backend && pytest -v

# Check code quality
cd backend && flake8 .
```

📚 **Documentation:**
- [CI Quick Start](.github/CI_QUICKSTART.md)
- [Full CI Documentation](.github/workflows/README.md)
- [Backend Tests](backend/tests/README.md)
- [CI Implementation Summary](.github/CI_IMPLEMENTATION_SUMMARY.md)

## Troubleshooting

- **Mouse buttons ignored:** run `tools/test_mouse_buttons.ahk` to confirm Windows sees the buttons, then remap inside the Settings dialog.
- **Backend refuses to start:** ensure Python 3.10+ is in PATH, then run `python -m uvicorn app.main:app --app-dir backend` for direct logs. Port 5003 must be free.
- **Helius analysis skipped:** verify `backend/config.json` has a valid `helius_api_key` or export it as `HELIUS_API_KEY`. Watch the console for quota errors.
- **Dashboard cannot connect to WebSocket:** confirm `start_backend.bat` launched the FastAPI server on port 5003 and that your browser allows `ws://localhost:5003/ws`.
- **CI checks failing:** run `run_ci_checks.bat` locally to identify issues before pushing.

## Security and Data Hygiene

- Sensitive outputs stay inside `backend/` and are already ignored by `.gitignore`. See `SECURITY.md` plus `docs/SECURITY_AUDIT.md` for the full checklist.
- Never commit `backend/config.json`, the SQLite databases, or anything under `backend/analysis_results/` or `backend/axiom_exports/`.
- Disable verbose logging before demos by toggling the flags in `backend/debug_config.py` and the helpers in `secure_logging.py`.

---

Gun Del Sol is intentionally hackable. Extend the wheel, add new API routes, or plug in different data providers—just keep the local-first security model intact.
