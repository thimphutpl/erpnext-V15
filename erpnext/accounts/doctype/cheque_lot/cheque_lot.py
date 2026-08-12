# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, flt, cint

class ChequeLot(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		bank_name: DF.Link | None
		branch: DF.Link | None
		end_no: DF.Data | None
		next_no: DF.Data | None
		no_of_cheques: DF.Int
		start_no: DF.Data
		status: DF.Literal["Available", "In Use", "Used"]
	# end: auto-generated types

	pass
def update_cheque_lot(ref_doc):
	if ref_doc:
		current = ref_doc.next_no
		if cint(current) < cint(ref_doc.end_no):
			ref_doc.db_set("next_no", str((cint(current) + 1)).zfill(len(ref_doc.next_no)))
			ref_doc.db_set("status", "In Use")
		else:
			ref_doc.db_set("status", "Used")

def get_cheque_info(name=None):
	res = []
	if name:
		ref_doc = frappe.get_doc("Cheque Lot", name)
		cheque_no = ref_doc.next_no
		cheque_date = nowdate()
		res.append({"reference_no": cheque_no})
		res.append({"reference_date": cheque_date})
		update_cheque_lot(ref_doc)
	
	return res

@frappe.whitelist()
def get_cheque_no_and_date(name=None):
	return get_cheque_info(name) 