import frappe

def after_install():
    create_default_service_types()
    create_default_settings()

    frappe.msgprint("PawPass installation setup completed successfully.")


def create_default_service_types():
    service_types = [
    ]
    for service in service_types:
        if not frappe.db.exists(
            "Service Type",
            {"service_name": service["service_name"]}
        ):
            doc = frappe.new_doc("Service Type")
            doc.service_name = service["service_name"]
            doc.base_rate = service["base_rate"]
            doc.insert(ignore_permissions=True)


def create_default_settings():
    if not frappe.db.exists("PawPass Settings", "PawPass Settings"):
        settings = frappe.new_doc("PawPass Settings")

        settings.shop_name = "PawPass Grooming & Boarding"
        settings.manager_email = "manager@pawpass.local"
        settings.default_boarding_rate = 400
        settings.vaccination_grace_days = 0
        settings.reminder_days_before_checkout = 1

        settings.insert(ignore_permissions=True)