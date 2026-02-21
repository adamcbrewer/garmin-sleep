#!/usr/bin/env python3
"""Preprocess raw Garmin sleep JSONs into optimized datasets for visualization."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "sleep"
OUT_DIR = Path(__file__).parent / "data"


def epoch_to_hours(epoch_ms, ref_date_str):
    """Convert epoch ms to fractional hours from 6pm on the reference date's eve."""
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    ref = datetime.strptime(ref_date_str, "%Y-%m-%d").replace(
        hour=18, tzinfo=timezone.utc
    )
    ref = ref.replace(day=ref.day - 1) if dt.hour < 12 else ref
    delta = (dt - ref).total_seconds() / 3600
    return round(delta, 4)


def iso_to_hours(iso_str):
    """Convert ISO datetime to fractional hour of day (0-24+)."""
    clean = iso_str.split(".")[0]
    dt = datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S")
    h = dt.hour + dt.minute / 60
    if h < 12:
        h += 24
    return round(h, 4)


def load_night(filepath):
    with open(filepath) as f:
        return json.load(f)


def process_all():
    files = sorted(DATA_DIR.glob("*.json"))
    print(f"Processing {len(files)} sleep files...")

    summary = []
    all_levels = []
    all_movement = []
    all_hr = []
    all_stress = []
    all_battery = []
    all_respiration = []
    nights_detail = {}

    for filepath in files:
        try:
            data = load_night(filepath)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  Skipping {filepath.name}: {e}")
            continue

        dto = data.get("dailySleepDTO", {})
        date = dto.get("calendarDate")
        if not date:
            continue

        sleep_seconds = dto.get("sleepTimeSeconds", 0)
        if sleep_seconds == 0:
            continue

        deep = dto.get("deepSleepSeconds") or 0
        light = dto.get("lightSleepSeconds") or 0
        rem = dto.get("remSleepSeconds") or 0
        awake = dto.get("awakeSleepSeconds") or 0
        total = deep + light + rem

        start_local = dto.get("sleepStartTimestampLocal") or 0
        end_local = dto.get("sleepEndTimestampLocal") or 0
        start_gmt = dto.get("sleepStartTimestampGMT") or 0
        end_gmt = dto.get("sleepEndTimestampGMT") or 0
        in_bed_seconds = (end_gmt - start_gmt) / 1000 if end_gmt and start_gmt else 0
        efficiency = round(total / in_bed_seconds * 100, 1) if in_bed_seconds > 0 else 0

        start_dt = datetime.fromtimestamp(start_local / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(end_local / 1000, tz=timezone.utc)
        bedtime_h = start_dt.hour + start_dt.minute / 60
        if bedtime_h < 12:
            bedtime_h += 24
        waketime_h = end_dt.hour + end_dt.minute / 60
        if waketime_h < bedtime_h - 12:
            waketime_h += 24

        avg_hr = None
        hr_data = data.get("sleepHeartRate") or []
        if hr_data:
            vals = [h["value"] for h in hr_data if h.get("value")]
            avg_hr = round(sum(vals) / len(vals), 1) if vals else None

        min_hr = None
        if hr_data:
            vals = [h["value"] for h in hr_data if h.get("value")]
            min_hr = min(vals) if vals else None

        avg_stress = None
        stress_data = data.get("sleepStress") or []
        if stress_data:
            vals = [s["value"] for s in stress_data if s.get("value") is not None]
            avg_stress = round(sum(vals) / len(vals), 1) if vals else None

        avg_resp = dto.get("averageRespirationValue")
        bb_change = data.get("bodyBatteryChange")
        resting_hr = data.get("restingHeartRate")

        night_summary = {
            "date": date,
            "dayOfWeek": start_dt.strftime("%a"),
            "bedtime": round(bedtime_h, 2),
            "waketime": round(waketime_h, 2),
            "totalSleep": total,
            "deep": deep,
            "light": light,
            "rem": rem,
            "awake": awake,
            "inBed": round(in_bed_seconds),
            "efficiency": efficiency,
            "avgHR": avg_hr,
            "minHR": min_hr,
            "restingHR": resting_hr,
            "avgStress": avg_stress,
            "avgRespiration": avg_resp,
            "bodyBatteryChange": bb_change,
        }
        summary.append(night_summary)

        levels = data.get("sleepLevels") or []
        for lvl in levels:
            all_levels.append({
                "date": date,
                "start": iso_to_hours(lvl["startGMT"]),
                "end": iso_to_hours(lvl["endGMT"]),
                "stage": lvl["activityLevel"],
            })

        movement = data.get("sleepMovement") or []
        mv_arr = []
        for mv in movement:
            mv_arr.append({
                "h": iso_to_hours(mv["startGMT"]),
                "v": round(mv["activityLevel"], 2),
            })
        if mv_arr:
            all_movement.append({"date": date, "data": mv_arr})

        for hr in hr_data:
            ts = hr.get("startGMT", 0)
            dt_hr = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            h = dt_hr.hour + dt_hr.minute / 60
            if h < 12:
                h += 24
            all_hr.append({
                "date": date,
                "h": round(h, 4),
                "v": hr["value"],
            })

        for s in stress_data:
            ts = s.get("startGMT", 0)
            dt_s = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            h = dt_s.hour + dt_s.minute / 60
            if h < 12:
                h += 24
            all_stress.append({
                "date": date,
                "h": round(h, 4),
                "v": s["value"],
            })

        bb_data = data.get("sleepBodyBattery") or []
        for bb in bb_data:
            ts = bb.get("startGMT", 0)
            dt_bb = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            h = dt_bb.hour + dt_bb.minute / 60
            if h < 12:
                h += 24
            all_battery.append({
                "date": date,
                "h": round(h, 4),
                "v": bb["value"],
            })

        resp_data = data.get("wellnessEpochRespirationDataDTOList") or []
        for r in resp_data:
            ts = r.get("startTimeGMT", 0)
            rv = r.get("respirationValue", -1)
            if rv < 0:
                continue
            dt_r = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            h = dt_r.hour + dt_r.minute / 60
            if h < 12:
                h += 24
            all_respiration.append({
                "date": date,
                "h": round(h, 4),
                "v": round(rv, 1),
            })

        nights_detail[date] = {
            "summary": night_summary,
            "levels": [{"start": iso_to_hours(l["startGMT"]), "end": iso_to_hours(l["endGMT"]), "stage": l["activityLevel"]} for l in levels],
            "hr": [{"h": round((datetime.fromtimestamp(h["startGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(h["startGMT"]/1000, tz=timezone.utc).minute/60) + (24 if (datetime.fromtimestamp(h["startGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(h["startGMT"]/1000, tz=timezone.utc).minute/60) < 12 else 0), 4), "v": h["value"]} for h in hr_data],
            "stress": [{"h": round((datetime.fromtimestamp(s["startGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(s["startGMT"]/1000, tz=timezone.utc).minute/60) + (24 if (datetime.fromtimestamp(s["startGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(s["startGMT"]/1000, tz=timezone.utc).minute/60) < 12 else 0), 4), "v": s["value"]} for s in stress_data],
            "battery": [{"h": round((datetime.fromtimestamp(b["startGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(b["startGMT"]/1000, tz=timezone.utc).minute/60) + (24 if (datetime.fromtimestamp(b["startGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(b["startGMT"]/1000, tz=timezone.utc).minute/60) < 12 else 0), 4), "v": b["value"]} for b in bb_data],
            "movement": mv_arr,
            "respiration": [{"h": round((datetime.fromtimestamp(r["startTimeGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(r["startTimeGMT"]/1000, tz=timezone.utc).minute/60) + (24 if (datetime.fromtimestamp(r["startTimeGMT"]/1000, tz=timezone.utc).hour + datetime.fromtimestamp(r["startTimeGMT"]/1000, tz=timezone.utc).minute/60) < 12 else 0), 4), "v": round(r["respirationValue"], 1)} for r in resp_data if r.get("respirationValue", -1) >= 0],
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, separators=(",", ":"))
    print(f"  summary.json: {len(summary)} nights")

    with open(OUT_DIR / "levels.json", "w") as f:
        json.dump(all_levels, f, separators=(",", ":"))
    print(f"  levels.json: {len(all_levels)} segments")

    with open(OUT_DIR / "movement.json", "w") as f:
        json.dump(all_movement, f, separators=(",", ":"))
    print(f"  movement.json: {len(all_movement)} nights")

    hr_by_date = {}
    for item in all_hr:
        d = item["date"]
        if d not in hr_by_date:
            hr_by_date[d] = []
        hr_by_date[d].append({"h": item["h"], "v": item["v"]})
    with open(OUT_DIR / "heartrate.json", "w") as f:
        json.dump(hr_by_date, f, separators=(",", ":"))
    print(f"  heartrate.json: {len(all_hr)} readings")

    stress_by_date = {}
    for item in all_stress:
        d = item["date"]
        if d not in stress_by_date:
            stress_by_date[d] = []
        stress_by_date[d].append({"h": item["h"], "v": item["v"]})
    with open(OUT_DIR / "stress.json", "w") as f:
        json.dump(stress_by_date, f, separators=(",", ":"))
    print(f"  stress.json: {len(all_stress)} readings")

    bb_by_date = {}
    for item in all_battery:
        d = item["date"]
        if d not in bb_by_date:
            bb_by_date[d] = []
        bb_by_date[d].append({"h": item["h"], "v": item["v"]})
    with open(OUT_DIR / "battery.json", "w") as f:
        json.dump(bb_by_date, f, separators=(",", ":"))
    print(f"  battery.json: {len(all_battery)} readings")

    resp_by_date = {}
    for item in all_respiration:
        d = item["date"]
        if d not in resp_by_date:
            resp_by_date[d] = []
        resp_by_date[d].append({"h": item["h"], "v": item["v"]})
    with open(OUT_DIR / "respiration.json", "w") as f:
        json.dump(resp_by_date, f, separators=(",", ":"))
    print(f"  respiration.json: {len(all_respiration)} readings")

    detail_dates = sorted(nights_detail.keys())
    sample_dates = []
    if len(detail_dates) >= 10:
        step = len(detail_dates) // 10
        sample_dates = detail_dates[::step][:10]
    else:
        sample_dates = detail_dates

    sample_detail = {d: nights_detail[d] for d in sample_dates}
    with open(OUT_DIR / "nights_sample.json", "w") as f:
        json.dump(sample_detail, f, separators=(",", ":"))
    print(f"  nights_sample.json: {len(sample_detail)} detailed nights")

    all_detail = {d: nights_detail[d] for d in detail_dates}
    with open(OUT_DIR / "nights_all.json", "w") as f:
        json.dump(all_detail, f, separators=(",", ":"))
    print(f"  nights_all.json: {len(all_detail)} detailed nights")

    print("\nDone!")


if __name__ == "__main__":
    process_all()
