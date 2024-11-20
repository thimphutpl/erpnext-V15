# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class DHIGCOAMapper(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.dhi_mapper_item.dhi_mapper_item import DHIMapperItem
		from frappe.types import DF

		account_code: DF.Link
		account_name: DF.Data | None
		account_type: DF.Data | None
		is_inter_company: DF.Check
		items: DF.Table[DHIMapperItem]
		root_type: DF.Data | None
	# end: auto-generated types
	pass

@frappe.whitelist()
def filter_account(doctype, txt, searchfield, start, page_len, filters):
	query = """
		SELECT 
			dg.account_code,
			dg.account_name,
			dg.account_type
		FROM `tabDHI GCOA` dg 
		WHERE NOT EXISTS(
			SELECT 1 FROM 
			`tabDHI GCOA Mapper` dgm
			WHERE dg.account_code = dgm.account_code
		)
		
	"""
	return frappe.db.sql(query)