import frappe
from frappe.query_builder import DocType
from frappe.utils import add_days, today

#B2a
@frappe.whitelist()
def get_upcoming_checkouts():
    StayCard = frappe.qb.DocType("Stay Card")
    cutoff_date = add_days(today(), 2)

    rows = (frappe.qb.from_(StayCard)
            .select(StayCard.name,
                    StayCard.pet,
                    StayCard.owner_name,
                    StayCard.expected_checkout_date,)
                    .where(
                        (StayCard.status.isin(["Checked In", "In Service"]))
                        & (StayCard.expected_checkout_date <= cutoff_date)
                    )
                    .orderby(StayCard.expected_checkout_date)).run(as_dict = True)
    return rows

#B2b
@frappe.whitelist()
def transfer_stays(from_attendant, to_attendant):
    try:
        frappe.db.sql(
            """
            update `tabStay Card` 
            set assigned_attendant =  %(to_attendant)s
            where assigned_attendant = %(from_attendant)s
            and status in ('Checked In', 'In Service')
            """,
        {
            "from_attendant": from_attendant,
            "to_attendant": to_attendant,
        },
        )
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error(
            frappe.get_traceback(),
            "PawPass: trasnfer_stays failed",
        )
        raise