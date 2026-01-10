# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class BankGurantee(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		bg_amount: DF.Data | None
		bg_date: DF.Date | None
		bg_expiry_date: DF.Date | None
		bg_number: DF.Data | None
		bg_type: DF.Literal["", "Advance Bank Guarantee", "Performance Bank Guarantee", "Performance Security", "Retention Bank Guarantee"]
		contract: DF.Link
		contract_final_price: DF.Data | None
		contract_name: DF.SmallText | None
		focal_person: DF.Link | None
		focal_person_name: DF.Data | None
		reference_number: DF.Data | None
		revised_bg_number: DF.Data | None
		revised_expiry_date: DF.Date | None
		supplier: DF.Link
		supplier_name: DF.Data | None
		supplier_type: DF.Literal["", "Domestic Vendor", "Indian Vendor", "International Vendor"]
	# end: auto-generated types
	pass
