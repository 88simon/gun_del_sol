# Solana Address Monitoring Service

A local Flask service that stores and manages Solana addresses for future Telegram monitoring.

## Current Status: Phase 1 MVP

This is a storage-only implementation. Future phases will add:
- Telegram bot integration
- Real-time transaction notifications
- Configurable thresholds per address

## Requirements

- Python 3.8+
- Flask (auto-installed by launcher)

## Installation

### Quick Start

1. Double-click `start_monitor_service.bat`
2. The script will automatically install Flask if needed
3. Service runs at `http://localhost:5001`

### Manual Installation

```bash
cd monitor
pip install -r requirements.txt
python monitor_service.py
```

## Usage

### Registering Addresses

**From AutoHotkey script:**
- Hover over any Solana address
- Hold Ctrl + Click F14 (or Ctrl+XButton2)

**From web dashboard:**
1. Visit `http://localhost:5001`
2. Enter address in the form
3. Optionally add a note/tag (e.g., "whale wallet", "friend")

### Web Dashboard

Open `http://localhost:5001` in your browser to:
- View all monitored addresses
- Add/remove addresses manually
- Edit notes/tags
- Export backup (JSON)
- Import from backup
- Search addresses by address or note

### API Endpoints

```
POST   /register              - Register new address
GET    /addresses             - List all addresses
GET    /address/<addr>        - Get address details
DELETE /address/<addr>        - Remove address
PUT    /address/<addr>/note   - Update address note
POST   /import                - Import addresses from backup
POST   /clear                 - Clear all addresses
GET    /health                - Health check
```

## Data Storage

Addresses are stored in `monitored_addresses.json`:

```json
{
  "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": {
    "address": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "registered_at": "2025-11-02T10:30:00",
    "threshold": 100,
    "total_notifications": 0,
    "last_notification": null,
    "note": "Example wallet"
  }
}
```

**Note:** This file is git-ignored to protect your privacy.

## Configuration

### Default Settings

- **Port:** 5001
- **Host:** localhost (not accessible from network)
- **Default Threshold:** 100 SOL (for future notifications)

### Changing Port

Edit `monitor_service.py` line 306:

```python
app.run(host='localhost', port=5001, debug=False)
```

## Backup & Restore

### Export Backup

1. Visit dashboard at `http://localhost:5001`
2. Click "Export Backup"
3. JSON file downloads automatically

### Import Backup

1. Visit dashboard
2. Click "Import Backup"
3. Select previously exported JSON file

### Manual Backup

Copy `monitored_addresses.json` to safe location.

## Troubleshooting

### Service won't start

**Port already in use:**
```bash
# Check what's using port 5001
netstat -ano | findstr :5001

# Kill the process or change port in monitor_service.py
```

**Python not found:**
- Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**Flask installation fails:**
```bash
python -m pip install --upgrade pip
pip install Flask
```

### Can't access dashboard

- Verify service is running (console should show "Running on http://localhost:5001")
- Check browser URL is exactly `http://localhost:5001` (not https)
- Try different browser if issues persist

### Address not registering from hotkey

1. Verify service is running at `http://localhost:5001/health`
2. Check console for error messages
3. Ensure address is valid Solana base58 (32-44 characters)

## Security & Privacy

- Service only listens on localhost (not accessible from network)
- No external API calls (except future Telegram integration)
- Data stored locally in `monitored_addresses.json`
- File is git-ignored by default

## Future Roadmap

### Phase 2: Configuration System
- YAML config file for flexible settings
- Per-address thresholds
- Multiple notification methods

### Phase 3: Telegram Integration
- Bot token configuration
- Real-time transaction monitoring
- Customizable alert messages

### Phase 4: Advanced Features
- Webhook support
- Discord integration
- Historical analytics

---

**License:** Free to use and modify. No warranty provided.