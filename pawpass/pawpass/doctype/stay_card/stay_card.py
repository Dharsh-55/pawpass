# Copyright (c) 2026, Dharshini  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import add_days, today

class StayCard(Document):
	#E2
    def autoname(self):
        self.name = make_autoname("PC-.YYYY.-.#####")
	#E1
    def validate(self):
        vaccination_expiry = frappe.db.get_value(
            "Pet", self.pet,
            "vaccination_expiry"
        )

        grace_days = frappe.db.get_single_value(
            "PawPass Settings",
            "vaccination_grace_days"
        ) or 0

        if vaccination_expiry:
            expiry = add_days(
                vaccination_expiry,
                grace_days
            )

            if expiry < today():
                self.vaccination_status = "Expired"

                if self.status != "Draft":
                    frappe.throw("vaccination expired")
            else:
                self.vaccination_status = "Valid"
        else:
            self.vaccination_status = "Expired"

            if self.status != "Draft":
                frappe.throw("vaccination missing")

        if self.purpose in ["Boarding", "Both"]:
            if not self.expected_checkout_date:
                frappe.throw("checkout date required")

            if self.expected_checkout_date <= self.checkin_date:
                frappe.throw("checkout date must be after checkin date")

        self.services_total = 0

        for row in self.service_lines:
            row.line_total = (row.rate or 0) * (row.quantity or 0)
            self.services_total += row.line_total

        self.final_amount = self.services_total

    def before_submit(self):
        if self.status != "Ready for Pickup":
            frappe.throw("stay card is not ready")

        if not self.service_lines:
            frappe.throw("add at least one service")

        if self.vaccination_status != "Valid":
            frappe.throw("vaccination is not valid")

    def on_submit(self):
        total_stays = frappe.db.get_value(
            "Pet",
            self.pet,
            "total_stays"
        ) or 0

        frappe.db.set_value(
            "Pet",
            self.pet,
            {
                "last_visit_date": self.actual_checkout_date or today(),
                "total_stays": total_stays + 1
            },
            update_modified=False
        )

        invoice_name = frappe.db.get_value(
            "Invoice",
            {"stay_card": self.name},
            "name"
        )

        if not invoice_name:
            invoice = frappe.new_doc("Invoice")
            invoice.stay_card = self.name
            invoice.owner_name = self.owner_name
            invoice.invoice_date = today()
            invoice.services_total = self.services_total
            invoice.total_amount = self.final_amount
            invoice.payment_status = "Unpaid"
            invoice.insert(ignore_permissions=True)

        frappe.enqueue(
            "pawpass.api.send_stay_complete_email",
            stay_card_name=self.name
        )

    def on_cancel(self):
        self.status = "Cancelled"

        total_stays = frappe.db.get_value(
            "Pet",
            self.pet,
            "total_stays"
        ) or 0

        frappe.db.set_value(
            "Pet",
            self.pet,
            "total_stays",
            max(total_stays - 1, 0),
            update_modified=False
        )

        invoice_name = frappe.db.get_value(
            "Invoice",
            {"stay_card": self.name},
            "name"
        )

        if invoice_name:
            invoice = frappe.get_doc(
                "Invoice",
                invoice_name
            )

            if invoice.docstatus == 1:
                invoice.cancel()

    def on_trash(self):
        if self.status not in ["Draft", "Cancelled"]:
            frappe.throw("only draft or cancelled stays can be deleted")
    
    def before_print(self, print_format=None, style=None):
        self.print_summary = f"{self.owner_name} - {self.pet}"