# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days


class DailySales(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.model.document import Document
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Data | None
		daily_variation_amount: DF.Data | None
		daily_variation_litres: DF.Data | None
		data_mepz: DF.Data | None
		item_code: DF.Data | None
		item_name: DF.Data | None
		net_sales: DF.Data | None
		posting_date: DF.Date
		pump_test_quantity: DF.Data | None
		rate: DF.Data | None
		sales_dip_measurement_cm: DF.Data | None
		table_wyam: DF.Table[Document]
		total_amount_sold: DF.Data | None
		total_quantity_sold: DF.Data | None
		ug_tank_calibration: DF.Data | None
		ug_tank_list: DF.Link
		warehouse: DF.Data | None
	# end: auto-generated types
	def validate(self):
		pass

	@frappe.whitelist()
	def get_daily_sales_record(self):
		shifts_data= frappe.db.sql("""
			select shift, nozzle_1, nozzle_2, nozzle_3, nozzle_4, total_quantity_sold, total_amount, name, employee,  from `tabDaily Sales Record`
			where posting_date = '{}' and ug_tank = '{}'
			and docstatus = 1
		""".format(self.posting_date, self.ug_tank), as_dict=1)
		for sot in shifts_data:
			row = self.append("daily_sales_record", {})
			row.shift = sot.shift
			row.nozzle_1 = sot.nozzle_1
			row.nozzle_2 = sot.nozzle_2
			row.nozzle_3 = sot.nozzle_3
			row.nozzle_4 = sot.nozzle_4
			row.total_quantity_sold = sot.total_quantity_sold
			row.total_amount = sot.total_amount
			row.employee = sot.employee
			row.employee = sot.name
