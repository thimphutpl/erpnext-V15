# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Date


def execute(filters=None):
	columns, data = [], []

	validate_filters(filters)

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def validate_filters(filters):
	if not filters:
		frappe.throw(_("Please set filters"))

	for field in ["company", "date", "location"]:
		if not filters.get(field):
			frappe.throw(_("Please set {0}").format(field))


def get_data(filters):
	vpr = frappe.qb.DocType("Visitor Pass Registry")
	query = (
		frappe.qb.from_(vpr)
		.select(
			vpr.posting_date,
			vpr.location,
			vpr.total_amount,
			vpr.status,
		)
		.where(
			(vpr.docstatus != 2)
			& (vpr.company == filters.get("company"))
			& (Date(vpr.posting_date) == filters.get("date"))
		)
	)

	data = query.run(as_list=True)

	return data


def get_columns():
	columns = [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "location",
			"label": _("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"width": 140,
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120,
		},
	]

	return columns
