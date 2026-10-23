# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if filters.payment_type == "Bank Payment":
		columns, data = get_column(), get_data(filters)
	else:
		columns, data = get_utility_column(), get_utility_data(filters)
	return columns, data

def get_column():
	columns = [
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 100
		},
		{
			"label": _("Transaction"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Bank Payment",
			"width": 100
		},
		{
			"label": _("Transaction Type"),
			"fieldname": "transaction_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Transaction ID"),
			"fieldname": "transaction_id",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Transaction Date"),
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Party Type"),
			"fieldname": "party_type",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Party"),
			"fieldname": "party",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Beneficiary Name"),
			"fieldname": "beneficiary_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Beneficiary Bank Acc No."),
			"fieldname": "bank_account_no",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Total Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Journal No."),
			"fieldname": "bank_journal_no",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("PI Number"),
			"fieldname": "pi_number",
			"fieldtype": "Data",
			"width": 100
		}
	]

    
	return columns

def get_data(filters):
    cond = get_condition(filters)

    data = frappe.db.sql("""
        SELECT 
            bp.company AS company,
            bp.name AS transaction,
            bpi.transaction_type AS transaction_type,
            bpi.transaction_id AS transaction_id,
            bpi.transaction_date AS transaction_date,
            bpi.party_type AS party_type,
            CASE
                WHEN bpi.party_type = 'Supplier' THEN bpi.supplier
                WHEN bpi.party_type = 'Employee' THEN bpi.employee
                WHEN bpi.party_type = 'Customer' THEN bpi.customer
                ELSE COALESCE(bpi.supplier, bpi.employee, bpi.customer)
            END AS party,
            bpi.beneficiary_name AS beneficiary_name,
            bpi.bank_account_no AS bank_account_no,
            bpi.amount AS amount,
            bpi.status AS status,
            bpi.bank_journal_no AS bank_journal_no,
            bpi.pi_number AS pi_number
        FROM `tabBank Payment` bp
        INNER JOIN `tabBank Payment Item` bpi
            ON bp.name = bpi.parent
        {condition}
    """.format(condition=cond), as_dict=True)

    return data

def get_utility_column():
	columns = [
		("Company") + ":Link/Company:100",
		("Utility Service Type") + ":Data:150",
		("Party") + ":Data:150",
		("Branch Expense Account") + ":Data:200",
		("Paid From Bank Account") + ":Data:200",
		("Debit Account") + ":Link/Account:200",
		("Unique Identity Code") + ":Data:100",
		("Outstanding Amount") + ":Data:100",
		("Payment Status") + ":Data:100",
		("Payment API Response") + ":Data:400",
		("Create Direct Payment") + ":Check:100",
		("TDS Applicable") + ":Check:100",
		("PI Number")
	]
	return columns

def get_utility_data(filters):
	cond = get_condition(filters)
	data = frappe.db.sql("""
		SELECT 
			ut.company as company,
			uti.utility_service_type, 
			uti.party, 
			ut.expense_account, 
			ut.bank_account, 
			uti.debit_account, 
			uti.consumer_code, 
			uti.outstanding_amount, 
			uti.payment_status, 
			uti.payment_response_msg, 
			uti.create_direct_payment, 
			uti.tds_applicable, 
			uti.pi_number
		FROM `tabUtility Bill` ut, `tabUtility Bill Item` uti 
		WHERE ut.name=uti.parent
		{condition}
	""".format(condition=cond))
	return data

# def get_condition(filters):
# 	conds = ""
# 	if filters.payment_type == "Bank Payment":
# 		if filters.transaction_type:
# 			conds += "and bpi.transaction_type='{}'".format(filters.transaction_type)
# 		if filters.party_type:
# 			conds += "and bpi.party_type='{}'".format(filters.party_type)
			
# 		if filters.party:
# 			parties = filters.party

# 			if isinstance(parties, str):
# 				parties = [parties]

# 			party_list = ", ".join(
# 				frappe.db.escape(party) for party in parties
# 			)

# 			conds += " and bpi.supplier IN ({})".format(party_list)
# 		if filters.status:
# 			conds += "and bpi.status='{}'".format(filters.status)
# 	return conds
def get_condition(filters):
	conds = ""

	if filters.payment_type == "Bank Payment":

		if filters.transaction_type:
			conds += " AND bpi.transaction_type = {}".format(
				frappe.db.escape(filters.transaction_type)
			)

		if filters.party_type:
			conds += " AND bpi.party_type = {}".format(
				frappe.db.escape(filters.party_type)
			)
		if filters.company:
			conds += " AND bp.company = {}".format(
				frappe.db.escape(filters.company)
			)
		if filters.from_date:
			conds += " AND bpi.transaction_date >= {}".format(
				frappe.db.escape(filters.from_date)
			)
		if filters.to_date:
			conds += " AND bpi.transaction_date <= {}".format(
				frappe.db.escape(filters.to_date)
			)


		if filters.party:
			parties = filters.party

			if isinstance(parties, str):
				parties = [parties]

			party_list = ", ".join(
				frappe.db.escape(party)
				for party in parties
			)

			if filters.party_type == "Supplier":
				conds += " AND bpi.supplier IN ({})".format(party_list)

			elif filters.party_type == "Employee":
				conds += " AND bpi.employee IN ({})".format(party_list)

			elif filters.party_type == "Customer":
				conds += " AND bpi.customer IN ({})".format(party_list)


		if filters.status:
			conds += " AND bpi.status = {}".format(
				frappe.db.escape(filters.status)
			)

	return conds