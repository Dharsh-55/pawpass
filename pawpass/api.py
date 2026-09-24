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

#D1
@frappe.whitelist()
def share_stay_card(stay_card_name, user_email):
    frappe.get_doc("Stay Card", stay_card_name)
    frappe.share.add(
        "Stay Card",
        stay_card_name,
        user_email,
        read=1
    )
    return {
        "message": "success"
    }

#D4 - dont leak data
@frappe.whitelist()
def unsafe():
    return frappe.get_all(
        "Stay Card",
        fields= [
            "name","pet","owner_name",
            "owner_phone","owner_email",
            "status",
        ],
    )

@frappe.whitelist()
def safe():
    rows = frappe.get_list(
        "Stay Card",
        fields = [
            "name","pet",
            "owner_name","owner_email",
            "status"
        ],
    )
    if "PP Manager" not in frappe.get_roles():
        for i in rows:
            i.pop("owner_name")
            i.pop("owner_email")
    return rows

#E2
@frappe.whitelist()
def rename_attendant(old, new):
    return frappe.rename_doc(
        "Attendant",
        old,
        new,
        merge=False
    )
    
# L1
import frappe


@frappe.whitelist()
def get_stay_summary():
    stay_card_name = frappe.form_dict.get("stay_card_name")

    if not frappe.db.exists("Stay Card", stay_card_name):
        frappe.local.response.http_status_code = 404
        return {"error": "Not found"}

    stay = frappe.get_doc("Stay Card", stay_card_name)

    return {
        "name": stay.name,
        "pet": stay.pet,
        "owner_name": stay.owner_name,
        "status": stay.status,
        "expected_checkout_date": stay.expected_checkout_date,
        "final_amount": stay.final_amount
    }
    
