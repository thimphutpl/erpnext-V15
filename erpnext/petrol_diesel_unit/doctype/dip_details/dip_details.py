# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DipDetails(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		a_i: DF.Float
		a_ii: DF.Float
		a_iii: DF.Float
		a_iv: DF.Float
		a_total: DF.Float
		a_v: DF.Float
		a_vi: DF.Float
		c_i: DF.Float
		c_ii: DF.Float
		c_iii: DF.Float
		c_iv: DF.Float
		c_total: DF.Float
		c_v: DF.Float
		c_vi: DF.Float
		cost_center: DF.Link
		density_as_per_invoice: DF.Float
		ld_combined: DF.Float
		ld_i: DF.Float
		ld_ii: DF.Float
		ld_iii: DF.Float
		ld_iv: DF.Float
		ld_v: DF.Float
		ld_vi: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rd_combined: DF.Float
		rd_i: DF.Float
		rd_ii: DF.Float
		rd_iii: DF.Float
		rd_iv: DF.Float
		rd_v: DF.Float
		rd_vi: DF.Float
		variance_in_amount: DF.Currency
		variance_in_dip: DF.Float
		variance_in_litres: DF.Float
	# end: auto-generated types
	pass
