import json
import unittest
from datetime import date

import main


class FleetTests(unittest.TestCase):
    def setUp(self):
        self.fleet = json.load(open("sample_fleet.json"))
        self.today = date(2026, 10, 9)

    def test_overdue_detected(self):
        items = {(i["vehicle"], i["item"]): i for v in self.fleet for i in main.due_items(v, self.today)}
        self.assertLess(items[("TRK-02", "oil change")]["days_left"], 0)
        self.assertEqual(items[("VAN-05", "oil change")]["trigger"], "time")

    def test_capacity_respected(self):
        b = main.schedule(self.fleet, self.today)
        per_day = {}
        for x in b:
            per_day[x["date"]] = per_day.get(x["date"], 0) + 1
            self.assertLess(x["date"].weekday(), 5)
        self.assertTrue(all(n <= main.SLOTS_PER_DAY for n in per_day.values()))
        self.assertEqual(len({x["vehicle"] for x in b}), len(b))


if __name__ == "__main__":
    unittest.main()
