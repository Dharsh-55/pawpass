# Copyright (c) 2026, Dharshini  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Attendant(Document):
	def on_update(self):
		days = frappe.db.get_value(
		"PawPass Settings",
		None,
		"reminder_days_before_checkout"
	)
