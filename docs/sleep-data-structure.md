# Garmin Sleep Data Structure

Raw JSON response from `Garmin.get_sleep_data(date)`. One file per night at `data/sleep/YYYY-MM-DD.json`.

## Top-Level Keys

| Key | Type | Description |
|---|---|---|
| `dailySleepDTO` | object | Sleep session summary |
| `sleepMovement` | array | Minute-by-minute movement/activity data |
| `remSleepData` | boolean | Whether REM data is available |
| `sleepLevels` | array | Sleep stage periods (deep/light/REM/awake) |
| `wellnessEpochRespirationDataDTOList` | array | Respiration readings (~2min intervals) |
| `wellnessEpochRespirationAveragesList` | array | Hourly respiration averages |
| `respirationVersion` | number | API version for respiration data |
| `sleepHeartRate` | array | Heart rate readings (~2min intervals) |
| `sleepStress` | array | Stress readings (~3min intervals) |
| `sleepBodyBattery` | array | Body battery readings (~3min intervals) |
| `skinTempDataExists` | boolean | Whether skin temp data exists |
| `bodyBatteryChange` | number | Net body battery change during sleep |
| `restingHeartRate` | number | Resting heart rate (bpm) |

## `dailySleepDTO` — Session Summary

| Field | Type | Example | Notes |
|---|---|---|---|
| `id` | number | `1771538820000` | Epoch ms, same as sleep start |
| `userProfilePK` | number | `3188846` | Garmin user ID |
| `calendarDate` | string | `"2026-02-20"` | Date the sleep is attributed to |
| `sleepTimeSeconds` | number | `25920` | Total sleep time (excludes awake) |
| `napTimeSeconds` | number | `0` | Nap duration |
| `sleepWindowConfirmed` | boolean | `true` | Whether Garmin confirmed the sleep window |
| `sleepWindowConfirmationType` | string | `"enhanced_confirmed"` | Confirmation method |
| `sleepStartTimestampGMT` | number | `1771538820000` | Epoch ms — sleep start (GMT) |
| `sleepEndTimestampGMT` | number | `1771564740000` | Epoch ms — sleep end (GMT) |
| `sleepStartTimestampLocal` | number | `1771538820000` | Epoch ms — sleep start (local TZ) |
| `sleepEndTimestampLocal` | number | `1771564740000` | Epoch ms — sleep end (local TZ) |
| `autoSleepStartTimestampGMT` | number | `1771537980000` | Auto-detected start (may differ from confirmed) |
| `autoSleepEndTimestampGMT` | number | `1771564560000` | Auto-detected end |
| `unmeasurableSleepSeconds` | number | `0` | Time that couldn't be classified |
| `deepSleepSeconds` | number | `4740` | Deep sleep duration |
| `lightSleepSeconds` | number | `20340` | Light sleep duration |
| `remSleepSeconds` | number | `840` | REM sleep duration |
| `awakeSleepSeconds` | number | `0` | Awake time during sleep window |
| `deviceRemCapable` | boolean | `true` | Whether device supports REM detection |
| `retro` | boolean | `false` | Retroactively computed |
| `averageRespirationValue` | number | `12.0` | Avg breaths/min |
| `lowestRespirationValue` | number | `10.0` | Min breaths/min |
| `highestRespirationValue` | number | `15.0` | Max breaths/min |

### Deriving sleep duration

```
total_sleep = deepSleepSeconds + lightSleepSeconds + remSleepSeconds
total_in_bed = sleepEndTimestampGMT - sleepStartTimestampGMT  (in ms)
sleep_efficiency = total_sleep / (total_in_bed / 1000)
```

## `sleepMovement` — Minute-by-Minute Activity

Array of ~480+ entries (one per minute of the sleep window).

```json
{
  "startGMT": "2026-02-19T21:07:00.0",
  "endGMT": "2026-02-19T21:08:00.0",
  "activityLevel": 5.69
}
```

| Field | Type | Notes |
|---|---|---|
| `startGMT` | string | ISO datetime (GMT) |
| `endGMT` | string | ISO datetime (GMT) |
| `activityLevel` | float | Movement intensity. `0.0` = still, higher = more movement. Observed range: `0.0`–`6.6` |

## `sleepLevels` — Sleep Stages

Array of variable-length periods representing classified sleep stages.

```json
{
  "startGMT": "2026-02-19T22:06:00.0",
  "endGMT": "2026-02-19T22:22:00.0",
  "activityLevel": 1.0
}
```

| `activityLevel` | Stage |
|---|---|
| `0.0` | Deep sleep |
| `1.0` | Light sleep |
| `2.0` | REM sleep |

Note: Awake periods may appear as gaps or as a separate level depending on the device/firmware.

## `sleepHeartRate` — Heart Rate During Sleep

Array of ~220 entries (~2 min intervals). Timestamps are epoch milliseconds.

```json
{
  "value": 65,
  "startGMT": 1771538760000
}
```

| Field | Type | Notes |
|---|---|---|
| `value` | number | Heart rate in bpm |
| `startGMT` | number | Epoch ms (GMT) |

## `sleepStress` — Stress During Sleep

Array of ~140 entries (~3 min intervals).

```json
{
  "value": 25,
  "startGMT": 1771538760000
}
```

| Field | Type | Notes |
|---|---|---|
| `value` | number | Stress score. Observed range: `7`–`37`. Lower = more relaxed. |
| `startGMT` | number | Epoch ms (GMT) |

## `sleepBodyBattery` — Body Battery During Sleep

Array of ~140 entries (~3 min intervals). Should monotonically increase during good sleep.

```json
{
  "value": 24,
  "startGMT": 1771538760000
}
```

| Field | Type | Notes |
|---|---|---|
| `value` | number | Body battery level (0–100) |
| `startGMT` | number | Epoch ms (GMT) |

## `wellnessEpochRespirationDataDTOList` — Respiration

Array of ~220 entries (~2 min intervals).

```json
{
  "startTimeGMT": 1771538820000,
  "respirationValue": 13.0
}
```

| Field | Type | Notes |
|---|---|---|
| `startTimeGMT` | number | Epoch ms (GMT) |
| `respirationValue` | float | Breaths per minute |

## `wellnessEpochRespirationAveragesList` — Hourly Respiration

Array of ~8 entries (one per hour of sleep).

```json
{
  "epochEndTimestampGmt": 1771542000000,
  "respirationAverageValue": 12.66,
  "respirationHighValue": 13.0,
  "respirationLowValue": 12.0
}
```

Note: The last entry may have `respirationAverageValue: -2.0` with null high/low — this appears to be a sentinel for incomplete epochs.

## Timestamp Formats

The API uses two timestamp formats inconsistently:
- **Epoch milliseconds** (number): `1771538820000` — used in `sleepHeartRate`, `sleepStress`, `sleepBodyBattery`, respiration arrays
- **ISO datetime strings** (string): `"2026-02-19T21:07:00.0"` — used in `sleepMovement`, `sleepLevels`

Both are GMT/UTC.

### Converting epoch ms to datetime (Python)

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(1771538820000 / 1000, tz=timezone.utc)
# 2026-02-19 21:07:00+00:00
```

## Nullable / Missing Fields

- `sleepQualityTypePK`: observed as `null`
- `sleepResultTypePK`: observed as `null`
- Last respiration average entry may have null high/low values
- Some nights may be missing sections entirely if the device was off or not worn
