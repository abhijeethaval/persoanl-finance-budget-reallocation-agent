def load_budget():
    # normally pull from DB; hard-coded for demo
    return [
        {"category": "Rent", "amount": 20_000, "locked": True},
        {"category": "School Fees", "amount": 6_000, "locked": True},
        {"category": "Groceries", "amount": 8_500, "locked": False},
        {"category": "Dining Out", "amount": 4_200, "locked": False},
        {"category": "Utilities", "amount": 3_300, "locked": False},
        {"category": "Subscriptions", "amount": 1_450, "locked": False},
        {"category": "Fuel", "amount": 2_800, "locked": False},
    ]


def simulate(changes):
    budget = load_budget()
    for c in changes:
        for row in budget:
            if row["category"] == c["category"]:
                row["amount"] = c["new_amount"]
    income = 56250
    current_sip = 10000
    surplus = income - current_sip - sum(r["amount"] for r in budget)   # mock net income = 30k
    return {"surplus": surplus}


def format_plan(changes):
    return "\n".join(
        f"• Reduce {c['category']} to ₹{c['new_amount']:,}" for c in changes
    )
