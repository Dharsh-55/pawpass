# import frappe

# def stay_card_query_conditions(user):
#     if "PP Attendant" not in frappe.get_roles(user):
#         return ""
#     return """
#         `tabStay Card`.assigned_attendant in
#         (select name from `tabAttendant`
#         where user = frappe.session.user)
#         """