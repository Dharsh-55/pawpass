# Copyright (c) 2026, Dharshini  and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Pet(Document):
	def autoname(self):
		if self.pet_code:
			self.name = self.pet_code.upper()
		else:
			self.name = make_autoname("PET-.YYYY.-.####")
