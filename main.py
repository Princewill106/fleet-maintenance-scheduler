"""Fleet Maintenance Scheduler."""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

INTERVALS = {"oil change": (5000, 90, 35000), "brake pads": (20000, 365, 60000),
             "tyre rotation": (10000, 180, 15000), "air filter": (15000, 365, 12000)}
SLOTS_PER_DAY = 2
MIN_AVAILABLE = 4
LOOKAHEAD = 14


def due_items(v, today):
    out = []
    for item, (km_int, day_int, cost) in INTERVALS.items():
        last = v["last_service"][item]
        km_left = last["km"] + km_int - v["odometer"]
        days_left_km = km_left / v["daily_km"]
        days_left_time = (date.fromisoformat(last["date"]) + timedelta(days=day_int) - today).days
        days_left = min(days_left_km, days_left_time)
        out.append({"vehicle": v["id"], "item": item, "days_left": round(days_left),
                    "due": today + timedelta(days=max(0, round(days_left))), "cost": cost,
                    "trigger": "km" if days_left_km <= days_left_time else "time"})
    return out


def schedule(fleet, today):
    items = [i for v in fleet for i in due_items(v, today) if i["days_left"] <= LOOKAHEAD]
    by_vehicle = {}
    for i in sorted(items, key=lambda i: i["days_left"]):
        by_vehicle.setdefault(i["vehicle"], []).append(i)
    bookings, day_load = [], {}
    for vid, its in sorted(by_vehicle.items(), key=lambda kv: kv[1][0]["days_left"]):
        d = today
        target = min(i["due"] for i in its)
        while True:
            if d.weekday() < 5 and day_load.get(d, 0) < SLOTS_PER_DAY and \
                    len(fleet) - day_load.get(d, 0) - 1 >= MIN_AVAILABLE and (d >= target - timedelta(days=3) or d <= today + timedelta(days=1) or its[0]["days_left"] <= 0):
                break
            d += timedelta(days=1)
        day_load[d] = day_load.get(d, 0) + 1
        bookings.append({"vehicle": vid, "date": d, "items": its})
    return bookings


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="sample_fleet.json")
    ap.add_argument("--today", default="2026-10-09")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    today = date.fromisoformat(a.today)
    fleet = json.loads(Path(a.input).read_text())
    bookings = schedule(fleet, today)
    total = 0
    for b in sorted(bookings, key=lambda b: b["date"]):
        cost = sum(i["cost"] for i in b["items"])
        total += cost
        print(f"{b['date']:%a %d %b}  {b['vehicle']:<8} NGN {cost:>7,}")
        for i in b["items"]:
            state = "OVERDUE" if i["days_left"] < 0 else f"due in {i['days_left']}d"
            print(f"      - {i['item']:<14} {state:<12} (by {i['trigger']})")
    print(f"\nWork orders: {len(bookings)} | estimated cost: NGN {total:,} | "
          f"max off-road per day: {SLOTS_PER_DAY}, min available: {MIN_AVAILABLE}")
    Path("output").mkdir(exist_ok=True)
    Path("output/work_orders.json").write_text(json.dumps(bookings, default=str, indent=2))


if __name__ == "__main__":
    main()
