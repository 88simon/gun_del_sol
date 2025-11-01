# Solscan Mouse Hotkey

Instantly open Solscan for any Solana address by hovering and clicking your side mouse button.

## Features

- Click side mouse button (XButton1) over any Solana address to open Solscan
- Smart text detection with multiple fallback strategies
- Validates Solana base58 addresses (32-44 characters)
- Safe clipboard handling - restores your clipboard after use
- Visual feedback with tooltip notifications
- Lightweight and non-intrusive

## Requirements

- **Windows** (Vista or later)
- **AutoHotkey v1.1+** - [Download here](https://www.autohotkey.com/)
- A mouse with side buttons (XButton1/XButton2)

## Installation

### Step 1: Install AutoHotkey

1. Download AutoHotkey from [https://www.autohotkey.com/](https://www.autohotkey.com/)
2. Run the installer and follow the prompts
3. Choose "Install" (default options are fine)

### Step 2: Run the Script

**Option A: Manual Start**
1. Double-click `solscan_hotkey.ahk`
2. You'll see a green "H" icon in your system tray (bottom-right)
3. The script is now active!

**Option B: Auto-start on Windows Startup**
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create a shortcut to `solscan_hotkey.ahk` in this folder
4. The script will now run automatically when you log in

**Option C: Use the Launcher (Recommended)**
1. Double-click `start_solscan_hotkey.bat`
2. This will launch the script and minimize to tray

## Usage

### Basic Usage

1. Hover your mouse over any Solana address (in browser, Discord, code editor, etc.)
2. Click your **side mouse button** (typically the "Back" button - XButton1)
3. The address will be captured and validated
4. If valid, Solscan opens automatically in your default browser
5. A tooltip shows success or error message

### Examples of Valid Addresses

```
TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
So11111111111111111111111111111111111111112
EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

### Mouse Button Configuration

The script is set to use **XButton1** (usually "Back" button).

**To change to XButton2 ("Forward" button):**
1. Open `solscan_hotkey.ahk` in Notepad
2. Find line ~30: `XButton1::`
3. Change to: `XButton2::`
4. Save and reload the script (right-click tray icon → Reload)

**To use both buttons:**
Uncomment lines 140-142 in the script.

## Text Capture Strategies

The script uses multiple strategies to capture text:

1. **Pre-selected text**: If you've already highlighted text, it uses that
2. **Word selection**: Double-clicks under cursor to select the word
3. **Line selection**: Selects entire line and extracts address pattern

This ensures compatibility across browsers, terminals, IDEs, and Discord.

## Validation Rules

An address is considered valid if:
- Length is between 32-44 characters
- Contains only base58 characters: `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`
- Excludes confusing characters: `0` (zero), `O` (capital o), `I` (capital i), `l` (lowercase L)

## Controls

- **XButton1** - Trigger Solscan lookup
- **Ctrl+Alt+Q** - Exit the script (with confirmation)
- **Tray icon right-click** - Reload or Exit script

## Troubleshooting

### "Nothing happens when I click the side button"

1. Verify AutoHotkey is installed: Check for green "H" in system tray
2. Test your mouse button:
   - Open Notepad
   - Run `solscan_hotkey.ahk`
   - Click side button - you should see a tooltip
3. Check if your mouse software is intercepting the button
4. Try the other side button (change XButton1 to XButton2)

### "Says 'Not a valid Solana address'"

1. Ensure the address is fully visible (not truncated with ...)
2. Remove any quotes, brackets, or extra spaces
3. Try highlighting the address manually before clicking
4. Check the tooltip to see what text was captured

### "Clipboard is disrupted"

The script saves and restores your clipboard automatically. If issues persist:
- Increase `SELECTION_DELAY` in the script (line 16)
- Close clipboard managers temporarily

### "Works in browser but not in Terminal/IDE"

Some apps have different selection behavior:
- **Terminal**: Text must be selectable (not just hoverable)
- **VS Code**: Works best when address is on its own line
- **Discord**: Highlight the address first, then click side button

### "Opens wrong address or partial address"

Ensure the address is:
- Not mixed with other text on the same word
- Separated by spaces or punctuation
- Not split across multiple lines

## Customization

### Change Notification Duration

Edit line 15:
```ahk
global NOTIFICATION_DURATION := 2000  ; milliseconds (2 seconds)
```

### Change Selection Timing

Edit line 16:
```ahk
global SELECTION_DELAY := 100  ; increase if selection fails
```

### Use Different URL

To use mainnet-beta or custom RPC:
```ahk
url := "https://solscan.io/account/" . address . "?cluster=mainnet-beta"
```

## Uninstallation

1. Right-click the green "H" tray icon → Exit
2. Remove from Startup folder if you added it there
3. Delete `solscan_hotkey.ahk` and this folder
4. Optionally uninstall AutoHotkey from Control Panel

## Security & Privacy

- Runs locally - no network calls except opening Solscan in browser
- Does not log or store any data
- Only accesses clipboard temporarily (fully restored after use)
- Open source - inspect the code yourself

## Support

- **Script issues**: Check the AHK tray icon for error messages
- **AutoHotkey help**: [https://www.autohotkey.com/docs/](https://www.autohotkey.com/docs/)
- **Modify the script**: Open in any text editor

## License

Free to use and modify. No warranty provided.

---

**Enjoy instant Solscan lookups!** If you find this useful, share it with other Solana devs.
