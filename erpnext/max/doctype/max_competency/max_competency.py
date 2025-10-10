# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MaxCompetency(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.max.doctype.competency_master_item.competency_master_item import CompetencyMasterItem
		from frappe.types import DF

		pms_group: DF.Link | None
		table_hpjh: DF.Table[CompetencyMasterItem]
	# end: auto-generated types
	pass
