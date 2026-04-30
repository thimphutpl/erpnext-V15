# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_data(filters):
	conditions = get_conditions(filters)

	return frappe.db.sql("""
		SELECT
			t.item_code,
			i.item_name,
			i.asset_category,
			i.asset_sub_category,
			t.cost_center,
			t.received_qty AS total_qty,
			t.received_amount AS total_val,
			t.issued_qty,
			t.issued_amount AS issued_val,
			(t.received_qty - t.issued_qty) AS balance_qty,
			CASE
				WHEN t.received_qty > 0 THEN
					(t.received_qty - t.issued_qty) * (t.received_amount / t.received_qty)
				ELSE 0
			END AS balance_val,
			CASE
				WHEN (t.received_qty - t.issued_qty) > 0 THEN
					CONCAT(
						'<a href="desk#Form/Purchase Receipt/', t.ref_doc, '">',
						t.ref_doc, '(', (t.received_qty - t.issued_qty), ')</a>'
					)
				ELSE ''
			END AS purchase_receipt,
			"" AS existing_pr
		FROM (
			SELECT
				ar.name AS asset_received_entry,
				ar.item_code,
				ar.ref_doc,
				ar.cost_center,
				(
					SELECT pri.warehouse
					FROM `tabPurchase Receipt Item` pri
					WHERE pri.name = ar.child_ref
					LIMIT 1
				) AS warehouse,
				SUM(ar.qty) AS received_qty,
				SUM(
					(
						SELECT pri.base_net_amount
						FROM `tabPurchase Receipt Item` pri
						JOIN `tabPurchase Receipt` pr
							ON pr.name = pri.parent
						WHERE pri.name = ar.child_ref
						AND pr.branch = ar.branch
						LIMIT 1
					)
				) AS received_amount,
				IFNULL((
					SELECT SUM(ai.qty)
					FROM `tabAsset Issue Details` ai
					WHERE ai.item_code = ar.item_code
					AND ai.asset_received_entries = ar.name
					AND ai.docstatus = 1
					AND ai.is_existing_asset = 0
					AND ai.issued_date BETWEEN '{from_date}' AND '{to_date}'
				), 0) AS issued_qty,
				IFNULL((
					SELECT SUM(ai.amount)
					FROM `tabAsset Issue Details` ai
					WHERE ai.item_code = ar.item_code
					AND ai.asset_received_entries = ar.name
					AND ai.docstatus = 1
					AND ai.is_existing_asset = 0
					AND ai.issued_date BETWEEN '{from_date}' AND '{to_date}'
				), 0) AS issued_amount
			FROM `tabAsset Received Entries` ar
			WHERE ar.received_date BETWEEN '{from_date}' AND '{to_date}'
			AND ar.docstatus = 1
			AND ar.is_existing_asset = 0
			{cond}
			GROUP BY ar.name, ar.item_code, ar.ref_doc, ar.cost_center, ar.branch
		) AS t
		JOIN `tabItem` i ON i.name = t.item_code

		UNION ALL

		SELECT
			t.item_code,
			i.item_name,
			i.asset_category,
			i.asset_sub_category,
			t.cost_center,
			t.received_qty AS total_qty,
			t.received_amount AS total_val,
			t.issued_qty,
			t.issued_amount AS issued_val,
			(t.received_qty - t.issued_qty) AS balance_qty,
			CASE
				WHEN t.received_qty > 0 THEN
					(t.received_qty - t.issued_qty) * (t.received_amount / t.received_qty)
				ELSE 0
			END AS balance_val,
			"" AS purchase_receipt,
			CASE
				WHEN (t.received_qty - t.issued_qty) > 0 THEN t.existing_pr
				ELSE ''
			END AS existing_pr
		FROM (
			SELECT
				ar.name AS asset_received_entry,
				ar.item_code,
				ar.ref_doc,
				ar.existing_pr_reference AS existing_pr,
				ar.cost_center,
				ar.warehouse,
				SUM(ar.qty) AS received_qty,
				SUM(ar.asset_rate * ar.qty) AS received_amount,
				IFNULL((
					SELECT SUM(ai.qty)
					FROM `tabAsset Issue Details` ai
					WHERE ai.item_code = ar.item_code
					AND ai.branch = ar.branch
					AND ai.asset_received_entries = ar.name
					AND ai.docstatus = 1
					AND ai.is_existing_asset = 1
					AND ai.issued_date BETWEEN '{from_date}' AND '{to_date}'
				), 0) AS issued_qty,
				IFNULL((
					SELECT SUM(ai.amount)
					FROM `tabAsset Issue Details` ai
					WHERE ai.item_code = ar.item_code
					AND ai.branch = ar.branch
					AND ai.asset_received_entries = ar.name
					AND ai.docstatus = 1
					AND ai.is_existing_asset = 1
					AND ai.issued_date BETWEEN '{from_date}' AND '{to_date}'
				), 0) AS issued_amount
			FROM `tabAsset Received Entries` ar
			WHERE ar.received_date BETWEEN '{from_date}' AND '{to_date}'
			AND ar.docstatus = 1
			AND ar.is_existing_asset = 1
			{cond}
			GROUP BY ar.name, ar.item_code, ar.ref_doc, ar.existing_pr_reference, ar.cost_center, ar.warehouse, ar.branch
		) AS t
		JOIN `tabItem` i ON i.name = t.item_code

		ORDER BY item_code, cost_center, purchase_receipt, existing_pr
	""".format(
		from_date=filters.get("from_date"),
		to_date=filters.get("to_date"),
		cond=conditions
	), as_dict=True)

def get_conditions(filters):
	if not filters.get("from_date"):
		frappe.throw(_("From Date is mandatory"))
	elif not filters.get("to_date"):
		frappe.throw(_("To Date is mandatory"))
		
	conditions = ""
	if filters.get("branch"):
		conditions += ' and ar.branch = "{}"'.format(filters.get("branch"))
	return conditions

def get_columns():
	return [
		{
		  "fieldname": "item_code",
		  "label": "Material Code",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "item_name",
		  "label": "Material Name",
		  "fieldtype": "Data",
		  "width": 200
		},
		{
		  "fieldname": "asset_category",
		  "label": "Asset Category",
		  "fieldtype": "Link",
		  "options": "Asset Category",
		  "width": 200
		},
		{
		  "fieldname": "asset_sub_category",
		  "label": "Asset Sub Category",
		  "fieldtype": "Data",
		  "width": 200
		},
		{
		  "fieldname": "cost_center",
		  "label": "Cost Center",
		  "fieldtype": "Link",
		  "options": "Cost Center",
		  "width": 200
		},
		{
		  "fieldname": "total_qty",
		  "label": "Total Quantity",
		  "fieldtype": "Int",
		  "width": 120
		},
		{
		  "fieldname": "total_val",
		  "label": "Total Value",
		  "fieldtype": "Currency",
		  "width": 120
		},
		{
		  "fieldname": "issued_qty",
		  "label": "Issued Quantity",
		  "fieldtype": "Int",
		  "width": 120
		},
		{
		  "fieldname": "issued_val",
		  "label": "Issued Value",
		  "fieldtype": "Currency",
		  "width": 120
		},
		{
		  "fieldname": "balance_qty",
		  "label": "Balance Quantity",
		  "fieldtype": "Int",
		  "width": 120
		},
		{
		  "fieldname": "balance_val",
		  "label": "Balance Value",
		  "fieldtype": "Currency",
		  "width": 120
		},
		{
			"fieldname": "purchase_receipt",
			"label": "Purchase Receipt",
			"fieldtype": "Data",
			"options": "Purchase Receipt",
			"width": 500
		},
		{
			"fieldname": "existing_pr",
			"label": "Existing PR Reference",
			"fieldtype": "Data",
			"width": 200
		}
	]

