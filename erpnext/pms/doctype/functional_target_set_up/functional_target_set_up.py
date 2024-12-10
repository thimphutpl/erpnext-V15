# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FunctionalTargetSetUp(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.pms.doctype.common_target_item.common_target_item import CommonTargetItem
		from erpnext.pms.doctype.negative_target.negative_target import NegativeTarget
		from frappe.types import DF

		amended_from: DF.Link | None
		approver: DF.Link | None
		approver_designation: DF.Data | None
		approver_name: DF.Data | None
		business_target: DF.Table[NegativeTarget]
		comment: DF.SmallText | None
		common_target: DF.Table[CommonTargetItem]
		company: DF.Link | None
		date: DF.Date | None
		division: DF.Link | None
		end_date: DF.Date | None
		manual_upload: DF.Check
		negative_target: DF.Check
		pms_calendar: DF.Link
		reason: DF.Data | None
		reference: DF.Link | None
		section: DF.Link | None
		set_manual_approver: DF.Check
		start_date: DF.Date | None
		type: DF.Literal["Tier I", "Tier II - Section", "Tier II - Unit"]
		unit: DF.Link | None
	# end: auto-generated types
	pass
