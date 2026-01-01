# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

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
	advance = sum(flt(d.get("advance")) for d in data)
	tds = sum(flt(d.get("tds")) for d in data)
	retention_money = sum(flt(d.get("retention_money")) for d in data)
	ld = sum(flt(d.get("ld")) for d in data)
	total_deduction = sum(flt(d.get("total_deduction")) for d in data)
	net_amount_payable = sum(flt(d.get("net_amount_payable")) for d in data)
	negotiation_amount = sum(flt(d.get("negotiation_amount")) for d in data)
	bill_amount_in_currency = sum(flt(d.get("bill_amount_in_currency")) for d in data)
	payable_amount_in_btnn = sum(flt(d.get("payable_amount_in_btnn")) for d in data)

	data.append({
		"types_of_contract": "<b>Total</b>",
		"initial_amount": total_initial,
		"discount": total_discount,
		"additional": total_additional,
		"final_amount": total_final,
		"advance": advance,
		"tds": tds,
		"retention_money": retention_money,
		"ld": ld,
		"total_deduction": total_deduction,
		"net_amount_payable": net_amount_payable,
		"negotiation_amount": negotiation_amount,
		"bill_amount_in_currency": bill_amount_in_currency,
		"payable_amount_in_btnn": payable_amount_in_btnn,
	})

def get_columns():
	return [
		{"label": "Contract", "fieldname": "contract", "fieldtype": "Link", "options": "Contract Details", "width": 140},
		{"label": "Reference Number", "fieldname": "reference_number", "fieldtype": "Data", "width": 120},
		{"label": "Contract Name", "fieldname": "contract_name", "fieldtype": "Data", "width": 280},
		{"label": "Supplier", "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
		{"label": "Types of Contract", "fieldname": "types_of_contract", "fieldtype": "Data", "width": 120},

		{"label": "Offer Amount", "fieldname": "initial_amount", "fieldtype": "Currency", "width": 130},
		{"label": "Discount", "fieldname": "discount", "fieldtype": "Currency", "width": 110},
		{"label": "Additional", "fieldname": "additional", "fieldtype": "Currency", "width": 120},
		{"label": "Negotiation Amount", "fieldname": "negotiation_amount", "fieldtype": "Currency", "width": 120},


		{"label": "Contract Amount", "fieldname": "final_amount", "fieldtype": "Currency", "width": 130},

		{"label": "Contract Start Date", "fieldname": "contract_start_date", "fieldtype": "Date", "width": 130},
		{"label": "Contract End Date", "fieldname": "contract_end_date", "fieldtype": "Date", "width": 130},
		{"label": "Revised Expiry Date", "fieldname": "revised_expiry_date", "fieldtype": "Date", "width": 120},

		{"label": "Focal Person", "fieldname": "focal_person", "fieldtype": "Link", "options": "Employee", "width": 120},

		{"label": "Payment Date", "fieldname": "payment_date", "fieldtype": "Date", "width": 120},
		{"label": "Currency", "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 90},
		{"label": "Bill Amount In Currency", "fieldname": "bill_amount_in_currency", "fieldtype": "Float", "width": 160},
		{"label": "Exchange Rate", "fieldname": "exchange_rate", "fieldtype": "Float", "width": 110},
		{"label": "Payable Amount In BTN", "fieldname": "payable_amount_in_btnn", "fieldtype": "Currency", "width": 170},
		{"label": "Payment Number", "fieldname": "payment", "fieldtype": "Float", "width": 90},

		{"label": "Payment Type", "fieldname": "payment_type", "fieldtype": "Data", "width": 120},
		{"label": "Advance", "fieldname": "advance", "fieldtype": "Float", "width": 90},
		{"label": "TDS", "fieldname": "tds", "fieldtype": "Float", "width": 90},
		{"label": "Retention Money", "fieldname": "retention_money", "fieldtype": "Float", "width": 130},
		{"label": "LD", "fieldname": "ld", "fieldtype": "Float", "width": 90},
		{"label": "Total Deduction", "fieldname": "total_deduction", "fieldtype": "Float", "width": 130},
		{"label": "Net Amount Payable", "fieldname": "net_amount_payable", "fieldtype": "Currency", "width": 150},


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
			cd.revised_expiry_date AS revised_expiry_date,
			cd.focal_person_name AS focal_person,
			cd.negotiation_amount AS negotiation_amount,
			cd.types_of_contract AS types_of_contract,		

			cp.payment_date AS payment_date,
			cp.currency AS currency,
			cp.bill_amount_in_currency AS bill_amount_in_currency,
			cp.exchange_rate AS exchange_rate,
			cp.payable_amount AS payable_amount_in_btnn,
			cp.payment_type AS payment_type,
			cp.advance AS advance,
			cp.tds AS tds,
			cp.retention_money AS retention_money,
			cp.ld AS ld,
			cp.total_deduction AS total_deduction,
			cp.net_amount_payable AS net_amount_payable,
			cp.payment AS payment,

			cp.name AS payment_id
		FROM `tabContract Payment` cp
		INNER JOIN `tabContract Details` cd
			ON cd.name = cp.contract
		{where_clause}
		ORDER BY cp.payment_date DESC, cp.name DESC
	"""

	return frappe.db.sql(query, values, as_dict=True)
