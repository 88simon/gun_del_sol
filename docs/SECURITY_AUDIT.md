# OPSEC Security Fixes Required

## Status: CRITICAL - Immediate Action Required

This document outlines all code changes needed to secure sensitive trading data from being leaked through logs, console output, and unsecured APIs.

---

## Summary of Issues

| Severity | Issue | Count | Status |
|----------|-------|-------|--------|
| **CRITICAL** | Wallet addresses in print() statements | 50+ | ❌ NOT FIXED |
| **CRITICAL** | Token addresses in print() statements | 30+ | ❌ NOT FIXED |
| **CRITICAL** | Unauthenticated API endpoints | 10 | ❌ NOT FIXED |
| **HIGH** | Full stack traces with file paths | 5 | ❌ NOT FIXED |
| **HIGH** | Browser console.log with sensitive data | 18 | ❌ NOT FIXED |
| **MEDIUM** | Webhook logs with wallet addresses | 3 | ❌ NOT FIXED |
| **MEDIUM** | Temp files with wallet data | 2 | ❌ NOT FIXED |

---

## Quick Wins (Immediate Fixes)

### 1. DISABLE DEBUG LOGGING (5 minutes)

Add this at the top of `monitor_service.py` and `helius_api.py`:

```python
# OPSEC: Set to False in production to prevent sensitive data leakage
DEBUG_LOGGING = False

def safe_log(message):
    """Only log if DEBUG_LOGGING is True"""
    if DEBUG_LOGGING:
        print(message)
```

Then replace all `print()` statements that contain sensitive data with `safe_log()`.

### 2. REMOVE BROWSER CONSOLE LOGS (10 minutes)

In `token_history.html` lines 342-366, wrap all console.log in a conditional:

```javascript
const DEBUG = false;  // Set to false in production

if (DEBUG) {
    console.log('[TokenHistory] Data received:', data);
}
```

Or simply comment them all out:
```javascript
// console.log('[TokenHistory] Data received:', data);
```

### 3. SANITIZE ERROR RESPONSES (15 minutes)

In `monitor_service.py`, change all error handlers from:
```python
except Exception as e:
    return jsonify({"error": str(e)}), 500
```

To:
```python
except Exception as e:
    log_error(f"Operation failed: {type(e).__name__}")  # Log internally
    return jsonify({"error": "An error occurred"}), 500  # Generic response
```

---

## Critical Fixes (Priority Order)

### FIX 1: Sanitize All Logging in monitor_service.py

**Lines to change:**

| Line | Current | Fix |
|------|---------|-----|
| 172 | `print(f"✓ Registered new address: {address}")` | `log_address_registered(address)` |
| 212 | `print(f"✓ Removed address: {address}")` | `log_address_removed(address)` |
| 244 | `print(f"✓ Updated note for address: {address}")` | `log_success("Address note updated")` |
| 289 | `print(f"✓ Imported {added} addresses...")` | `log_success(f"Imported {added} addresses")` |
| 326 | `print(f"[Job {job_id}] Starting analysis for {token_address}")` | `log_analysis_start(job_id)` |
| 388 | `print(f"[Job {job_id}] Saved to database (ID: {token_id})")` | `log_success(f"Job {job_id} saved to database")` |
| 411 | `print(f"[Job {job_id}] Analysis complete - found {result['total_unique_buyers']} early bidders")` | `log_analysis_complete(job_id, result['total_unique_buyers'])` |
| 412 | `print(f"[Job {job_id}] Axiom export saved: {axiom_filepath}")` | `log_success(f"Job {job_id} export saved")` |
| 417-418 | Full traceback logging | Remove or wrap in `if DEBUG_LOGGING:` |
| 473 | `print(f"✓ Queued token analysis: {token_address} (Job ID: {job_id})")` | `log_success(f"Analysis queued (Job: {job_id})")` |
| 654 | `print(f"[Webhook] Created webhook {webhook_id} for token ID {token_id}")` | `log_success(f"Webhook {webhook_id} created")` |
| 785 | `print(f"[Webhook] Saved activity for wallet {wallet_address[:8]}...")` | `log_success("Webhook activity saved")` |

### FIX 2: Sanitize helius_api.py Logging

**Critical lines exposing token addresses:**

| Line | Current | Fix |
|------|---------|-----|
| 77 | `print(f"Error fetching token metadata (standard): {str(e)}")` | `log_error("Token metadata fetch failed (trying DAS)")` |
| 107 | `print(f"Error fetching token metadata (DAS): {str(das_error)}")` | `log_error("DAS API metadata fetch failed")` |
| 316 | `print(f"[Helius] Analyzing token: {mint_address}")` | `log_info("Token analysis started")` |
| 322 | `print(f"[Helius] Token info: {token_name}")` | `log_info("Token metadata retrieved")` |
| 427 | `print(f"[Helius] Found {len(early_bidders)} early bidders...")` | `log_success(f"Found {len(early_bidders)} early buyers")` |

**Debug logging (lines 454-518):**
Wrap entire debug section in:
```python
DEBUG_TRANSACTIONS = False  # Set to True only when debugging locally

if DEBUG_TRANSACTIONS and debug_first:
    # ... all debug print statements ...
```

### FIX 3: Add API Authentication

Add to `monitor_service.py` after imports:

```python
from functools import wraps

# Generate a random API key on first run (save to config.json)
API_KEY = os.environ.get('API_KEY') or 'CHANGE_ME_IN_PRODUCTION'

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or provided_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function
```

Then protect sensitive endpoints:
```python
@app.route('/api/tokens/history', methods=['GET'])
@require_api_key  # ADD THIS
def get_token_history():
    # ... existing code ...
```

Protect these endpoints:
- `/addresses`
- `/address/<address>`
- `/analysis`
- `/analysis/<job_id>`
- `/api/tokens/history`
- `/api/tokens/<token_id>`

### FIX 4: Remove Browser Console Logs

**token_history.html:**
```javascript
// Lines 342-366: Comment out or wrap in DEBUG flag
const DEBUG = false;

// Replace all console.log with:
if (DEBUG) console.log('[TokenHistory] ...', data);
```

**defined-fi-autosearch.user.js:**
```javascript
// Lines 16, 21, 27, 38, 49, 70, 76, 89, 93, 104, 108, 122:
// Comment out all console.log statements or wrap in DEBUG flag
const DEBUG = false;
if (DEBUG) console.log('[Defined.fi Auto-Search] ...', address);
```

### FIX 5: Replace AHK Temp Files

**gun_del_sol.ahk lines 1225-1249 and 1335-1362:**

Instead of:
```ahk
tempFile := A_Temp . "\solscan_register.json"
FileAppend jsonData, tempFile
RunWait curl ... @tempFile, , Hide
FileDelete tempFile
```

Use:
```ahk
; Pass JSON directly via stdin
RunWait curl -X POST http://localhost:5001/register -H "Content-Type: application/json" --data-raw "`" jsonData `"`, , Hide
```

This eliminates temp files entirely.

---

## Configuration Changes

### Enable/Disable Logging

Create `monitor/config.json`:
```json
{
    "helius_api_key": "your-key-here",
    "api_key": "generate-random-key-here",
    "debug_logging": false,
    "debug_transactions": false
}
```

### .gitignore Check ✓

Already protected:
- ✓ `monitor/axiom_exports/`
- ✓ `monitor/analysis_results/`
- ✓ `monitor/*.db`
- ✓ `monitor/config.json`
- ✓ `monitor/monitored_addresses.json`

---

## Testing After Fixes

1. **Restart service** and run token analysis
2. **Check terminal output** - should see NO wallet/token addresses
3. **Check browser console** - should see NO sensitive data
4. **Try API without auth** - should get 401 Unauthorized
5. **Check Windows temp folder** - should have NO JSON files

---

## Enforcement Checklist

Before committing ANY code:
- [ ] Search for `print(.*address)` - should find ZERO matches
- [ ] Search for `print(.*token)` - should find ZERO matches
- [ ] Search for `console.log.*address` - should find ZERO matches
- [ ] All sensitive endpoints have `@require_api_key` decorator
- [ ] No temp files created with sensitive data
- [ ] `DEBUG_LOGGING = False` in production code
- [ ] All error messages are generic

---

## Emergency Procedure

If you've already leaked data in logs:

1. **Delete log files** immediately
2. **Clear browser console** (close/reopen browser)
3. **Rotate API keys** if exposed
4. **Check Windows temp folder** and delete any JSON files
5. **Review screen recording/sharing** history
6. **Consider wallet addresses compromised** - adjust strategy accordingly

---

## Long-term Solutions

### Production Mode Flag

Add to `monitor_service.py`:
```python
PRODUCTION_MODE = os.environ.get('PRODUCTION', 'true').lower() == 'true'

if PRODUCTION_MODE:
    # Disable all logging of sensitive data
    # Require API authentication
    # Sanitize all error messages
```

### Structured Logging

Replace `print()` with Python's `logging` module:
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if PRODUCTION_MODE else logging.DEBUG)
```

### Database Encryption

Consider encrypting the SQLite database using `sqlcipher`:
```bash
pip install pysqlcipher3
```

---

## Responsible Disclosure

**DO NOT**:
- Share logs publicly
- Post screenshots with addresses visible
- Stream/record with terminal open
- Send unencrypted exports via email

**DO**:
- Keep terminal minimized when screen sharing
- Use secure encrypted channels for backups
- Regularly audit logs for leaks
- Clear browser console before demos

---

## Status: NOT PRODUCTION READY

**Current State**: ❌ UNSAFE - Actively leaking sensitive data through logs and console

**Required Before Production**:
1. Implement all FIX 1-5 changes above
2. Test thoroughly
3. Enable API authentication
4. Set `DEBUG_LOGGING = False`
5. Review all print/console.log statements

**Estimated Time to Secure**: 2-3 hours of focused work

---

**Last Updated**: 2025-11-05
**Next Review**: After implementing fixes