# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your Queries

Edit `dorks.txt` and add your Google dork queries (one per line):

```
site:github.com secret
inurl:admin login
filetype:sql backup
```

### 3. Run the Tool

```bash
# Basic usage (fastest way to start)
python google_dork_cli.py -f dorks.txt

# Target a specific domain
python google_dork_cli.py -t example.com -f dorks.txt

# See results in console
python google_dork_cli.py -f dorks.txt --console

# Increase delay for stealth
python google_dork_cli.py -f dorks.txt -d 5

# Use advanced version with caching
python advanced.py -f dorks.txt --cache --console
```

## Common Scenarios

### Scenario 1: Quick Testing
```bash
python google_dork_cli.py -f dorks.txt --console
```
- Fast feedback
- No file saving
- Good for testing queries

### Scenario 2: Target Specific Domain
```bash
python google_dork_cli.py -t example.com -f dorks.txt --console
```
- Search only on target domain
- Uses `site:example.com` prefix
- Good for focused penetration testing

### Scenario 3: Large Batch with Stealth
```bash
python google_dork_cli.py -f dorks.txt --delay 10 --output results
```
- Longer delays between requests
- Saves to CSV and JSON
- Less likely to trigger rate limiting

### Scenario 4: Using Proxies (Advanced)
```bash
python advanced.py -t example.com -f dorks.txt --proxies proxies.txt --delay 3 --cache
```
- Rotates through proxies
- Caches results to avoid duplicate searches
- Better for distributed searches

## Understanding Output Files

Files are created with timestamps: `results_20240207_143022.csv`

### CSV Format
Perfect for importing to Excel/Sheets:
```
Query,Title,URL,Snippet
site:github.com password,GitHub - My Secret...,https://github.com/...,Found secret in...
```

### JSON Format
Perfect for automation:
```json
{
  "site:github.com password": [
    {
      "title": "GitHub - My Secret",
      "url": "https://github.com/...",
      "snippet": "Found secret in...",
      "domain": "github.com"
    }
  ]
}
```

## Troubleshooting

### Issue: Slow Results / Timeouts
```bash
# Reduce timeout, increase delay
python google_dork_cli.py -f dorks.txt -d 5
```

### Issue: Getting CAPTCHA
```bash
# Wait 30 minutes, or use proxy version
python advanced.py -f dorks.txt --proxies proxies.txt
```

### Issue: Permission Error on proxies.txt
```bash
# Make sure proxies.txt has valid proxy addresses
# Or skip proxies for basic version
python google_dork_cli.py -f dorks.txt
```

## Best Practices Checklist

- ✅ Start with small batches (5 queries)
- ✅ Use 2-3 second delay minimum
- ✅ Check legal requirements first
- ✅ Space out large searches
- ✅ Monitor for errors/CAPTCHAs
- ✅ Save results regularly
- ✅ Respect site ToS

## Next Steps

1. **Test it**: Run with sample dorks first
2. **Add queries**: Update dorks.txt with your queries
3. **Run in bulk**: Use --delay 5 for larger batches
4. **Automate**: Schedule with cron (Linux) or Task Scheduler (Windows)

## Advanced Tips (Target Specific Domain)
```bash
# Search only on target domain
python advanced.py -t target-company.com -f dorks.txt --proxies proxies.txt --delay 2
```

### Use Case: Information Gathering
```bash
# Stealthy, cached, comprehensive
python advanced.py -t example.com
# Faster pace with proxy rotation
python advanced.py -f dorks.txt --proxies proxies.txt --delay 2
```

### Use Case: Information Gathering
```bash
# Stealthy, cached, comprehensive
python advanced.py -f dorks.txt --cache --delay 8 --console
```

## Monitoring Execution

While running, watch for:
- **HTTP 429**: Rate limited (increase --delay)
- **HTTP 403**: Possibly blocked (try proxies or wait)
- **Content Detection**: Different page format (may indicate bot detection)
- **Empty Results**: Query may be blocked or invalid

## Performance Tuning

| Setting | Value | Effect |
|---------|-------|--------|
| --delay | 1 | Fast, high rate limit risk |
| --delay | 3 | Balanced (recommended) |
| --delay | 5+ | Slow, low rate limit risk |
| --cache | enabled | Faster for repeated queries |
| --proxies | enabled | Distributed requests |

---

**Remember**: Always use ethically and legally! 🚀
