# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Order
from frappe.utils import (
	add_days,
	add_months,
	add_years,
	cint,
	date_diff,
	flt,
	get_first_day,
	get_last_day,
	getdate,
	is_last_day_of_the_month,
	month_diff,
	nowdate,
	today,
	get_year_ending,
	get_year_start,
)

def execute(filters=None):
	columns = get_column(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
	month = str(int(months.index(filters.month))+1).rjust(2,"0")

	month_start_date = "-".join([str(filters.fiscal_year), month, "01"])
	month_end_date   = get_last_day(month_start_date)

	a = frappe.qb.DocType("Asset")
	ads = frappe.qb.DocType("Asset Depreciation Schedule")
	ds = frappe.qb.DocType("Depreciation Schedule")

	res = (
		frappe.qb.from_(ads)
		.join(a)
		.on(ads.asset == a.name)
		.join(ds)
		.on(ads.name == ds.parent)
		.select(a.name, a.asset_name, a.asset_category, a.asset_sub_category, a.cost_center, a.custodian_name, a.status)
		.where(a.calculate_depreciation == 1)
		.where(a.docstatus == 1)
		.where(a.disable_depreciation == 0)
		.where(ads.docstatus == 1)
		.where(a.status.isin(["Submitted", "Partially Depreciated"]))
		.where(ds.journal_entry.isnull())
		.where(ds.schedule_date == month_end_date)
		.groupby(ads.name)
		.orderby(a.asset_category, order=Order.desc)
	)

	# acc_frozen_upto = get_acc_frozen_upto()
	# if acc_frozen_upto:
	# 	res = res.where(ds.schedule_date > acc_frozen_upto)

	res = res.run()
	return res
	# frappe.throw("<pre>{}</pre>".format(frappe.as_json(res)))

def get_column(filters):
	return [
		{
			"fieldname": "asset",
			"label": "Asset",
			"fieldtype": "Link",
			"options": "Asset",
			"width": 200
		},
		{
			"fieldname": "asset_name",
			"label": "Asset Name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "asset_category",
			"label": "Asset Category",
			"fieldtype": "Data",
			"options": "",
			"width": 120,
		},
		{
			"fieldname": "asset_sub_category",
			"label": "Asset Sub Category",
			"fieldtype": "Data",
			"options": "",
			"width": 120,
		},
		{
			"fieldname": "cost_center",
			"label": "Cost Center",
			"fieldtype": "Data",
			"options": "",
			"width": 180,
		},
		{
			"fieldname": "custodian",
			"label": "Custodian",
			"fieldtype": "Data",
			"options": "",
			"width": 180,
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Data",
			"options": "",
			"width": 120,
		}
	]