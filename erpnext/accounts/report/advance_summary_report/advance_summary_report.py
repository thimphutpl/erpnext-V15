# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate


COMPANY = "GYALSUNG INFRA"

ADVANCE_ACCOUNTS = (
	"A202022001 - Advance to Staff (Other) - GYALSUNG",
	"A202022002 - Advance to Staff (Salary) - GYALSUNG",
	"A202022003 - Advance to Staff (Travel) - GYALSUNG",
	"A202022004 - Advance to Supplier - GYALSUNG",
	"A202022005 - Mobilisation advance Paid - GYALSUNG",
	"A202022006 - Musterroll Advance - GYALSUNG",
	"L202030101 - Advance from Customer - GYALSUNG",
	"L202030102 - Advance from Other - GYALSUNG",
	"L202030107 - Mobilization advance Received - GYALSUNG",
)


def execute(filters=None):
	filters = frappe._dict(filters or {})

	filters.from_date = filters.get("from_date") or "2020-01-01"
	filters.to_date = filters.get("to_date") or nowdate()

	if getdate(filters.from_date) > getdate(filters.to_date):
		frappe.throw(_("Start Date cannot be greater than End Date"))

	columns = get_columns(filters)
	data = get_data(filters)
	add_total_row(data, filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"label": _("From Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("To Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Cost Center"),
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 180,
		},
		{
			"label": _("Party Type"),
			"fieldname": "party_type",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label": _("Party"),
			"fieldname": "party",
			"fieldtype": "Dynamic Link",
			"options": "party_type",
			"width": 180,
		},
	]

	
	if filters.get("party_type") != "Employee":
		columns.append({
			"label": _("Supplier Type"),
			"fieldname": "supplier_type",
			"fieldtype": "Data",
			"width": 140,
		})

	columns.extend([
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 260,
		},
		{
			"label": _("Advance Paid"),
			"fieldname": "advance_paid",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Advance Adjusted"),
			"fieldname": "advance_adjusted",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Advance Balance"),
			"fieldname": "advance_balance",
			"fieldtype": "Currency",
			"width": 150,
		},
	])

	return columns


def add_total_row(data, filters):
	if not data:
		return

	total_advance_paid = sum(row.get("advance_paid") or 0 for row in data)
	total_advance_adjusted = sum(row.get("advance_adjusted") or 0 for row in data)
	total_advance_balance = sum(row.get("advance_balance") or 0 for row in data)

	total_row = {
		"from_date": filters.from_date,
		"to_date": filters.to_date,
		"cost_center": "",
		"party_type": "",
		"party": "<b>Total</b>",
		"supplier_type": "",
		"account": "",
		"advance_paid": total_advance_paid,
		"advance_adjusted": total_advance_adjusted,
		"advance_balance": total_advance_balance,
	}

	data.append(total_row)	

def get_data(filters):
	conditions = [
		"gle.company = %(company)s",
		"gle.is_cancelled = 0",
		"gle.posting_date BETWEEN %(from_date)s AND %(to_date)s",
	]

	params = {
		"company": COMPANY,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
		"advance_accounts": ADVANCE_ACCOUNTS,
	}

	if filters.get("advance_account"):
		conditions.append("gle.account = %(advance_account)s")
		params["advance_account"] = filters.advance_account
	else:
		conditions.append("gle.account IN %(advance_accounts)s")

	if filters.get("cost_center"):
		conditions.append("gle.cost_center = %(cost_center)s")
		params["cost_center"] = filters.cost_center

	if filters.get("party_type"):
		conditions.append("gle.party_type = %(party_type)s")
		params["party_type"] = filters.party_type

	if filters.get("party"):
		conditions.append("gle.party = %(party)s")
		params["party"] = filters.party

	if filters.get("supplier_type") and filters.get("party_type") == "Supplier":
		conditions.append("s.supplier_type = %(supplier_type)s")
		params["supplier_type"] = filters.supplier_type

	where_clause = " AND ".join(conditions)

	return frappe.db.sql(
		f"""
		SELECT
			%(from_date)s AS from_date,
			%(to_date)s AS to_date,
			IFNULL(gle.cost_center, '') AS cost_center,
			IFNULL(gle.party_type, '') AS party_type,
			IFNULL(gle.party, '') AS party,
			IFNULL(s.supplier_type, '') AS supplier_type,
			gle.account AS account,
			SUM(gle.debit) AS advance_paid,
			SUM(gle.credit) AS advance_adjusted,
			SUM(gle.debit) - SUM(gle.credit) AS advance_balance
		FROM `tabGL Entry` gle
		LEFT JOIN `tabSupplier` s
			ON s.name = gle.party
			AND gle.party_type = 'Supplier'
		WHERE {where_clause}
		GROUP BY
			gle.cost_center,
			gle.party_type,
			gle.party,
			s.supplier_type,
			gle.account
		HAVING
			ROUND(advance_balance, 2) != 0
		ORDER BY
			gle.account,
			gle.party_type,
			gle.party,
			gle.cost_center
		""",
		params,
		as_dict=True,
	)