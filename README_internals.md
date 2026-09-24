### Part-B: B2c - Dangerous Patterns

# Bug-1: 
self.save() is used inside validate function, whereas the actual lifecycle is save() -> validate() -> before_save(), according to this existing code, it leads to a infinite loop inbetween validate() and save().

# Bug-2:
pet.total_stays += 1, is a update code which cant be done inside validate(), because it leads to a complete lifecycle of validation in loop. Whereas this update can be done while the documents are being submitted.

# Corrected Code:
def validate(self):
    self.services_total = sum(r.line_total for r in self.service_lines)
def on_submit(self):
    pet = frappe.get_doc("Pet", self.pet)
    pet.total_stays += 1
    pet.save()

### Part-B: B2d - Concurrency
Let's assume that User A and User B opens the same document at the same time and User A does some change and saves it. Wihtout refreshing the page or reloading the document User B wont be able to change something again and save it, frappe will block the save since B is working with the older version of the document to prevent overwriting A's change.


### Part-D: D2 - frappe.get_all()




### Part-E

# E1 - self.save() inside on_update
def on_update(self):
    self.save()
the above code leads to an infinite loop of running of on_update() -> save() -> on_update() -> save(). so to avoid this we can write something like:
def on_update(self):
    frappe.logger().info("stay card updated")

# E3 - doc.get_value() vs get_doc() 
In the Attendant on_update controller, frappe.db.get_value() is preferable because only reminder_days_before_checkout is required from PawPass Settings. get_doc() loads the complete settings document as a Document object, whereas get_value() directly retrieves the required field without loading the full document.


### I1 - Active stays query report

# Parameterized query:
select name, pet, owner_name, status, assigned_attendant,
expected_checkout_date, creation
from `tabStay Card` where status not in ("Picked Up", "Cancelled")
and (%(attendant)s is null or %(attendant)s='' or assigned_attendant = %(attendant)s)
order by expected_checkout_date asc

# f-string:
attendant = filters.get("attendant")
query = f"""
select name, pet, owner_name, status,
 assigned_attendant,expected_checkout_date
from `tabStay Card`
where status not in ("Picked Up", "Cancelled")
and ('{attendant}' = '' or assigned_attendant = '{attendant}')
order by expected_checkout_date asc
"""

Parameterized query is preferred because it avoides sql injection and does the substitution of values safely.


### H1 - Async frappe.call() and validate

frappe.call() is asynchronous. It sends a request to the server and the
response comes back later.
when I use frappe.call() inside the client validate event, validation can
finish before the server response comes back. So I cannot reliably use the response to decide whether the form should be saved.

so, I use asynchronous calls in events such as refresh,
onload, or field-change events instead of depending on them inside
validate.

### J1 - Print format and before_print

data can be fetched directly inside a jinja print format, 
using frappe.get_all(). but, doing database queries directly in
the template can makes the print format more complex.

a better approach for data that is needed by the print format is to
prepare it in the before_print() method of the controller and then use the prepared value in jinja.


### K2 - N+1 query problem

in the given code get_doc() is inside the for loop, which leads to multiple db calls. like if I have 10 stay cards, it takes 11 db calls (1 get_all() and 10 get_doc()) but we can reduce it to just 2 calls using the below fixed code:

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