# Copyright (c) 2026, Dharshini  and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff


def execute(filters=None):
    filters = filters or {}

    conditions = [
        ["checkin_date", "between", [filters.get("from_date"), filters.get("to_date")]],
        ["assigned_attendant", "is", "set"]
    ]

    if filters.get("attendant"):
        conditions.append(
            ["assigned_attendant", "=", filters.get("attendant")]
        )

    stays = frappe.get_list(
        "Stay Card",
        filters=conditions,
        fields=[
            "assigned_attendant",
            "status",
            "checkin_date",
            "expected_checkout_date",
            "final_amount"
        ]
    )

    data = {}

    for stay in stays:
        attendant = stay.assigned_attendant

        if attendant not in data:
            data[attendant] = {
                "attendant": attendant,
                "total_stays": 0,
                "completed": 0,
                "nights": 0,
                "revenue": 0
            }

        row = data[attendant]
        row["total_stays"] += 1
        row["completed"] += stay.status == "Picked Up"
        row["revenue"] += stay.final_amount or 0

        if stay.checkin_date and stay.expected_checkout_date:
            row["nights"] += date_diff(
                stay.expected_checkout_date,
                stay.checkin_date
            )

    rows = []

    for row in data.values():
        total = row["total_stays"]

        rows.append({
            "attendant": row["attendant"],
            "total_stays": total,
            "completed": row["completed"],
            "avg_stay_length": round(row["nights"] / total, 2) if total else 0,
            "revenue": row["revenue"],
            "completion_rate": round(row["completed"] / total * 100, 2)
        })

    columns = [
        {"label": "Attendant", "fieldname": "attendant",
         "fieldtype": "Link", "options": "Attendant", "width": 180},

        {"label": "Total Stays", "fieldname": "total_stays",
         "fieldtype": "Int"},

        {"label": "Completed", "fieldname": "completed",
         "fieldtype": "Int"},

        {"label": "Avg Stay Length (nights)", "fieldname": "avg_stay_length",
         "fieldtype": "Float"},

        {"label": "Revenue", "fieldname": "revenue",
         "fieldtype": "Currency"},

        {"label": "Completion Rate %", "fieldname": "completion_rate",
         "fieldtype": "Percent"}
    ]

    chart = {
        "data": {
            "labels": [r["attendant"] for r in rows],
            "datasets": [
                {"name": "Total Stays", "values": [r["total_stays"] for r in rows]},
                {"name": "Completed", "values": [r["completed"] for r in rows]}
            ]
        },
        "type": "bar"
    }

    total_stays = sum(r["total_stays"] for r in rows)
    total_revenue = sum(r["revenue"] for r in rows)
    best = max(rows, key=lambda r: r["completion_rate"])["attendant"] if rows else "-"

    summary = [
        {"label": "Total Stays", "value": total_stays},
        {"label": "Total Revenue", "value": total_revenue, "datatype": "Currency"},
        {"label": "Best Attendant", "value": best}
    ]

    return columns, rows, None, chart, summary
