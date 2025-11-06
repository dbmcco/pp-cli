# Morning News Briefing System

Automated daily news briefing delivered to your Obsidian vault using Perplexity AI.

## Setup

### 1. Test the Script

First, test the script manually to ensure it works:

```bash
/Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh
```

This will generate a briefing and save it to `daily-briefings/YYYY-MM-DD-news-briefing.md` in your Obsidian vault.

### 2. Set Up Cron Job

To run the briefing automatically every morning at 7:00 AM:

```bash
# Open crontab editor
crontab -e

# Add this line (press 'i' to insert, then ESC and ':wq' to save):
0 7 * * * /Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh >> /tmp/morning-briefing.log 2>&1
```

**Cron Schedule Explanation:**
- `0 7 * * *` - Run at 7:00 AM every day
- Alternative times:
  - `0 6 * * *` - 6:00 AM
  - `0 8 * * *` - 8:00 AM
  - `30 7 * * *` - 7:30 AM

### 3. Verify Cron Setup

Check that your cron job is installed:

```bash
crontab -l
```

### 4. Monitor Execution

Check the log file to see if the job ran successfully:

```bash
cat /tmp/morning-briefing.log
```

## Customization

### Change the Prompt

Edit `/Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh` and modify the `PROMPT` variable to customize:
- Topics covered
- Level of detail
- Structure and format
- Word count

### Change the Save Location

Modify the `VAULT_PATH` variable to save briefings to a different location in your vault:

```bash
VAULT_PATH="path/to/your/location/${TODAY}-news-briefing.md"
```

### Add Custom Topics

Example custom prompt focusing on specific areas:

```bash
PROMPT="Generate a morning briefing for ${BRIEFING_DATE} focusing on:

## AI & Machine Learning
Latest developments in AI, LLMs, and ML research

## Developer Tools
New tools, frameworks, and developer productivity

## Startup & VC News
Funding rounds, acquisitions, and startup trends

## Open Source
Notable open source releases and community news"
```

## Troubleshooting

### Cron Job Not Running

1. **Check cron service is running:**
   ```bash
   sudo launchctl list | grep cron
   ```

2. **Give Full Disk Access to cron:**
   - System Settings → Privacy & Security → Full Disk Access
   - Add `/usr/sbin/cron`

3. **Check permissions:**
   ```bash
   ls -la /Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh
   ```
   Should show: `-rwxr-xr-x` (executable)

### Script Fails

1. **Test pp-cli directly:**
   ```bash
   pp --help
   ```

2. **Check config:**
   ```bash
   cat ~/.config/pp/config.json
   ```

3. **Run with verbose output:**
   ```bash
   bash -x /Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh
   ```

### No Briefing Generated

1. **Check API limits:** Verify your Perplexity API hasn't hit rate limits
2. **Check vault path:** Ensure `/Users/braydon/Obsidian/Bvault/daily-briefings/` exists
3. **Review logs:** `cat /tmp/morning-briefing.log`

## Advanced: Multiple Briefings

Create different briefings for different times of day:

```bash
# Morning briefing at 7 AM
0 7 * * * /Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh

# Midday update at 12 PM
0 12 * * * /Users/braydon/projects/experiments/pp/scripts/midday-update.sh

# Evening summary at 6 PM
0 18 * * * /Users/braydon/projects/experiments/pp/scripts/evening-summary.sh
```
