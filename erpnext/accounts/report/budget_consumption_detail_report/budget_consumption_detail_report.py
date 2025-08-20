# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint
from erpnext.accounts.report.financial_statements_cdcl  import (get_period_list, get_columns, get_data)

def execute(filters=None):
	if filters.periodicity != "Yearly":
		frappe.throw("{} report for this report not applicable.".format(filters.periodicity))
	if filters.show_zero_values:
		show_zero = 1
	else:
		show_zero = 0
	if filters.from_fiscal_year > filters.to_fiscal_year:
		frappe.throw("From Fiscal Year Cannot Be Greater Than To Fiscal Year")
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, filters.company)

	budget = get_budget_data(filters.cost_center, filters.company, filters.from_fiscal_year, filters.to_fiscal_year)
	income = get_data(filters.cost_center, filters.company, "Income", "Credit", period_list,
		accumulated_values=filters.accumulated_values, ignore_closing_entries=True, show_zero_values=show_zero, project=filters.project)
	expense = get_data(filters.cost_center, filters.company, "Expense", "Debit", period_list,
		accumulated_values=filters.accumulated_values, ignore_closing_entries=True, show_zero_values=show_zero, project=filters.project)
	net_profit_loss = get_net_profit_loss(budget, income, expense, period_list, filters.company)
	# frappe.throw(str(budget))
	data = []
	data.append(budget or [])
	data.extend(income or [])
	data.extend(expense or [])
	if net_profit_loss:
		data.append(net_profit_loss)

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)

	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

	return columns, data, None, chart

def get_budget_data(cost_center, company, from_fiscal_year, to_fiscal_year):
	fiscal_years = []
	budget_data = {
		"account_name": "'" + _("Budget Allocated") + "'",
		"account": None,
		"warn_if_negative": True,
		"currency": frappe.db.get_value("Company", company, "default_currency"),
		"total": 0
	}
	total = 0
	if from_fiscal_year and to_fiscal_year:
		if not cost_center:
			for year in range(cint(from_fiscal_year), cint(to_fiscal_year)+1):
				bud = frappe.db.sql("""
					select sum(ifnull(ccb.estimated_budget,0)) as budget from `tabCost Center Budget` ccb, `tabCost Center` cc where ccb.parent = cc.name and cc.disabled = 0
					and ccb.fiscal_year = '{}' 
				""".format(year), as_dict=1)
				if bud[0].budget:
					bud = bud[0].budget
				else:
					bud = 0
				budget_data["dec_"+str(year)] = flt(bud,2)
				total += flt(bud,2)
		else:
			for year in frappe.range(from_fiscal_year, cint(to_fiscal_year)+1):
				bud = frappe.db.sql("""
					select sum(ifnull(ccb.estimated_budget,0)) as budget from `tabCost Center Budget` ccb, `tabCost Center` cc where ccb.parent = cc.name and cc.disabled = 0
					and cc.fiscal_year = '{}' and cc.parent = '{}'
				""".format(year, cost_center), as_dict=1)
				if bud[0].budget:
					bud = bud[0].budget
				else:
					bud = 0
				budget_data["dec_"+str(year)] = flt(bud,2)
				total += flt(bud,2)
		budget_data["total"] = total
		return budget_data

def get_net_profit_loss(budget, income, expense, period_list, company):
	if income and expense:
		total = 0
		net_profit_loss = {
			"account_name": "'" + _("Net Profit / Loss") + "'",
			"account": None,
			"warn_if_negative": True,
			"currency": frappe.db.get_value("Company", company, "default_currency")
		}

		has_value = False
		# frappe.throw(str(income)+" <br><br> "+str(expense))
		for period in period_list:
			net_profit_loss[period.key] = flt(budget[period.key])-flt(expense[0]['total'] - income[0]['total'] , 3)

			if net_profit_loss[period.key]:
				has_value=True

			total += flt(net_profit_loss[period.key])
			net_profit_loss["total"] = total

		if has_value:
			return net_profit_loss

def get_chart_data(filters, columns, income, expense, net_profit_loss):
	x_intervals = ['x'] + [d.get("label") for d in columns[2:-1]]

	income_data, expense_data, net_profit = [], [], []
	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	columns = [x_intervals]
	if income_data:
		columns.append(["Income"] + income_data)
	if expense_data:
		columns.append(["Expense"] + expense_data)
	if net_profit:
		columns.append(["Net Profit/Loss"] + net_profit)

	chart = {
		"data": {
			'x': 'x',
			'columns': columns
		}
	}

	if not filters.accumulated_values:
		chart["chart_type"] = "bar"

	return chart
