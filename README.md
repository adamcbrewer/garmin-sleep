# Garmin Sleep Extractor

Dockerized tool that pulls your sleep data from Garmin Connect and dumps it as raw JSON files for analysis.

## What it does

- Authenticates with Garmin Connect
- Fetches the last 180 days of sleep data (configurable)
- Saves one JSON file per night to `data/sleep/`
- Skips dates already fetched on re-runs
- Caches auth tokens so you don't re-login every time

## Setup

```bash
cp .env.example .env
```

Edit `.env` with your Garmin credentials:

```
GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=your_password
```

## Run

```bash
docker compose up --build
```

Sleep data lands in `data/sleep/` as one file per night:

```
data/sleep/
├── 2025-08-24.json
├── 2025-08-25.json
├── ...
└── 2026-02-21.json
```

Re-running skips dates already fetched.

## Configuration

All optional, set in `.env`:

| Variable | Default | Description |
|---|---|---|
| `BACKFILL_DAYS` | `180` | Number of days to fetch |
| `REQUEST_DELAY` | `1.0` | Seconds between API requests |

## MFA / Two-Factor Auth

If your Garmin account has MFA enabled, the first login may fail inside Docker since it can't prompt interactively. To work around this:

1. Run the script locally first to generate tokens:
   ```bash
   pip install garminconnect
   python app/main.py
   ```
2. Complete the MFA prompt
3. Tokens are saved to `data/.garminconnect/` and will be reused by Docker on subsequent runs

## Exploring the data

Each JSON file is the raw Garmin API response. Quick ways to poke at it:

```bash
# Pretty-print a single night
cat data/sleep/2026-02-21.json | jq .

# Extract total sleep seconds for all nights
jq '.dailySleepDTO.sleepTimeSeconds' data/sleep/*.json

# Load into pandas
python -c "
import json, glob, pandas as pd
files = glob.glob('data/sleep/*.json')
rows = [json.load(open(f))['dailySleepDTO'] for f in sorted(files)]
df = pd.DataFrame(rows)
print(df[['calendarDate','sleepTimeSeconds','deepSleepSeconds','lightSleepSeconds','remSleepSeconds']].to_string())
"
```
