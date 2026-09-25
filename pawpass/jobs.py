import frappe
from frappe.utils import today, add_days

def check_upcoming_checkouts():
    already_done = frappe.db.get_value(
        "Audit Log",
        {
            "action": "checkout_reminder",
            "date": today()
        }, "name"
    )
    if already_done:
        return
    settings = frappe.get_single("PawPass Settings")
    reminder_days = settings.reminder_days_before_checkout or 2
    checkout_date = add_days(today(), reminder_days)
    stays = frappe.get_all(
        "Stay Card",
        filters={
            "expected_checkout_date": ["between", [today(), checkout_date]],
            "status": ["in", ["Checked In", "In Service"]]
        },
        fields=[
            "name", "pet",
            "owner_name", "owner_email",
            "expected_checkout_date"
        ]
    )
    for stay in stays:
        if stay.owner_email:
            frappe.sendmail(
                recipients=[stay.owner_email],
                subject="Upcoming Checkout Reminder",
                message=f"""
Hello {stay.owner_name},
your pet {stay.pet} is due for checkout on
{stay.expected_checkout_date}.
""")

    log = frappe.new_doc("Audit Log")
    log.doctype_name = "Stay Card"
    log.document_name = "Checkout Reminder"
    log.action = "checkout_reminder"
    log.user = frappe.session.user
    log.timestamp = frappe.utils.now_datetime()
    log.date = today()
    log.insert(ignore_permissions=True)
    
    # K2
    def show_attendant_details():
        stay_cards = frappe.get_all(
            "Stay Card",
            fields=["name", "assigned_attendant"]
        )
        names = [x.assigned_attendant for x in stay_cards if x.assigned_attendant]
        attendants = frappe.get_all(
            "Attendant",
            filters={"name": ["in", names]},
            fields=["name", "attendant_name", "phone"]
        )
        for att in attendants:
            print(att.attendant_name, att.phone)