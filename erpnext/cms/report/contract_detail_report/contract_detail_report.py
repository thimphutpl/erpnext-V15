# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	filters = filters or {}

	columns = get_columns()
	data = get_data(filters)
	append_totals_row(data)

	return columns, data

def append_totals_row(data):
	if not data:
		return
	total_initial = sum(flt(d.get("initial_amount")) for d in data)
	total_discount = sum(flt(d.get("discount")) for d in data)
	total_additional = sum(flt(d.get("additional")) for d in data)
	total_final = sum(flt(d.get("final_amount")) for d in data)
	negotiation_amount = sum(flt(d.get("negotiation_amount")) for d in data)
	actual_amount = sum(flt(d.get("actual_amount")) for d in data)

	data.append({
		"defect_liability_amount": "<b>Total</b>",
		"initial_amount": total_initial,
		"discount": total_discount,
		"additional": total_additional,
		"final_amount": total_final,
		"negotiation_amount": negotiation_amount,
		"actual_amount": actual_amount,
	})


def get_columns():
	return [
		{"label": "Contract", "fieldname": "name", "fieldtype": "Link", "options": "Contract Details", "width": 160},

		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Supplier Name", "fieldname": "supplier_name", "fieldtype": "Data", "width": 200},
		{"label": "Supplier Type", "fieldname": "supplier_type", "fieldtype": "Data", "width": 140},


		{"label": "Contract Name", "fieldname": "contract_name", "fieldtype": "Data", "width": 220},
		{"label": "Contract Ref Number", "fieldname": "reference_number", "fieldtype": "Data", "width": 140},
		{"label": "Types of Contract", "fieldname": "types_of_contract", "fieldtype": "Data", "width": 150},

		{"label": "Currency", "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 90},

		{"label": "Offer Amount", "fieldname": "initial_amount", "fieldtype": "Currency", "width": 140},
		{"label": "Discount", "fieldname": "discount", "fieldtype": "Currency", "width": 120},
		{"label": "Additional", "fieldname": "additional", "fieldtype": "Currency", "width": 120},
		{"label": "Negotiation Amount", "fieldname": "negotiation_amount", "fieldtype": "Currency", "width": 160},
		{"label": "Contract Amount", "fieldname": "final_amount", "fieldtype": "Currency", "width": 140},

		{"label": "Actual Amount", "fieldname": "actual_amount", "fieldtype": "Currency", "width": 140},

		{"label": "Contract Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 120},
		{"label": "Contract End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 120},
		{"label": "Revised Expiry Date", "fieldname": "revised_expiry_date", "fieldtype": "Date", "width": 140},
		{"label": "Actual Completion Date", "fieldname": "actual_completion_date", "fieldtype": "Date", "width": 140},

		{"label": "Delay (Days)", "fieldname": "delay_days", "fieldtype": "Int", "width": 110},

		{"label": "Defect Liability Period", "fieldname": "defect_liability_amount", "fieldtype": "Data", "width": 170},

		
		{"label": "Focal Person", "fieldname": "focal_person", "fieldtype": "Link", "options": "Employee", "width": 140},
		{"label": "Focal Person Name", "fieldname": "focal_person_name", "fieldtype": "Data", "width": 180},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},

	]


def get_data(filters):
	conditions = []
	values = {}

	# JS filter: contract
	if filters.get("contract"):
		conditions.append("name = %(contract)s")
		values["contract"] = filters["contract"]

	# JS filter: status
	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters["status"]

	where_clause = ""
	if conditions:
		where_clause = "WHERE " + " AND ".join(conditions)

	return frappe.db.sql(
		f"""
		SELECT
			name,
			supplier,
			supplier_name,
			supplier_type,
			status,
			contract_name,
			reference_number,
			start_date,
			end_date,
			revised_expiry_date,
			actual_completion_date,
			delay_days,
			types_of_contract,
			defect_liability_amount,
			currency,
			initial_amount,
			final_amount,
			discount,
			additional,
			negotiation_amount,
			actual_amount,
			focal_person,
			focal_person_name
		FROM `tabContract Details`
		{where_clause}
		ORDER BY modified DESC
		""",
		values,
		as_dict=True
	)
