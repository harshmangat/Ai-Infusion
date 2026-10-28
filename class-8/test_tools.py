import unittest

from tools import (
    calculate_damage_compensation,
    calculate_delay_compensation,
    calculate_lost_compensation,
)


class DelayCompensationTests(unittest.TestCase):
    def test_daily_rate_and_value_cap(self):
        self.assertEqual(
            calculate_delay_compensation(100, 1)["compensation_amount"],
            10.0,
        )
        self.assertEqual(
            calculate_delay_compensation(100, 5)["compensation_amount"],
            20.0,
        )

    def test_zero_delay_and_zero_value(self):
        self.assertEqual(
            calculate_delay_compensation(100, 0)["compensation_amount"],
            0.0,
        )
        self.assertEqual(
            calculate_delay_compensation(0, 3)["compensation_amount"],
            0.0,
        )

    def test_rejects_negative_or_non_integer_delay(self):
        for days_delayed in (-1, 1.5, True):
            with self.subTest(days_delayed=days_delayed):
                with self.assertRaises(ValueError):
                    calculate_delay_compensation(100, days_delayed)


class DamageCompensationTests(unittest.TestCase):
    def test_compensation_by_severity(self):
        expected_amounts = {
            "minor": 25.0,
            "moderate": 50.0,
            "severe": 100.0,
        }
        for severity, expected_amount in expected_amounts.items():
            with self.subTest(severity=severity):
                result = calculate_damage_compensation(100, severity)
                self.assertEqual(result["compensation_amount"], expected_amount)
                self.assertEqual(result["severity"], severity)

    def test_severity_is_case_insensitive_and_trimmed(self):
        result = calculate_damage_compensation(100, " Moderate ")
        self.assertEqual(result["compensation_amount"], 50.0)
        self.assertEqual(result["severity"], "moderate")

    def test_rejects_unknown_severity(self):
        with self.assertRaises(ValueError):
            calculate_damage_compensation(100, "unknown")


class LostCompensationTests(unittest.TestCase):
    def test_full_value_plus_goodwill_credit(self):
        result = calculate_lost_compensation(125.50)
        self.assertEqual(result["compensation_amount"], 175.50)
        self.assertEqual(result["goodwill_credit"], 50.0)

    def test_zero_value_still_includes_goodwill_credit(self):
        self.assertEqual(
            calculate_lost_compensation(0)["compensation_amount"],
            50.0,
        )


class ShipmentValueValidationTests(unittest.TestCase):
    def test_all_calculators_reject_negative_shipment_value(self):
        calculators = (
            lambda: calculate_delay_compensation(-1, 1),
            lambda: calculate_damage_compensation(-1, "minor"),
            lambda: calculate_lost_compensation(-1),
        )
        for calculate in calculators:
            with self.subTest(calculator=calculate):
                with self.assertRaises(ValueError):
                    calculate()


if __name__ == "__main__":
    unittest.main()
