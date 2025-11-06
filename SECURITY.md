# Security and Data Privacy Notice

## ⚠️ SENSITIVE DATA - DO NOT SHARE ⚠️

This directory contains **highly sensitive trading data** that should NEVER be committed to version control or shared publicly.

### Protected Files and Directories

The following contain your private trading research and strategies:

#### 1. `axiom_exports/` directory
- **Contains**: Wallet addresses of early buyers you discovered
- **Risk**: Reveals your exact trading strategy and targets
- **Protection**: Added to `.gitignore`

#### 2. `analysis_results/` directory
- **Contains**: Full token analysis results with transaction data
- **Risk**: Exposes your research methodology and findings
- **Protection**: Added to `.gitignore`

#### 3. `solscan_monitor.db` (SQLite database)
- **Contains**:
  - All analyzed tokens
  - Early buyer wallet addresses
  - Transaction timestamps and amounts
  - Your complete trading history
- **Risk**: Complete exposure of your trading activity
- **Protection**: Added to `.gitignore` (all `.db` files)

#### 4. `monitored_addresses.json`
- **Contains**: Wallet addresses you're actively monitoring
- **Risk**: Reveals addresses of interest
- **Protection**: Added to `.gitignore`

#### 5. `config.json` (Gun Del Sol settings)
- **Contains**: Your Helius API key
- **Risk**: API key theft and unauthorized usage
- **Protection**: Added to `.gitignore`

---

## Best Practices

### ✅ DO:
- Keep these files on your local machine only
- Back up to encrypted external drives
- Use strong passwords for any backups
- Regularly review `.gitignore` to ensure protection

### ❌ DON'T:
- Commit these files to Git
- Share analysis results publicly
- Upload to cloud storage (Dropbox, Google Drive, etc.)
- Send unencrypted via email
- Post wallet addresses on social media or forums

---

## What's Safe to Share

You CAN safely share:
- The Python source code (`.py` files)
- The AutoHotkey script (`.ahk` file)
- HTML templates (without data)
- Documentation and README files
- Configuration templates (without real API keys)

---

## If Data is Accidentally Committed

If you accidentally commit sensitive data to Git:

1. **DO NOT** just delete the file - it remains in Git history
2. Use `git filter-branch` or BFG Repo-Cleaner to remove it from history
3. Immediately revoke and regenerate any exposed API keys
4. Consider the wallet addresses potentially compromised

---

## Questions?

Remember: **When in doubt, don't share it.**

Your trading edge depends on keeping this data private.