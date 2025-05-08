# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt, getdate

from erpnext.accounts.utils import get_balance_on


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()

	if not filters.get("account"):
		return columns, []

	account_currency = frappe.get_cached_value("Account", filters.account, "account_currency")

	data = get_entries(filters)

	balance_as_per_system = get_balance_on(filters["account"], filters["report_date"])

	total_debit, total_credit = 0, 0
	for d in data:
		total_debit += flt(d.debit)
		total_credit += flt(d.credit)

	amounts_not_reflected_in_system = get_amounts_not_reflected_in_system(filters)
	# frappe.throw(str(amounts_not_reflected_in_system))

	bank_bal = (
		flt(balance_as_per_system) - flt(total_debit) + flt(total_credit) + amounts_not_reflected_in_system
	)

	data += [
		get_balance_row(
			_("Bank Statement balance as per General Ledger"), balance_as_per_system, account_currency
		),
		{},
		{
			"payment_entry": _("Cheques issued but not encashed"),
			"debit": 0,
			"credit": total_credit,
			"account_currency": account_currency,
		},
		{
			"payment_entry": _("Cheques deposited but not cleared"),
			"debit": total_debit,
			"credit": 0,
			"account_currency": account_currency,
		},
		# get_balance_row(
		# 	_("Cheques and Deposits incorrectly cleared"), amounts_not_reflected_in_system, account_currency
		# ),
		{},
		get_balance_row(_("Balance as per Bank Statement"), bank_bal, account_currency),
	]
	return columns, data


def get_columns():
	return [
		{"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 90},
		{
			"fieldname": "payment_document",
			"label": _("Payment Document Type"),
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"fieldname": "payment_entry",
			"label": _("Payment Document"),
			"fieldtype": "Dynamic Link",
			"options": "payment_document",
			"width": 220,
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"options": "account_currency",
			"width": 120,
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"options": "account_currency",
			"width": 120,
		},
		{
			"fieldname": "against_account",
			"label": _("Against Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 200,
		},
		{"fieldname": "reference_no", "label": _("Reference"), "fieldtype": "Data", "width": 100},
		{"fieldname": "ref_date", "label": _("Ref Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "clearance_date", "label": _("Clearance Date"), "fieldtype": "Date", "width": 110},
		{
			"fieldname": "account_currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"width": 100,
		},
	]


def get_entries(filters):
	entries = []

	for method_name in frappe.get_hooks("get_entries_for_bank_reconciliation_statement"):
		entries += frappe.get_attr(method_name)(filters) or []

	return sorted(
		entries,
		key=lambda k: getdate(k["posting_date"]),
	)

def get_entries_for_bank_reconciliation_statement(filters):
    journal_entries = get_journal_entries(filters)
    payment_entries = get_payment_entries(filters)
    pos_entries = get_pos_entries(filters) if filters.get("include_pos_transactions") else []
    imprest_entries = get_imprest_recoup_entries(filters)  # New line
    
    return (
        list(journal_entries) 
        + list(payment_entries) 
        + list(pos_entries)
        + list(imprest_entries)
    )


def get_journal_entries(filters):
	return frappe.db.sql(
		"""
		select "Journal Entry" as payment_document, jv.posting_date,
			jv.name as payment_entry, jvd.debit_in_account_currency as debit,
			jvd.credit_in_account_currency as credit, jvd.against_account,
			jv.cheque_no as reference_no, jv.cheque_date as ref_date, jv.clearance_date, jvd.account_currency
		from
			`tabJournal Entry Account` jvd, `tabJournal Entry` jv
		where jvd.parent = jv.name and jv.docstatus=1
			and jvd.account = %(account)s and jv.posting_date <= %(report_date)s
			and ifnull(jv.clearance_date, '4000-01-01') > %(report_date)s
			and ifnull(jv.is_opening, 'No') = 'No'""",
		filters,
		as_dict=1,
	)

def get_imprest_recoup_entries(filters):
    return frappe.db.sql("""
        SELECT 
            'Imprest Recoup' AS payment_document,
            ir.posting_date AS posting_date,
            ir.name AS payment_entry,
            0 AS debit,  # Changed from total_amount
            ir.total_amount AS credit,  # Now in credit column
            ir.cheque_no AS reference_no,
            ir.cheque_date AS ref_date,
            NULL AS clearance_date,
            ir.remarks AS against_account,
            b.expense_bank_account AS against_account_number,
            (SELECT account_currency FROM `tabAccount` 
             WHERE name=%(account)s) AS account_currency
        FROM `tabImprest Recoup` ir
        INNER JOIN `tabBranch` b ON ir.branch = b.name
        WHERE
            ir.docstatus = 1
            AND ir.posting_date <= %(report_date)s
            AND b.expense_bank_account = %(account)s  # Ensure this is your BANK account
    """, filters, as_dict=1)


def get_payment_entries(filters):
	return frappe.db.sql(
		"""
		select
			"Payment Entry" as payment_document, name as payment_entry,
			reference_no, reference_date as ref_date,
			if(paid_to=%(account)s, received_amount, 0) as debit,
			if(paid_from=%(account)s, paid_amount, 0) as credit,
			posting_date, ifnull(party,if(paid_from=%(account)s,paid_to,paid_from)) as against_account, clearance_date,
			if(paid_to=%(account)s, paid_to_account_currency, paid_from_account_currency) as account_currency
		from `tabPayment Entry`
		where
			(paid_from=%(account)s or paid_to=%(account)s) and docstatus=1
			and posting_date <= %(report_date)s
			and ifnull(clearance_date, '4000-01-01') > %(report_date)s
	""",
		filters,
		as_dict=1,
	)


def get_pos_entries(filters):
	return frappe.db.sql(
		"""
			select
				"Sales Invoice Payment" as payment_document, sip.name as payment_entry, sip.amount as debit,
				si.posting_date, si.debit_to as against_account, sip.clearance_date,
				account.account_currency, 0 as credit
			from `tabSales Invoice Payment` sip, `tabSales Invoice` si, `tabAccount` account
			where
				sip.account=%(account)s and si.docstatus=1 and sip.parent = si.name
				and account.name = sip.account and si.posting_date <= %(report_date)s and
				ifnull(sip.clearance_date, '4000-01-01') > %(report_date)s
			order by
				si.posting_date ASC, si.name DESC
		""",
		filters,
		as_dict=1,
	)


def get_amounts_not_reflected_in_system(filters):
	amount = 0.0

	# get amounts from all the apps
	for method_name in frappe.get_hooks(
		"get_amounts_not_reflected_in_system_for_bank_reconciliation_statement"
	):
		amount += frappe.get_attr(method_name)(filters) or 0.0

	return amount


def get_amounts_not_reflected_in_system_for_bank_reconciliation_statement(filters):
	je_amount = frappe.db.sql(
		"""
		select sum(jvd.debit_in_account_currency - jvd.credit_in_account_currency)
		from `tabJournal Entry Account` jvd, `tabJournal Entry` jv
		where jvd.parent = jv.name and jv.docstatus=1 and jvd.account=%(account)s
		and jv.posting_date > %(report_date)s and jv.clearance_date <= %(report_date)s
		and ifnull(jv.is_opening, 'No') = 'No' """,
		filters,
	)

	je_amount = flt(je_amount[0][0]) if je_amount else 0.0

	pe_amount = frappe.db.sql(
		"""
		select sum(if(paid_from=%(account)s, paid_amount, received_amount))
		from `tabPayment Entry`
		where (paid_from=%(account)s or paid_to=%(account)s) and docstatus=1
		and posting_date > %(report_date)s and clearance_date <= %(report_date)s""",
		filters,
	)

	pe_amount = flt(pe_amount[0][0]) if pe_amount else 0.0

	return je_amount + pe_amount


def get_balance_row(label, amount, account_currency):
	if amount > 0:
		return {
			"payment_entry": label,
			"debit": amount,
			"credit": 0,
			"account_currency": account_currency,
		}
	else:
		return {
			"payment_entry": label,
			"debit": 0,
			"credit": abs(amount),
			"account_currency": account_currency,
		}
