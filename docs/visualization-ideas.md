# Sleep Data Visualization Ideas

Research into creative ways to analyze and display Garmin sleep data. Our dataset covers ~180 nights with unusually rich per-night data: sleep stages, minute-by-minute movement, HR (~2min intervals), stress (~3min intervals), body battery (~3min intervals), and respiration.

---

## Data Art / Poster-Worthy

### Sleep Barcode

Each night compressed to a single horizontal gradient strip where color = sleep stage. Left = bedtime, right = wake time. Stack 180 strips vertically — your entire 6 months in one image.

- Maximum data density. A single poster-sized image encodes an entire half-year of sleep architecture
- Patterns emerge at the macro level: seasonal variations, lifestyle changes, consistency shifts
- Similar to the "warming stripes" climate visualization — pure color field, no axes
- **Data needed:** `sleepLevels` for color mapping, timestamps for positioning

### Ridgeline Plot (Joy Division)

Stack nightly HR or respiration curves with slight vertical offset. ~220 data points per night × 180 nights = a rich, wave-like topographic image.

- Respiration is inherently wave-like — the ridgeline format (popularized by the Joy Division album cover) creates an almost musical visualization
- Can also be done with sleep stage distributions or movement intensity
- Beautiful at poster scale
- **Data needed:** `sleepHeartRate`, `wellnessEpochRespirationDataDTOList`, or `sleepMovement`

### Movement Topography

Render `sleepMovement` data as a 3D terrain or topographic contour map. X = time within night, Y = date, Z (height/color) = activity level.

- ~480 data points per night × 180 nights = 86,400 points — enough for rich terrain
- Restless periods become "mountain ranges"; still sleep becomes "valleys"
- Contour lines at specific activity thresholds reveal patterns invisible in line charts
- **Data needed:** `sleepMovement` array (activity levels 0.0–6.6)

### Sleep Garden (Flower Glyphs)

Each night = one flower. Petals = sleep stages (4 types: deep, light, REM, awake). Petal length = duration. Petal angle = time of occurrence. Color saturation = quality metric. Arrange chronologically in a garden layout.

- Inspired by [Or Misgav's "Garden of Sleep"](https://nightingaledvs.com/a-garden-of-sleep/) and Shirley Wu's "Film Flowers"
- Each night becomes a unique organic shape; a whole month becomes a garden you can scan for "healthy" vs "wilted" flowers
- **Data needed:** `sleepLevels` for petals, summary metrics for color/saturation

### Tree Rings

Each night = one ring in a tree cross-section. Ring color varies by sleep stage around the 24-hour circle. Ring thickness modulated by total sleep or body battery recovery. Over months, the tree grows outward.

- Inspired by [Leonard Pierce's newborn visualizations](https://nightingaledvs.com/flower-visualizations-uncertainty-of-new-parenthood/)
- The cumulative shape becomes a unique "fingerprint" of your sleep life
- **Data needed:** Sleep stages for color, `sleepTimeSeconds` or `bodyBatteryChange` for ring thickness

### Mondrian Sleep Grid

Divide each night into a grid where columns = 20-minute intervals, rows = hours. Color cells by sleep stage or movement level. Each night becomes a Mondrian-esque composition.

- Inspired by [Or Misgav's first-trimester tracking](https://nightingaledvs.com/first-trimester-data-tracking/)
- Deep = navy, light = sky blue, REM = purple, awake = gold
- **Data needed:** `sleepMovement` or `sleepLevels` mapped to grid cells

### Gradient Night Strip

A more refined version of the sleep barcode — each night gets a smooth gradient rather than discrete blocks. Color transitions between stages are blended. The result is softer and more organic.

- Works well as a phone wallpaper or narrow vertical print
- **Data needed:** `sleepLevels` with interpolated color transitions

---

## Analytical / Pattern-Finding

### 24-Hour Radial Clock

Map each night's sleep onto a polar chart. Angle = time of day (midnight at top). Sleep stages as concentric colored arcs.

- Humans intuit circular time better than linear
- Instantly reveals chronotype and bedtime/wake-time drift over weeks
- Stack multiple nights with low opacity for a "sleep fingerprint"
- **Data needed:** `sleepStartTimestampLocal` / `sleepEndTimestampLocal` for angles, `sleepLevels` for arcs

### Horizon Chart (Raster Plot)

One horizontal strip per night, stacked vertically. X-axis = time (9pm–9am). Color = sleep stage. Over months, a dense "carpet" where patterns pop.

- The classic baby-sleep Reddit visualization format — consistently goes viral on r/dataisbeautiful
- Consistent bedtimes form vertical edges; irregular sleep creates jagged silhouettes
- **Data needed:** `sleepLevels` for stage segments; each night = one row

### Weekday Fingerprint Overlay

Overlay all Mondays on one radial clock, all Tuesdays on another, etc. (with low opacity). Each day-of-week gets its own chart.

- Reveals social jet lag and weekly rhythms
- Friday nights probably look very different from Tuesday nights
- **Data needed:** Filter by `calendarDate` day-of-week, overlay radial sleep data

### Enhanced Hypnogram with Physiological Overlay

The classic clinical hypnogram (step chart of deep/light/REM/awake) with layered transparent area charts of HR, stress, respiration, and body battery underneath.

- Reveals correlations invisible in summary stats: HR dipping during deep sleep, stress spikes during awakenings, body battery charging during quality sleep
- Exploits all data channels simultaneously
- **Data needed:** `sleepLevels` for step chart, `sleepHeartRate`, `sleepStress`, `sleepBodyBattery`, respiration arrays

### Sleep Stage Sankey / Alluvial Flow

Each transition between stages (deep→light, light→REM, REM→awake) shown as a flow diagram. Width = frequency or time spent.

- Sleep architecture is about cycles and transitions, not just totals
- Makes the ~90-minute ultradian cycling pattern visually tangible
- **Data needed:** Derived transitions from sequential `sleepLevels` entries

### Sleep Cycle Wave

Treat sleep stages as a continuous wave instead of a stepped hypnogram. Interpolate between stages using a smooth curve, color the area by stage. Each 90-min cycle becomes a visible "wave."

- More aesthetically pleasing than step charts, emphasizes rhythm
- Overlay multiple nights = beautiful interference pattern
- **Data needed:** `sleepLevels` with spline interpolation

### Heart Rate Valley Profile

Plot HR over the night as a filled area chart, inverted (lower HR = higher peak). The deepest "valley" = lowest resting HR.

- The valley shape tells a story: smooth U-shape = good recovery; jagged = disrupted sleep
- One of the strongest recovery signals
- **Data needed:** `sleepHeartRate` array (~220 points/night), `restingHeartRate` as reference

### Body Battery Charge Curve

Plot body battery as a "charging" visualization. Show the rate of charge (derivative) as color intensity. Flat = poor recovery; steep = excellent.

- The curve *shape* is more informative than the summary `bodyBatteryChange` number
- Cross-reference with stress to explain plateaus
- Unique to Garmin — Apple/Fitbit don't have this
- **Data needed:** `sleepBodyBattery` array (~140 points), `sleepStress` for correlation

### Weekday vs Weekend Heatmap Grid

7 columns (Mon–Sun) × N weeks. Each cell colored by a metric: total sleep, deep sleep %, bedtime, efficiency.

- Shows "social jet lag" — the weekend vs weekday sleep timing gap
- **Data needed:** `calendarDate` for grid position, any summary metric for color

---

## Comparative / Analytical

### Small Multiples

One small chart per night (e.g. 30 in a 5×6 grid for a month). Each shows the same encoding — a mini hypnogram, mini radial clock, or mini gradient strip.

- Tufte's core principle: the human eye spots outliers in a grid of similar shapes instantly
- "Which night was terrible?" jumps out
- **Data needed:** Any per-night visualization miniaturized

### Sleep Quality Scatter Matrix

Multi-dimensional scatter plot comparing: total sleep, deep %, REM %, efficiency, resting HR, body battery change, average stress, respiration. Each pair gets a scatter plot; diagonal shows distribution.

- Exploratory data analysis for your own body
- Discover personal correlations that differ from population averages
- **Data needed:** Summary fields from `dailySleepDTO` plus derived metrics

### Stress–Sleep Correlation Timeline

Dual y-axis timeline. Top: nightly sleep metrics. Bottom: average stress during sleep. Connect corresponding nights with colored lines (green = good recovery, red = poor).

- Makes the stress–sleep bidirectional relationship visible
- **Data needed:** `sleepStress` averaged, `dailySleepDTO` durations, `bodyBatteryChange`

### Sleep Efficiency Waffle Chart

10×10 grid per night. Filled squares = minutes asleep. Empty = minutes awake in bed. Color of filled squares = stage proportion.

- More tactile than a percentage number
- **Data needed:** `sleepTimeSeconds` vs total in-bed time, stage seconds for color

### Chronotype Radar

Radar/spider chart with axes: avg bedtime, wake time, sleep onset latency, mid-sleep time, total duration, deep %. Plot against published chronotype profiles (lion/bear/wolf/dolphin).

- "Am I actually a wolf chronotype?" becomes answerable
- **Data needed:** Derived from `dailySleepDTO` timestamps and durations

---

## Interactive / Exploratory

### Night Explorer

Scrollable timeline where clicking any night expands into a full multi-channel view: hypnogram + HR + stress + body battery + respiration + movement, all time-aligned. Default view = gradient strip barcode; click zooms in.

- Progressive disclosure: overview first, details on demand (Shneiderman's mantra)
- **Data needed:** All arrays from a single night's JSON, rendered in synchronized charts

### Sleep DJ Mixer

Sliders that filter nights by criteria ("show nights with >90min deep sleep" or "body battery increased >30"). Visualization updates in real-time, highlighting or dimming nights.

- Turns passive viewing into active exploration
- **Data needed:** Summary metrics as filter dimensions

### Animated Sleep Playback

Play through a single night in accelerated real-time. Clock ticks, sleep stage updates, HR line draws, body battery fills up, movement sparkles appear.

- Time-lapse of an invisible process
- **Data needed:** All time-series arrays played back synchronized

---

## Derived Metrics Worth Calculating

| Metric | Formula / Source | What It Reveals |
|---|---|---|
| Sleep efficiency | (actual sleep / time in bed) × 100 | How much of your time in bed is actual sleep (~85% is typical) |
| Sleep debt | Cumulative (8hr target − actual) over rolling window | Deficit accumulation and recovery patterns |
| Bedtime regularity index | Std deviation of sleep onset times | Schedule consistency — the #1 predictor of sleep quality |
| HR nadir timing | Time of lowest HR during sleep | When deepest recovery occurs; shifts when schedule is irregular |
| Body battery charge rate | d(bodyBattery)/dt over sleep | Recovery quality — flat sections = poor, steep = excellent |
| Weekend recovery pattern | Weekday avg vs weekend avg | Social jet lag quantified |
| Stage ratio stability | % deep/light/REM per night | Ratios stay remarkably consistent even as total fluctuates |
| Next-day resting HR | Sleep quality → morning HR correlation | 15 min later bedtime ≈ 10 bpm higher next-day HR (from k-means study) |
| Sleep onset latency | Time between "in bed" and first sleep stage | Falling asleep speed — derived from auto vs confirmed start times |

---

## Tech Stack Options

| Approach | Library | Best For |
|---|---|---|
| Prototype fast | [Observable Plot](https://observablehq.com/plot/) | Ridgelines, heatmaps, horizon charts in ~10 lines |
| Full creative control | [D3.js](https://d3js.org/) | Bespoke, pixel-perfect, SVG export for prints |
| Hand-drawn aesthetic | [Rough.js](https://roughjs.com/) + D3 | Sketchy/organic look, great for posters |
| Generative art | [p5.js](https://p5js.org/) | Particle systems, noise-driven, gallery output |
| React app | [visx](https://airbnb.io/visx/) (Airbnb) | D3-level control, React-native (used by CNN, WSJ) |
| Svelte app | [Layer Cake](https://layercake.graphics/) | SSR, synced brush, small multiples built-in |
| Quick dashboards | [Plotly.js](https://plotly.com/javascript/) | Functional but looks corporate |

---

## Existing Projects Worth Studying

| Project | Stack | Stars | URL |
|---|---|---|---|
| garmin-grafana | Docker + InfluxDB + Grafana | 2.9k | https://github.com/arpanghosh8453/garmin-grafana |
| GarminDB | SQLite + Jupyter | 2.9k | https://github.com/tcgoetz/GarminDB |
| sleep-analysis-garmin | Python + Tableau | — | https://github.com/portermclaws/sleep-analysis-garmin |
| GarminSleepAnalytics | Python + R | — | https://github.com/tintin305/GarminSleepAnalytics |
| activity-to-sleep-analysis | Python + XGBoost | — | https://github.com/newbabak/activity-to-sleep-analysis |

---

## References & Inspiration

- [Or Misgav — "A Garden of Sleep"](https://nightingaledvs.com/a-garden-of-sleep/) — flower metaphor for bedtime data
- [Or Misgav — "First Trimester Nights"](https://nightingaledvs.com/first-trimester-data-tracking/) — Mondrian-inspired sleep grid
- [Leonard Pierce — "Flower Visualizations"](https://nightingaledvs.com/flower-visualizations-uncertainty-of-new-parenthood/) — radial flowers + tree rings for baby data
- [Visual Cinnamon (Nadieh Bremer)](https://www.visualcinnamon.com/portfolio/) — elaborate D3 data art
- [Data Sketches](https://www.datasketch.es/) — 24 creative data viz projects with process write-ups
- [FlowingData — "Who is Sleeping"](https://flowingdata.com/2024/04/24/who-is-sleeping-by-age-and-time/) — animated age-based sleep patterns
- [QuantifiedBob — year of sleep data](https://www.quantifiedbob.com/analyzing-a-year-of-my-sleep-tracking-data/) — Python + MongoDB analysis
- [Reddit: 488 nights of sleep analysis](https://www.reddit.com/r/QuantifiedSelf/comments/1q1dwrn/) — k-means clustering, regularity findings
