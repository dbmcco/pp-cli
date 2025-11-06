# Morning News Briefing System

Automated daily news briefing delivered to your Obsidian vault using Perplexity AI.

## Features

- **Different briefing each day:** Custom focus areas for each day of the week
- **7-day weather forecast:** Boston, MA weather included in every briefing
- **Multi-query approach:** Separate queries per section for balanced coverage
- **Markdown prompts:** Easy to customize and maintain
- **Research mode option:** Use deep reasoning for single-query mode

## Daily Themes

- **Monday:** Week Ahead & Technology Focus
- **Tuesday:** Business & Markets Deep Dive
- **Wednesday:** Innovation & Deep Dives
- **Thursday:** Science & Research Focus
- **Friday:** Week in Review & Weekend Preview
- **Saturday:** Weekend Deep Dive & Analysis (longer format)
- **Sunday:** Week Ahead Prep & Insights

## Two Approaches

### Multi-Query (Recommended)
Runs separate queries for each section, giving balanced coverage. Uses `monday-queries.md` format.

**Pros:** Better balance, no section dominates, consistent depth per topic
**Cons:** Takes longer (multiple API calls), uses more API quota

### Single-Query
Runs one comprehensive query. Uses `monday.md` format with research mode.

**Pros:** Faster, single API call, deeper reasoning
**Cons:** Can be unbalanced, one topic may dominate

## Setup

### 1. Test the Script

**Multi-query approach (recommended):**
```bash
/Users/braydon/projects/experiments/pp/scripts/multi-query-briefing.py
```

**Single-query approach:**
```bash
/Users/braydon/projects/experiments/pp/scripts/morning-briefing.sh
```

### 2. Set Up Cron Job

To run the briefing automatically every morning at 7:00 AM:

```bash
# Open crontab editor
crontab -e

# Add this line (multi-query):
0 7 * * * /Users/braydon/projects/experiments/pp/scripts/multi-query-briefing.py >> /tmp/morning-briefing.log 2>&1

# OR single-query:
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

### Edit Daily Prompts

Each day's briefing is controlled by a markdown file in `scripts/prompts/`:

```
scripts/prompts/
├── monday.md      # Week ahead & tech focus
├── tuesday.md     # Business & markets
├── wednesday.md   # Innovation deep dives
├── thursday.md    # Science & research
├── friday.md      # Week in review
├── saturday.md    # Deep analysis
└── sunday.md      # Week ahead prep
```

**To customize a day's briefing:**
1. Open the relevant `.md` file
2. Edit the structure and topics
3. Adjust word count targets
4. Add or remove sections

**Example customization** (edit `monday.md`):
```markdown
## Weather Forecast
7-day forecast for Boston, MA

## Crypto & Web3
Latest developments in blockchain and cryptocurrency

## Your Custom Section
Whatever topics you want to track
```

### Change Weather Location

Edit each prompt file and change:
```markdown
7-day forecast for Boston, MA
```
To your location:
```markdown
7-day forecast for San Francisco, CA
```

### Change Save Location

Modify the `VAULT_PATH` variable in `morning-briefing.sh`:

```bash
VAULT_PATH="your-folder/${TODAY}-briefing.md"
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
