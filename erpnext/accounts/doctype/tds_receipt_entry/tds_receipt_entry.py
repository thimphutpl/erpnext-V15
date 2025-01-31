# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TDSReceiptEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bill_no: DF.Data | None
		branch: DF.Link | None
		cheque_date: DF.Date | None
		cheque_no: DF.Data | None
		cost_center: DF.Link | None
		fiscal_year: DF.Data | None
		invoice_no: DF.Data | None
		invoice_type: DF.Data | None
		month: DF.Data | None
		pbva: DF.Data | None
		posting_date: DF.Date | None
		purpose: DF.Data | None
		receipt_date: DF.Date | None
		receipt_number: DF.Data | None
		region: DF.Data | None
		tds_receipt_update: DF.Link | None
		tds_remittance: DF.Link | None
	# end: auto-generated types
	pass


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabRRCO Receipt Entry`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabRRCO Receipt Entry`.branch)
	)""".format(user=user)
