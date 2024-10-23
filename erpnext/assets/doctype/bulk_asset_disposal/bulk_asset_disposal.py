# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BulkAssetDisposal(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.assets.doctype.bulk_asset_disposal_item.bulk_asset_disposal_item import BulkAssetDisposalItem
		from frappe.types import DF

		amended_form: DF.Link | None
		amended_from: DF.Link | None
		asset_category: DF.Link
		branch: DF.Link | None
		customer: DF.Link | None
		item: DF.Table[BulkAssetDisposalItem]
		sales_invoice: DF.Link | None
		scrap: DF.Literal["", "Scrap Asset"]
		scrap_date: DF.Date
	# end: auto-generated types
	pass
