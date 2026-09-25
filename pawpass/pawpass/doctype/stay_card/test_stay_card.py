# Copyright (c) 2026, Dharshini and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


def make_service_type(**kwargs):
    data = {
        "doctype": "Service Type",
        "service_name": "test service",
        "is_boarding": 0,
        "base_rate": 100
    }
    data.update(kwargs)
    service_type = frappe.get_doc(data)
    service_type.insert()
    return service_type

def make_attendant(**kwargs):
    data = {
        "doctype": "Attendant",
        "attendant_name": "test attendant"
    }
    data.update(kwargs)
    attendant = frappe.get_doc(data)
    attendant.insert()
    return attendant

def make_pet(vaccination_expiry=None, **kwargs):
    data = {
        "doctype": "Pet",
        "pet_name": "test pet",
        "pet_code": "testpet",
        "species": "Dog",
        "owner_name": "test owner",
        "owner_phone": "9876543210",
        "vaccination_expiry": vaccination_expiry
    }
    data.update(kwargs)
    pet = frappe.get_doc(data)
    pet.insert()
    return pet

def make_stay_card(pet, **kwargs):
    data = {
        "doctype": "Stay Card",
        "pet": pet.name,
        "owner_name": pet.owner_name,
        "owner_phone": pet.owner_phone,
        "checkin_date": today(),
        "purpose": "Grooming Only",
        "status": "Ready for Pickup",
        "service_lines": []
    }
    data.update(kwargs)
    stay_card = frappe.get_doc(data)
    return stay_card


class IntegrationTestStayCard(FrappeTestCase):
	pass