# Solscan Mouse Hotkey

Instantly open Solscan for any Solana address by hovering and clicking your side mouse button.

## Features

- **F14/XButton2**: Open any Solana address in Solscan with custom filters
- **F13/XButton1**: Add exclusion filters to current Solscan page (per-tab persistence)
- **Ctrl+F14**: Register addresses for Telegram monitoring
- Smart text detection with multiple fallback strategies
- Safe clipboard handling - restores your clipboard after use
- Validates Solana base58 addresses (32-44 characters)

## Requirements

- **Windows** 10 or later
- **AutoHotkey v2.0+** - [Download here](https://www.autohotkey.com/)
- A mouse with side buttons (or Logitech G502/similar with G HUB)

**Optional (for Telegram Monitoring):**
- Python 3.8+ and Flask (auto-installed by launcher)

## Installation

### 1. Install AutoHotkey v2

Download and install AutoHotkey v2 from [autohotkey.com](https://www.autohotkey.com/)

**Important:** Install v2.0+, not v1.1

### 2. Configure Your Mouse (G HUB Users Only)

If you have Logitech G HUB:

1. Open G HUB and select your mouse profile
2. Map your side buttons:
   - One button → `F14` (for opening addresses)
   - Other button → `F13` (for exclusions)
3. Save the profile

**Why F13/F14?** G HUB blocks native XButton signals. F13/F14 are extended function keys that work reliably.

**No G HUB?** The script works directly with XButton1/XButton2. Skip this step.

### 3. Run the Script

**Recommended:** Double-click `start_solscan_hotkey.bat`

**Or manually:** Double-click `solscan_hotkey.ahk` (green "H" icon appears in system tray)

**Auto-start on boot:** Press Win+R, type `shell:startup`, create a shortcut to `solscan_hotkey.ahk`

## Usage

### Basic Lookup (F14)

1. Hover over any Solana address
2. Click F14-mapped button (or XButton2)
3. Solscan opens with filters: SOL transfers only, no spam, 100+ SOL minimum

### Exclusion Filters (F13)

Filter out specific addresses to focus on interesting counterparties.

**Workflow:**
1. Open a wallet on Solscan (using F14 or manually)
2. Hover over addresses you want to exclude (DEXs, exchanges, etc.)
3. Click F13 to add exclusion - page reloads with that address filtered out
4. Repeat to exclude more addresses (up to 5 max due to Solscan limits)

**Per-tab persistence:** Exclusions are stored in the browser URL. Each tab maintains independent filters - switch tabs freely, reload manually, F13 always works on the current tab.

**Example:**
Analyzing whale wallet? Exclude Jupiter, Raydium, Pump.fun to see only novel counterparties.

### Telegram Monitoring (Beta)

**Start service:**
1. Double-click `start_monitor_service.bat`
2. Service runs at `http://localhost:5001`

**Register addresses:**
- Hover over address → Hold Ctrl + Click F14/XButton2
- View registered addresses at `http://localhost:5001` (web dashboard)

**Current status:** Phase 1 MVP - stores addresses locally, no actual notifications yet.

## Controls

- **F14** (or XButton2) - Open address in Solscan
- **F13** (or XButton1) - Add exclusion filter
- **Ctrl+F14** (or Ctrl+XButton2) - Register for monitoring
- **Ctrl+Alt+Q** - Exit script
- **Right-click tray icon** - Reload or exit

## Troubleshooting

### Mouse button not working

**G HUB users:**
1. Verify buttons are mapped to F13/F14 in G HUB
2. Ensure profile is active (not "Default")
3. Reload script: Right-click tray icon → Reload
4. Test by pressing F13/F14 on keyboard - should see tooltip

**Non-G HUB users:**
1. Check green "H" icon in system tray
2. Run `test_buttons.ahk` to identify which button is which
3. Check if mouse software is intercepting the button

**Still not working?**
- Restart computer after changing G HUB settings
- Enable "Persistent Profile" in G HUB
- Test keys directly in Notepad

### Monitor service offline

1. Install Python 3.8+: `python --version` in Command Prompt
2. Start service: Double-click `start_monitor_service.bat`
3. Verify: Visit `http://localhost:5001/health` in browser
4. Check if port 5001 is already in use

### Invalid address error

- Ensure address is fully visible (not truncated)
- Remove quotes, brackets, or extra spaces
- Try highlighting the address manually first
- Address must be 32-44 characters, base58 encoded

### Other issues

**Clipboard disrupted:** Script auto-restores clipboard. If issues persist, close clipboard managers temporarily.

**Works in browser but not Terminal/IDE:** Some apps require manual text selection first.

**Wrong/partial address:** Ensure address is separated by spaces/punctuation, not mixed with other text.

## Customization

Edit `solscan_hotkey.ahk` in any text editor:

- Line 21: `NOTIFICATION_DURATION` - Toast notification length (ms)
- Line 22: `SELECTION_DELAY` - Text selection timing (increase if capture fails)
- Line 376: Modify Solscan URL filters

## Uninstallation

1. Right-click tray icon → Exit
2. Remove from Startup folder if added
3. Delete folder
4. Optionally uninstall AutoHotkey

## Security & Privacy

- Runs locally - no network calls except opening Solscan
- Does not log or store data (except monitoring addresses)
- Clipboard fully restored after use
- Open source - inspect the code yourself

---

**License:** Free to use and modify. No warranty provided.

**Enjoy instant Solscan lookups!** Share with other Solana devs.