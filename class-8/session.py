"""Keep a session's shipment exceptions and calculate its daily summary."""


class TriageSession:
    def __init__(self):
        self.exceptions = []

    def add_exception(self, exception_result: dict[str, object]) -> None:
        """Save one result returned by process_exception."""
        self.exceptions.append(exception_result)

    def generate_daily_summary(self) -> dict[str, object]:
        """Calculate totals and escalation rate for saved exceptions."""
        category_totals = {
            "delayed": 0,
            "damaged": 0,
            "lost": 0,
            "unknown": 0,
        }
        total_compensation_paid = 0
        escalated_count = 0

        for exception in self.exceptions:
            category = exception["category"]
            compensation = exception["compensation"]
            compensation_amount = compensation["compensation_amount"]

            category_totals[category] = (
                category_totals[category] + compensation_amount
            )
            total_compensation_paid = (
                total_compensation_paid + compensation_amount
            )

            if exception["should_escalate"]:
                escalated_count = escalated_count + 1

        number_of_exceptions = len(self.exceptions)
        if number_of_exceptions == 0:
            escalation_rate = 0
        else:
            escalation_rate = (
                escalated_count / number_of_exceptions
            ) * 100

        costliest_category = None
        highest_category_total = 0

        for category in category_totals:
            if category_totals[category] > highest_category_total:
                highest_category_total = category_totals[category]
                costliest_category = category

        return {
            "number_of_exceptions": number_of_exceptions,
            "total_compensation_paid": total_compensation_paid,
            "escalated_count": escalated_count,
            "escalation_rate": escalation_rate,
            "category_totals": category_totals,
            "costliest_category": costliest_category,
        }
