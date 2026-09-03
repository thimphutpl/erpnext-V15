# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe 
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class AdvanceEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.mobilisation_entry_item.mobilisation_entry_item import MobilisationEntryItem
		from frappe.types import DF

		advance: DF.Link | None
		advance_recoup: DF.Link | None
		advance_type: DF.Link | None
		amended_from: DF.Link | None
		branch: DF.Link | None
		cost_center: DF.Link | None
		customer: DF.DynamicLink | None
		is_cancelled: DF.Check
		is_opening: DF.Check
		is_running_bill: DF.Check
		mobilisation_entry: DF.Table[MobilisationEntryItem]
		party_type: DF.Literal["", "Supplier", "Employee", "Customer"]
		posting_date: DF.Date | None
		posting_time: DF.Time | None
	# end: auto-generated types

	pass
@frappe.whitelist()
def get_advance(customer,party_type,advance_type,branch=None):
    if not customer:
        frappe.throw(_("Customer is required"))

    filters = {"customer": customer}
    if branch:
        filters["branch"] = branch

    if party_type:
        filters["party_type"] = party_type
    if advance_type:
        filters["advance_type"] = advance_type


    entries = frappe.get_all(
        "Advance Entry",
        filters=filters,
        fields=["name","branch","posting_date"],
    )
   
    result = []

    for entry in entries:
        children = frappe.get_all(
            "Mobilisation Entry Item",
            filters={"parent": entry.name,
                     "balance_amount": [">", 0]},
            fields=[
                    "name",
                    "reference",
                    "advance_type",
                    "account",
                    "advance_amount",
                    "total_amount",
                    "balance_amount",
                    "budget_activity",
                    "budget_sub_activity",
                    "source_of_fund",
                     
                ],
        )
        for child in children:
            if flt(child.balance_amount) > 0:
                result.append({
                    "parent": entry.parent,
                    "advance_entry": entry.name,
                    "posting_date": entry.posting_date,
                    "branch": entry.branch,
                    "reference": child.reference,
                    "advance_type": child.advance_type,
                    "account": child.account,
                    "budget_activity": child.budget_activity,
                    "budget_sub_activity": child.budget_sub_activity,
                    "source_of_fund": child.source_of_fund,
                    "total_amount": child.balance_amount,
                    "advance_amount": child.advance_amount,
                    "balance_amount": child.balance_amount
                })
        if not result:
            return "No advance available"
    return result