# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AnnualTender(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.buying.doctype.annual_tender_details.annual_tender_details import AnnualTenderDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		company: DF.Link
		currency: DF.Link
		fiscal_year: DF.Link
		supplier: DF.Link
		table_zifs: DF.Table[AnnualTenderDetails]
	# end: auto-generated types
	pass
