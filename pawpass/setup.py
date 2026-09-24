import frappe


def after_install():
    create_default_service_types()
    create_default_settings()

    frappe.msgprint("PawPass installation setup completed successfully.")


def create_default_service_types():
    service_types = [
        # EXACT 4 service types from the task brief
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
    settings = frappe.get_single("PawPass Settings")

    if not settings.reminder_days:
        settings.reminder_days = 2

    settings.save(ignore_permissions=True)