# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FabricationAndBaileyBridge(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link
		cost_center: DF.Link
		customer: DF.Link | None
		customer_branch: DF.ReadOnly | None
		customer_cost_center: DF.ReadOnly | None
		dispatch_number: DF.Data | None
		equipment_model: DF.Link | None
		equipment_number: DF.Data | None
		equipmment: DF.Link | None
		finish_date: DF.Date | None
		job_in_time: DF.Time | None
		job_out_time: DF.Time | None
		owned_by: DF.Data | None
		posting_date: DF.Date | None
		ref_number: DF.Data | None
		repair_type: DF.Literal["", "Fabrication Works", "Bailey Bridge Works"]
	# end: auto-generated types
	pass
