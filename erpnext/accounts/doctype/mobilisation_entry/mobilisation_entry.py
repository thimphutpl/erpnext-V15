# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class MobilisationEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.mobilisation_entry_item.mobilisation_entry_item import MobilisationEntryItem
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		cost_center: DF.Link | None
		customer: DF.Link | None
		is_running_bill: DF.Check
		mobilisation_entry: DF.Table[MobilisationEntryItem]
		posting_date: DF.Date | None
		posting_time: DF.Time | None
	# end: auto-generated types

	pass
@frappe.whitelist()
def get_mobilisation_advance(customer,branch=None):
    # frappe.msgprint(str(is_running_bill))
    if not customer:
        frappe.throw(_("Customer is required"))

    filters = {"customer": customer, "docstatus": 1,"is_running_bill": 1}
    # if is_running_bill is not None:
    #     filters["is_running_bill"] = is_running_bill
    if branch:
        filters["branch"] = branch


    entries = frappe.get_all(
        "Mobilisation Entry",
        filters=filters,
        fields=["name","branch","posting_date"],
        
        # limit=1
    )

    result = []

    for entry in entries:
        children = frappe.get_all(
            "Mobilisation Entry Item",
            filters={"parent": entry.name},
            fields=["reference","advance_type","account","advance_amount","balance_amount"]
        )
        for child in children:
            if flt(child.balance_amount) > 0:
                result.append({
                    "mobilisation_entry": entry.name,
                    "posting_date": entry.posting_date,
                    "branch": entry.branch,
                    "reference": child.reference,
                    "advance_type": child.advance_type,
                    "account": child.account,
                    "advance_amount": child.advance_amount,
                    "balance_amount": child.balance_amount
                })
        if not result:
            return "No advance available"
    return result