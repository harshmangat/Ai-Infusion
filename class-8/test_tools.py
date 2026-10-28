"""Simple checks for each shipment compensation calculator."""

from tools import (
    calculate_damage_compensation,
    calculate_delay_compensation,
    calculate_lost_compensation,
)


def test_delay_compensation():
    print("Testing delayed shipments...")

    # One day is $10.
    result = calculate_delay_compensation(100, 1)
    assert result["compensation_amount"] == 10

    # The cap is 20% of $100, which is $20.
    result = calculate_delay_compensation(100, 5)
    assert result["compensation_amount"] == 20

    # No delay means no compensation.
    result = calculate_delay_compensation(100, 0)
    assert result["compensation_amount"] == 0

    print("Delayed shipment tests passed.")


def test_damage_compensation():
    print("Testing damaged shipments...")

    result = calculate_damage_compensation(100, "minor")
    assert result["compensation_amount"] == 25

    result = calculate_damage_compensation(100, "moderate")
    assert result["compensation_amount"] == 50

    result = calculate_damage_compensation(100, "severe")
    assert result["compensation_amount"] == 100

    print("Damaged shipment tests passed.")


def test_lost_compensation():
    print("Testing lost shipments...")

    result = calculate_lost_compensation(100)
    assert result["compensation_amount"] == 150
    assert result["goodwill_credit"] == 50

    print("Lost shipment tests passed.")


def test_invalid_inputs():
    print("Testing invalid inputs...")

    try:
        calculate_delay_compensation(-1, 1)
        assert False, "Negative shipment value should be rejected."
    except ValueError:
        pass

    try:
        calculate_damage_compensation(100, "unknown")
        assert False, "Unknown damage severity should be rejected."
    except ValueError:
        pass

    try:
        calculate_lost_compensation(-1)
        assert False, "Negative shipment value should be rejected."
    except ValueError:
        pass

    print("Invalid input tests passed.")


if __name__ == "__main__":
    test_delay_compensation()
    test_damage_compensation()
    test_lost_compensation()
    test_invalid_inputs()
    print("All compensation tests passed.")
