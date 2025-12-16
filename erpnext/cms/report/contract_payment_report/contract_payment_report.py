# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

import frappe

def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": "Contract", "fieldname": "contract", "fieldtype": "Link", "options": "Contract Details", "width": 140},
		{"label": "Reference Number", "fieldname": "reference_number", "fieldtype": "Data", "width": 120},
		{"label": "Contract Name", "fieldname": "contract_name", "fieldtype": "Data", "width": 280},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},

		{"label": "Initial Amount", "fieldname": "initial_amount", "fieldtype": "Currency", "width": 130},
		{"label": "Discount", "fieldname": "discount", "fieldtype": "Currency", "width": 110},
		{"label": "Additional", "fieldname": "additional", "fieldtype": "Currency", "width": 120},
		{"label": "Final Amount", "fieldname": "final_amount", "fieldtype": "Currency", "width": 130},

		{"label": "Contract Start Date", "fieldname": "contract_start_date", "fieldtype": "Date", "width": 130},
		{"label": "Contract End Date", "fieldname": "contract_end_date", "fieldtype": "Date", "width": 130},

		{"label": "Focal Person", "fieldname": "focal_person", "fieldtype": "Link", "options": "Employee", "width": 120},

		{"label": "Payment Date", "fieldname": "payment_date", "fieldtype": "Date", "width": 120},
		{"label": "Currency", "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 90},
		{"label": "Bill Amount In Currency", "fieldname": "bill_amount_in_currency", "fieldtype": "Float", "width": 160},
		{"label": "Exchange Rate", "fieldname": "exchange_rate", "fieldtype": "Float", "width": 110},
		{"label": "Payable Amount In BTN", "fieldname": "payable_amount_in_btnn", "fieldtype": "Currency", "width": 170},

		{"label": "Payment Type", "fieldname": "payment_type", "fieldtype": "Data", "width": 120},
		{"label": "Payment", "fieldname": "payment", "fieldtype": "Float", "width": 90},

		{"label": "Payment ID", "fieldname": "payment_id", "fieldtype": "Link", "options": "Contract Payment", "width": 140},
	]

def get_data(filters):
	conditions = []
	values = {}

	if filters.get("contract"):
		conditions.append("cp.contract = %(contract)s")
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

	where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

	query = f"""
		SELECT
			cd.name AS contract,
			cd.reference_number AS reference_number,
			cd.contract_name AS contract_name,
			cd.supplier AS supplier,
			cd.initial_amount AS initial_amount,
			cd.discount AS discount,
			cd.additional AS additional,
			cd.final_amount AS final_amount,
			cd.start_date AS contract_start_date,
			cd.end_date AS contract_end_date,
			cd.focal_person_name AS focal_person,

			cp.payment_date AS payment_date,
			cp.currency AS currency,
			cp.bill_amount_in_currency AS bill_amount_in_currency,
			cp.exchange_rate AS exchange_rate,
			cp.payable_amount AS payable_amount_in_btnn,
			cp.payment_type AS payment_type,
			cp.payment AS payment,

			cp.name AS payment_id
		FROM `tabContract Payment` cp
		INNER JOIN `tabContract Details` cd
			ON cd.name = cp.contract
		{where_clause}
		ORDER BY cp.payment_date DESC, cp.name DESC
	"""

	return frappe.db.sql(query, values, as_dict=True)
