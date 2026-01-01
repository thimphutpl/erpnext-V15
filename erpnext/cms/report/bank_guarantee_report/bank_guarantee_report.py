# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": "BG ID", "fieldname": "bg_id", "fieldtype": "Link", "options": "Bank Guarantee", "width": 140},

		{"label": "Contract", "fieldname": "contract", "fieldtype": "Link", "options": "Contract Details", "width": 140},
		{"label": "Reference Number", "fieldname": "reference_number", "fieldtype": "Data", "width": 120},
		{"label": "Contract Name", "fieldname": "contract_name", "fieldtype": "Data", "width": 280},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Supplier Type", "fieldname": "supplier_type", "fieldtype": "Data", "width": 140},
		{"label": "Focal Person", "fieldname": "focal_person", "fieldtype": "Link", "options": "Employee", "width": 120},
		{"label": "Contract Final Price", "fieldname": "contract_final_price", "fieldtype": "Currency", "width": 160},

		{"label": "BG Amount", "fieldname": "bg_amount", "fieldtype": "Currency", "width": 130},
		{"label": "BG Type", "fieldname": "bg_type", "fieldtype": "Data", "width": 120},
		{"label": "BG Number", "fieldname": "bg_number", "fieldtype": "Data", "width": 140},
		{"label": "BG Date", "fieldname": "bg_date", "fieldtype": "Date", "width": 110},
		{"label": "BG Expiry Date", "fieldname": "bg_expiry_date", "fieldtype": "Date", "width": 130},
		{"label": "Revised Expiry Date", "fieldname": "revised_expiry_date", "fieldtype": "Date", "width": 130},

	]


def get_data(filters):
	conditions = ["bg.docstatus = 0"]
	values = {}

	if filters.get("contract"):
		conditions.append("bg.contract = %(contract)s")
		values["contract"] = filters["contract"]

	if filters.get("reference_number"):
		conditions.append("cd.reference_number = %(reference_number)s")
		values["reference_number"] = filters["reference_number"]

	if filters.get("supplier"):
		conditions.append("cd.supplier = %(supplier)s")
		values["supplier"] = filters["supplier"]

	if filters.get("focal_person"):
		conditions.append("cd.focal_person = %(focal_person)s")
		values["focal_person"] = filters["focal_person"]

	where_clause = "WHERE " + " AND ".join(conditions)

	return frappe.db.sql(
		f"""
		SELECT
			bg.name AS bg_id,
			bg.contract AS contract,

			cd.reference_number AS reference_number,
			cd.contract_name AS contract_name,
			cd.supplier AS supplier,
			cd.supplier_type AS supplier_type,
			cd.focal_person AS focal_person,
			cd.final_amount AS contract_final_price,

			bg.bg_amount AS bg_amount,
			bg.bg_type AS bg_type,
			bg.bg_number AS bg_number,
			bg.bg_date AS bg_date,
			bg.bg_expiry_date AS bg_expiry_date,
			bg.revised_expiry_date AS revised_expiry_date

		FROM `tabBank Gurantee` bg
		INNER JOIN `tabContract Details` cd
			ON cd.name = bg.contract
		{where_clause}
		ORDER BY bg.bg_expiry_date DESC, bg.name DESC
		""",
		values,
		as_dict=True,
	)