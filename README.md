# Fleet Maintenance Scheduler

> Services each vehicle by kilometres or days, whichever comes first, and never takes too many off the road at once.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Offline demo](https://img.shields.io/badge/demo-runs%20offline-brightgreen) ![n8n](https://img.shields.io/badge/n8n-importable%20workflow-EA4B71) ![n8n](https://img.shields.io/badge/n8n-importable%20workflow-EA4B71) ![Series](https://img.shields.io/badge/AI%20Automation-36%2F50-purple)

**Sector:** Logistics & Fleet  ·  **Project 36 of 50** in my [AI Automation Projects series](https://github.com/Princewill106/Princewill106)

## The problem

Fleet owners service vehicles when they break down, which is the most expensive time to do it. A truck off the road unexpectedly costs a day's deliveries plus the repair, and a missed oil change today is an engine rebuild in six months.

## How it works

```mermaid
flowchart LR
    S0["Odometer + history"]
    S1["Service intervals"]
    S2["Due-date projection"]
    S3["Capacity-aware booking"]
    S4["Work orders + cost"]
    S0 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
```

1. **Load** — Read each vehicle's odometer, average daily km and last service per item (`sample_fleet.json`).
2. **Intervals** — Service items have km and day intervals (oil every 5,000 km or 90 days, etc.).
3. **Project** — The due date for each item is the earlier of the km-based and day-based dates.
4. **Book** — Items due in the next 14 days are booked on the earliest workday where the workshop has a slot and enough vehicles remain on the road.
5. **Report** — Work orders, overdue items and a cost estimate are printed and saved.

## Features

- Km-or-days, whichever first
- Overdue flags
- Minimum-availability rule
- Workshop slots per day
- Monthly cost estimate

## Quick start

```bash
git clone https://github.com/Princewill106/fleet-maintenance-scheduler.git
cd fleet-maintenance-scheduler
python main.py --demo
```

No installs needed: it uses only the Python standard library. The demo runs fully offline using the sample data in this repo.

**Optional: plug in an LLM.** Copy `.env.example` to `.env` and add an Anthropic or OpenAI key. The project will then use the model for the language-heavy steps and fall back to its rule-based logic if a call fails.

Run the tests:

```bash
python -m unittest -v
```

## Sample output

```text
Fri 09 Oct  TRK-02   NGN  35,000
      - oil change     OVERDUE      (by time)
Fri 09 Oct  TRK-01   NGN 122,000
      - oil change     due in 1d    (by km)
      - brake pads     due in 7d    (by km)
      - tyre rotation  due in 7d    (by km)
      - air filter     due in 12d   (by km)
Tue 20 Oct  VAN-05   NGN  35,000
      - oil change     due in 14d   (by time)

Work orders: 3 | estimated cost: NGN 192,000 | max off-road per day: 2, min available: 4
```

## Use it in n8n (no code needed)

[`n8n-workflow.json`](n8n-workflow.json) is a ready-to-import n8n version of this project, built for n8n 1.x.

1. In n8n, open **Workflows → Import from File** and choose `n8n-workflow.json`.
2. Click **Test workflow**. It runs the full logic on the sample data built into the *Sample data* node, so you can see the results before connecting anything.
3. Open each output node and connect your accounts: Google Sheets (OAuth2). For Google Sheets, pick your spreadsheet and sheet.
4. Adjust the settings at the top of the **Logic** node (thresholds, templates, contacts), then **Activate**.

**Flow:** **Schedule (weekdays 6am)** → Read fleet sheet → **Logic** (Code node)

**Outputs:**
- Add work orders for workshop

The Logic node is a JavaScript port of the rules in `main.py`, so you can run the project in n8n without Python.

## Use it on your own data

Fill `sample_fleet.json` with your vehicles, update `INTERVALS` and costs, and run `python main.py --today 2026-10-09`. Feed odometers from your GPS tracker for hands-off scheduling.

## Project structure

```text
n8n-workflow.json            Importable n8n workflow
.env.example                 Optional API key settings
.gitignore                   Git ignore rules
LICENSE                      MIT license
README.md                    This file
llm.py                       Optional LLM helper (offline fallback)
main.py                      Entry point and core logic
requirements.txt             Dependencies (stdlib only)
sample_fleet.json            Sample input data for the demo
test_main.py                 Unit tests
```

## Who this is for

- Haulage and delivery fleets
- School bus operators
- Ride-hailing fleet owners

## Ideas to extend it

- [ ] Odometer sync from GPS trackers
- [ ] Driver defect reports via WhatsApp
- [ ] Parts inventory integration
- [ ] Breakdown-risk scoring

## About

Built by **Ogbu Ugochukwu Princewill**, AI Automation Lead and robotics engineer. I teach people and businesses to build with AI, not just talk about it. [LinkedIn](https://www.linkedin.com/in/ugochukwu-ogbu-653a0816a)

If this helped you, give it a ⭐ and share what you built with it.

## License

MIT — see [LICENSE](LICENSE).
