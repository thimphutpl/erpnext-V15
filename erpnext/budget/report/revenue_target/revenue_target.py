# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.utils import flt, formatdate
import frappe
from frappe import _
import calendar

from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	queries = construct_query(filters)
	data = get_data(queries,filters)
	
	chart = get_chart_data(filters, columns, data)
	
	return columns, data, None, chart

def get_columns(filters):
	columns = [
		{
			"fieldname": "cost_center",
			"label": "Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 200
		},
		{
			"fieldname": "account",
			"label": "Account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 200
		},
		{
			"fieldname": "account_number",
			"label": "Account Number",
			"fieldtype": "Data",
			"width": 120
		}
	]

	if filters.get('details') and filters.get('month') == 'All':
		for month in get_period_month_ranges("Monthly", filters["fiscal_year"]):
			for label in [
				_("%s") + " Target",
				_("%s") + " Achieved",
				_("%s") + " Balance",
				_("%s") + " Achieved Percent",
			]:
				label = label % str(month[0])[0:3]
				# frappe.throw(str(frappe.scrub(label)))
				columns.append(
					{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
				)

	if filters.get('details') and filters.get('month') != 'All':
		for label in [
			_("%s") + " Target",
			_("%s") + " Achieved",
			_("%s") + " Balance",
			_("%s") + " Achieved Percent",
		]:
			label = label % str(filters.get('month'))[0:3]
			# frappe.throw(str(frappe.scrub(label)))
			columns.append(
				{"label": label, "fieldtype": "Float", "fieldname": frappe.scrub(label), "width": 150}
			)
	else:
		columns += [{
				"fieldname": "target_amount",
				"label": "Target Total",
				"fieldtype": "Currency",
				"width": 160
			},
			{
				"fieldname": "achieved_amount",
				"label": "Total Achieved",
				"fieldtype": "Currency",
				"width": 160
			},
			{
				"fieldname": "balance_amount",
				"label": "Total Balance",
				"fieldtype": "Currency",
				"width": 160
			},
			{
				"fieldname": "achieved_percent",
				"label": "Total Achieved Percent",
				"fieldtype": "Percent",
				"width": 160
			}]

	return columns

def construct_query(filters=None):
	conditions, filters = get_conditions(filters)
	month_lower = filters.get("month").lower()

	query = ("""
			select 
				rta.*
			from `tabRevenue Target` rt, `tabRevenue Target Account` rta 
			where rta.parent = rt.name and rt.docstatus = 1 
			{conditions}
			""".format(month=month_lower, conditions=conditions))
	return query
	""" rta.cost_center as cost_center, rta.account as account, 
		  		rta.account_number as account_number,
		  		rta.{month} as monthly_amt """
	
def get_data(query, filters):
	data = []
	datas = frappe.db.sql(query, as_dict=True)

	# frappe.throw(f"{filters.get('details')} and here: {filters.get('month')}")
	if filters.get('details') and filters.get('month') != 'All':
		# frappe.throw(f"hello")
		month_name = filters.get("month")
		year = filters.get("fiscal_year")
		month_number = list(calendar.month_name).index(month_name.capitalize())
		_, end_day = calendar.monthrange(int(year), month_number)

		start_date = f"{year}-{month_number:02d}-01"
		end_date = f"{year}-{month_number:02d}-{end_day}"
	# elif filters.get('details'):
	# 	year = filters.get("fiscal_year")
	# 	start_date = f"{year}-01-01"
	# 	end_date = f"{year}-12-31"
	else:
		year = filters.get("fiscal_year")
		start_date = f"{year}-01-01"
		end_date = f"{year}-12-31"

	for d in datas:
		row = [d.cost_center, d.account, d.account_number]

		if filters.get('details') and filters.get('month') == 'All':
			# for month get_period_month_ranges("Monthly", filters["fiscal_year"]):
			for from_date, to_date in get_period_date_ranges('Monthly', filters.get("fiscal_year")):
				# frappe.throw(str(formatdate(from_date, format_string="MMMM")))
				month_name = str(formatdate(from_date, format_string="MMMM").lower())
				achieved_month = frappe.db.sql("""
					select
						ifnull(sum(gl.debit) - sum(gl.credit), 0) as achieved_amount
						from `tabGL Entry` as gl
						where gl.docstatus = 1
						and gl.posting_date between '{from_date}' and '{to_date}'
						and gl.cost_center = '{cost_center}'
						and gl.account ='{account}'
				""".format(from_date=from_date, to_date=to_date, cost_center=d.cost_center, account=d.account),as_dict=True)
				achieved_month_amt = achieved_month[0]['achieved_amount']

				achieved_percent_month, balance_amount_month = 0, 0
				balance_amount_month = flt(d[month_name]) - flt(abs(achieved_month_amt))
				if d[month_name] != 0:
					achieved_percent_month = (flt(achieved_month_amt) / flt(d[month_name])) * 100

				row += [flt(d[month_name]), abs(achieved_month_amt), flt(balance_amount_month), abs(achieved_percent_month)]
			
		achieved = frappe.db.sql("""
			select
				ifnull(sum(gl.debit) - sum(gl.credit), 0) as achieved_amount
				from `tabGL Entry` as gl
				where gl.docstatus = 1
				and gl.posting_date between '{from_date}' and '{to_date}'
				and gl.cost_center = '{cost_center}'
				and gl.account ='{account}'
			""".format(from_date=start_date, to_date=end_date, cost_center=d.cost_center, account=d.account),as_dict=True)
	
		achieved_amount = achieved[0]['achieved_amount']

		achieved_percent,target_amount = 0,0
		if filters.get('details') and filters.get('month') != 'All':
			month_val = filters.get('month').lower()
			balance_amount = flt(d[month_val]) - flt(abs(achieved_amount))
			target_amount = flt(d[month_val])
			if d[month_val] != 0:
				achieved_percent = (flt(achieved_amount) / flt(d[month_val])) * 100
		else:
			balance_amount = flt(d.target_amount) - flt(abs(achieved_amount))
			if d.target_amount != 0:
				achieved_percent = (flt(achieved_amount) / flt(d.target_amount)) * 100
			target_amount = flt(d.target_amount)
		
		# row = {
		# 	"cost_center": d.cost_center,
		# 	"account": d.account,
		# 	"account_number": d.account_number,
		# 	"target_amount": target_amount,
		# 	"achieved_amount": abs(achieved_amount),
		# 	"balance_amount": balance_amount,
		# 	"achieved_percent": abs(achieved_percent)
		# }
		row += [target_amount, abs(achieved_amount), balance_amount, abs(achieved_percent)]
		# frappe.throw("<pre>{}</pre>".format(frappe.as_json(row)))
		data.append(row)
	return data

def get_conditions(filters):
	# if not filters.get("details") and filters.get("month") != "All":
	# 	frappe.throw(f"set month filter to <b>All</b>")
	conditions = ""
	# if filters.get("month") != 'All':
	# 	conditions += """ and rta.{month} as monthly_amt""".format(month=filters.get("month").lower())
	if filters.get("cost_center"):
		conditions += """ and rta.cost_center ='{cost_center}'""".format(cost_center=filters.get("cost_center"))
	if filters.get("fiscal_year"):
		conditions += """ and rt.fiscal_year = '{year}'""".format(year=filters.get("fiscal_year"))

	return conditions, filters

def get_chart_data(filters, columns, data):
	if not data:
		return None

	labels = []

	if filters.get('details') and filters.get('month') == 'All':
		for month in get_period_month_ranges("Monthly", filters["fiscal_year"]):
			labels.append(str(month[0])[0:3])

	if filters.get('details') and filters.get('month') != 'All':
		labels.append(str(filters.get('month'))[0:3])
	else:
		labels.append(filters.get("fiscal_year"))

	no_of_columns = len(labels)

	target_values, achieved_values, balance_value, achieve_percent = [0] * no_of_columns, [0] * no_of_columns, [0] * no_of_columns, [0] * no_of_columns
	for d in data:
		values = d[3:]
		index = 0

		for i in range(no_of_columns):
			target_values[i] += values[index]
			achieved_values[i] += values[index + 1]
			balance_value[i] += values[index + 2]
			achieve_percent[i] += values[index + 3]
			index += 4

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Target"), "chartType": "bar", "values": target_values},
				{"name": _("Achieved"), "chartType": "bar", "values": achieved_values},
				{"name": _("Balace"), "chartType": "bar", "values": balance_value},
				{"name": _("Percent Achieved"), "chartType": "bar", "values": achieve_percent},
			],
		},
		"type": "bar",
	}
