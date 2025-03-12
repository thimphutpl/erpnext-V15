import frappe

def make_journal_entry():
	doc = frappe.get_doc("Employee Advance", "HR-EAD-2025-00004")
	doc.post_journal_entry()
	print("DONE")