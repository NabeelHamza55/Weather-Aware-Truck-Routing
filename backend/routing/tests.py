"""Run with:  python manage.py test"""

import unittest

from . import planner, risk


class WindTests(unittest.TestCase):
    def test_wind_levels(self):
        self.assertEqual(risk.wind_level(10), risk.LOW)
        self.assertEqual(risk.wind_level(25), risk.MODERATE)
        self.assertEqual(risk.wind_level(35), risk.HIGH)
        self.assertEqual(risk.wind_level(45), risk.SEVERE)
        self.assertEqual(risk.wind_level(55), risk.NO_TRAVEL)


class RainAndSnowTests(unittest.TestCase):
    def test_rain_levels(self):
        self.assertEqual(risk.rain_level(0.05), risk.LOW)
        self.assertEqual(risk.rain_level(0.10), risk.MODERATE)
        self.assertEqual(risk.rain_level(0.25), risk.HIGH)
        self.assertEqual(risk.rain_level(1.00), risk.SEVERE)
        self.assertEqual(risk.rain_level(1.01), risk.NO_TRAVEL)

    def test_snow_levels(self):
        self.assertEqual(risk.snow_level(0.2), risk.LOW)
        self.assertEqual(risk.snow_level(0.5), risk.MODERATE)
        self.assertEqual(risk.snow_level(1.0), risk.HIGH)
        self.assertEqual(risk.snow_level(3.0), risk.SEVERE)
        self.assertEqual(risk.snow_level(3.1), risk.NO_TRAVEL)


class LoadRuleTests(unittest.TestCase):
    def test_worst_condition_wins(self):
        self.assertEqual(risk.get_risk(10, 0.3, 0, 20000), risk.HIGH)

    def test_55_mph_is_no_travel_for_any_load(self):
        self.assertEqual(risk.get_risk(55, 0, 0, 0), risk.NO_TRAVEL)

    def test_heavy_load_in_severe_wind(self):
        self.assertEqual(risk.get_risk(50, 0, 0, 30001), risk.NO_TRAVEL)
        self.assertEqual(risk.get_risk(50, 0, 0, 30000), risk.SEVERE)

    def test_very_heavy_load_in_high_wind(self):
        self.assertEqual(risk.get_risk(40, 0, 0, 40001), risk.SEVERE)
        self.assertEqual(risk.get_risk(40, 0, 0, 40000), risk.HIGH)


class RankingTests(unittest.TestCase):
    def make_route(self, severe, high, avg, minutes):
        miles = {"no_travel": 0, "severe": severe, "high": high}
        return {"summary": {"miles_by_level": miles, "avg_risk": avg, "duration_minutes": minutes}}

    def test_fewer_severe_miles_wins_even_if_slower(self):
        safe_but_slow = self.make_route(severe=1, high=50, avg=2, minutes=300)
        fast_but_risky = self.make_route(severe=5, high=0, avg=0.1, minutes=60)
        self.assertLess(planner.ranking_key(safe_but_slow), planner.ranking_key(fast_but_risky))

    def test_same_risk_then_faster_wins(self):
        faster = self.make_route(severe=0, high=0, avg=1, minutes=50)
        slower = self.make_route(severe=0, high=0, avg=1, minutes=60)
        self.assertLess(planner.ranking_key(faster), planner.ranking_key(slower))
