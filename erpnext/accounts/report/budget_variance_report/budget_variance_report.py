

# # Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# # License: GNU General Public License v3. See license.txt


# import datetime

# import frappe
# from frappe import _
# from frappe.utils import flt, formatdate

# from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges


# def execute(filters=None):
# 	if not filters:
# 		filters = {}

# 	columns = get_columns(filters)
# 	if filters.get("budget_against_filter"):
# 		dimensions = filters.get("budget_against_filter")
# 	else:
# 		dimensions = get_cost_centers(filters)

# 	period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
# 	cam_map = get_dimension_account_month_map(filters)

# 	data = []
# 	for dimension in dimensions:
# 		dimension_items = cam_map.get(dimension)
# 		if dimension_items:
# 			data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, 0)

# 	chart = get_chart_data(filters, columns, data)

# 	return columns, data, None, chart


# def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation):
#     for account, monthwise_data in dimension_items.items():
#         row = [dimension, account]
#         totals = [0, 0, 0, ""]  # budget, actual, variance, variance% (as string)
        
#         for year in get_fiscal_years(filters):
#             last_total = 0
#             for relevant_months in period_month_ranges:
#                 period_data = [0, 0, 0, ""]  # budget, actual, variance, variance% (as string)
                
#                 for month in relevant_months:
#                     if monthwise_data.get(year[0]):
#                         month_data = monthwise_data.get(year[0]).get(month, {})
#                         for i, fieldname in enumerate(["target", "actual", "variance"]):
#                             value = flt(month_data.get(fieldname))
#                             period_data[i] += value
#                             if i < 3:  # Don't add to totals for the percentage string
#                                 totals[i] += value

#                 period_data[0] += last_total

#                 if DCC_allocation:
#                     period_data[0] = period_data[0] * (DCC_allocation / 100)
#                     period_data[1] = period_data[1] * (DCC_allocation / 100)

#                 if filters.get("show_cumulative"):
#                     last_total = period_data[0] - period_data[1]

#                 period_data[2] = period_data[0] - period_data[1]
                
#                 # Calculate and format variance percentage with 3 decimal points
#                 if period_data[0] != 0:
#                     if period_data[0] > 0:
#                         variance_pct = flt((period_data[2] / period_data[0]) * 100, 3)
#                     else:
#                         variance_pct = flt((period_data[2] / abs(period_data[0])) * 100, 3)
#                     variance_pct = max(-100, min(100, variance_pct))
#                     period_data[3] = f"{variance_pct}%"
#                 else:
#                     period_data[3] = "0.000%"
                
#                 # row += period_data
#                 row += [round(period_data[i], 3) if isinstance(period_data[i], float) else period_data[i] for i in range(len(period_data))]
        
#         # Calculate and format total variance percentage with 3 decimal points
#         totals[2] = totals[0] - totals[1]
#         if totals[0] != 0:
#             if totals[0] > 0:
#                 total_variance_pct = flt((totals[2] / totals[0]) * 100, 3)
#             else:
#                 total_variance_pct = flt((totals[2] / abs(totals[0])) * 100, 3)
#             total_variance_pct = max(-100, min(100, total_variance_pct))
#             totals[3] = f"{total_variance_pct}%"
#         else:
#             totals[3] = "0.000%"
        
#         if filters["period"] != "Yearly":
#             row += totals
#         data.append(row)

#     return data

# def get_columns(filters):
#     columns = [
#         {
#             "label": _(filters.get("budget_against")),
#             "fieldtype": "Link",
#             "fieldname": "budget_against",
#             "options": filters.get("budget_against"),
#             "width": 150,
#         },
#         {
#             "label": _("Account"),
#             "fieldname": "Account",
#             "fieldtype": "Link",
#             "options": "Account",
#             "width": 150,
#         },
#     ]

#     group_months = False if filters["period"] == "Monthly" else True
#     fiscal_year = get_fiscal_years(filters)

#     for year in fiscal_year:
#         for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
#             if filters["period"] == "Yearly":
#                 labels = [
#                     {"label": _("Budget") + " " + str(year[0]), "fieldtype": "Float"},
#                     {"label": _("Actual") + " " + str(year[0]), "fieldtype": "Float"},
#                     {"label": _("Variance") + " " + str(year[0]), "fieldtype": "Float"},
#                     {"label": _("Variance %") + " " + str(year[0]), "fieldtype": "Data"},
#                 ]
#                 for col in labels:
#                     columns.append({
#                         "label": col["label"],
#                         "fieldtype": col["fieldtype"],
#                         "fieldname": frappe.scrub(col["label"]),
#                         "width": 150
#                     })
#             else:
#                 # Modified the labels to properly handle string formatting
                # base_labels = [
                #     _("Budget") + " ({})" + " " + str(year[0]),
                #     _("Actual") + " ({})" + " " + str(year[0]),
                #     _("Variance") + " ({})" + " " + str(year[0]),
                #     _("Variance %") + " ({})" + " " + str(year[0]),
                # ]
                
#                 if group_months:
#                     period_str = (
#                         formatdate(from_date, format_string="MMM")
#                         + "-"
#                         + formatdate(to_date, format_string="MMM")
#                     )
#                 else:
#                     period_str = formatdate(from_date, format_string="MMM")
                
#                 for base_label in base_labels:
#                     formatted_label = base_label.format(period_str)
#                     fieldtype = "Float" if "Variance %" not in base_label else "Data"
#                     columns.append({
#                         "label": formatted_label,
#                         "fieldtype": fieldtype,
#                         "fieldname": frappe.scrub(formatted_label),
#                         "width": 150
#                     })

#     if filters["period"] != "Yearly":
#         for label, fieldtype in [
#             (_("Total Budget"), "Float"),
#             (_("Total Actual"), "Float"),
#             (_("Total Variance"), "Float"),
#             (_("Total Variance %"), "Data"),
#         ]:
#             columns.append({
#                 "label": label,
#                 "fieldtype": fieldtype,
#                 "fieldname": frappe.scrub(label),
#                 "width": 150
#             })

#     return columns


# def get_cost_centers(filters):
# 	order_by = ""
# 	if filters.get("budget_against") == "Cost Center":
# 		order_by = "order by lft"

# 	if filters.get("budget_against") in ["Cost Center", "Project"]:
# 		return frappe.db.sql_list(
# 			"""
# 				select
# 					name
# 				from
# 					`tab{tab}`
# 				where
# 					company = %s
# 				{order_by}
# 			""".format(tab=filters.get("budget_against"), order_by=order_by),
# 			filters.get("company"),
# 		)
# 	else:
# 		return frappe.db.sql_list(
# 			"""
# 				select
# 					name
# 				from
# 					`tab{tab}`
# 			""".format(tab=filters.get("budget_against"))
# 		)  # nosec

# # Get dimension & target details
# def get_dimension_target_details(filters):
# 	budget_against = frappe.scrub(filters.get("budget_against"))
# 	cond = ""
# 	if filters.get("budget_against_filter"):
# 		cond += f""" and b.{budget_against} in (%s)""" % ", ".join(
# 			["%s"] * len(filters.get("budget_against_filter"))
# 		)

# 	return frappe.db.sql(
# 		f"""
# 			select
# 				b.{budget_against} as budget_against,
# 				b.monthly_distribution,
# 				ba.account,
# 				ba.budget_amount,
# 				b.fiscal_year
# 			from
# 				`tabBudget` b,
# 				`tabBudget Account` ba
# 			where
# 				b.name = ba.parent
# 				and b.docstatus = 1
# 				and b.fiscal_year between %s and %s
# 				and b.budget_against = %s
# 				and b.company = %s
# 				{cond}
# 			order by
# 				b.fiscal_year
# 		""",
# 		tuple(
# 			[
# 				filters.from_fiscal_year,
# 				filters.to_fiscal_year,
# 				filters.budget_against,
# 				filters.company,
# 			]
# 			+ (filters.get("budget_against_filter") or [])
# 		),
# 		as_dict=True,
# 	)


# # Get target distribution details of accounts of cost center
# def get_target_distribution_details(filters):
# 	target_details = {}
# 	for d in frappe.db.sql(
# 		"""
# 			select
# 				md.name,
# 				mdp.month,
# 				mdp.percentage_allocation
# 			from
# 				`tabMonthly Distribution Percentage` mdp,
# 				`tabMonthly Distribution` md
# 			where
# 				mdp.parent = md.name
# 				and md.fiscal_year between %s and %s
# 			order by
# 				md.fiscal_year
# 		""",
# 		(filters.from_fiscal_year, filters.to_fiscal_year),
# 		as_dict=1,
# 	):
# 		target_details.setdefault(d.name, {}).setdefault(d.month, flt(d.percentage_allocation))

# 	return target_details


# # Get actual details from gl entry
# def get_actual_details(name, filters):
# 	budget_against = frappe.scrub(filters.get("budget_against"))
# 	cond = ""

# 	if filters.get("budget_against") == "Cost Center":
# 		cc_lft, cc_rgt = frappe.db.get_value("Cost Center", name, ["lft", "rgt"])
# 		cond = f"""
# 				and lft >= "{cc_lft}"
# 				and rgt <= "{cc_rgt}"
# 			"""

# 	ac_details = frappe.db.sql(
# 		f"""
# 			select
# 				gl.account,
# 				gl.debit,
# 				gl.credit,
# 				gl.fiscal_year,
# 				MONTHNAME(gl.posting_date) as month_name,
# 				b.{budget_against} as budget_against
# 			from
# 				`tabGL Entry` gl,
# 				`tabBudget Account` ba,
# 				`tabBudget` b
# 			where
# 				b.name = ba.parent
# 				and b.docstatus = 1
# 				and ba.account=gl.account
# 				and b.{budget_against} = gl.{budget_against}
# 				and gl.fiscal_year between %s and %s
# 				and b.{budget_against} = %s
# 				and exists(
# 					select
# 						name
# 					from
# 						`tab{filters.budget_against}`
# 					where
# 						name = gl.{budget_against}
# 						{cond}
# 				)
# 				group by
# 					gl.name
# 				order by gl.fiscal_year
# 		""",
# 		(filters.from_fiscal_year, filters.to_fiscal_year, name),
# 		as_dict=1,
# 	)

# 	cc_actual_details = {}
# 	for d in ac_details:
# 		cc_actual_details.setdefault(d.account, []).append(d)

# 	return cc_actual_details


# def get_dimension_account_month_map(filters):
# 	dimension_target_details = get_dimension_target_details(filters)
# 	tdd = get_target_distribution_details(filters)

# 	cam_map = {}

# 	for ccd in dimension_target_details:
# 		actual_details = get_actual_details(ccd.budget_against, filters)

# 		for month_id in range(1, 13):
# 			month = datetime.date(2013, month_id, 1).strftime("%B")
# 			cam_map.setdefault(ccd.budget_against, {}).setdefault(ccd.account, {}).setdefault(
# 				ccd.fiscal_year, {}
# 			).setdefault(month, frappe._dict({"target": 0.0, "actual": 0.0}))

# 			tav_dict = cam_map[ccd.budget_against][ccd.account][ccd.fiscal_year][month]
# 			month_percentage = (
# 				tdd.get(ccd.monthly_distribution, {}).get(month, 0)
# 				if ccd.monthly_distribution
# 				else 100.0 / 12
# 			)

# 			tav_dict.target = flt(ccd.budget_amount) * month_percentage / 100

# 			for ad in actual_details.get(ccd.account, []):
# 				if ad.month_name == month and ad.fiscal_year == ccd.fiscal_year:
# 					tav_dict.actual += flt(ad.debit) - flt(ad.credit)

# 	return cam_map


# def get_fiscal_years(filters):
# 	fiscal_year = frappe.db.sql(
# 		"""
# 			select
# 				name
# 			from
# 				`tabFiscal Year`
# 			where
# 				name between %(from_fiscal_year)s and %(to_fiscal_year)s
# 		""",
# 		{"from_fiscal_year": filters["from_fiscal_year"], "to_fiscal_year": filters["to_fiscal_year"]},
# 	)

# 	return fiscal_year


# def get_chart_data(filters, columns, data):
# 	if not data:
# 		return None

# 	labels = []

# 	fiscal_year = get_fiscal_years(filters)
# 	group_months = False if filters["period"] == "Monthly" else True

# 	for year in fiscal_year:
# 		for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
# 			if filters["period"] == "Yearly":
# 				labels.append(year[0])
# 			else:
# 				if group_months:
# 					label = (
# 						formatdate(from_date, format_string="MMM")
# 						+ "-"
# 						+ formatdate(to_date, format_string="MMM")
# 					)
# 					labels.append(label)
# 				else:
# 					label = formatdate(from_date, format_string="MMM")
# 					labels.append(label)

# 	no_of_columns = len(labels)

# 	budget_values, actual_values = [0] * no_of_columns, [0] * no_of_columns
# 	for d in data:
# 		values = d[2:]
# 		index = 0

# 		for i in range(no_of_columns):
# 			budget_values[i] += values[index]
# 			actual_values[i] += values[index + 1]
# 			index += 4  # Changed from 3 to 4 to account for the new variance % column

# 	return {
# 		"data": {
# 			"labels": labels,
# 			"datasets": [
# 				{"name": _("Budget"), "chartType": "bar", "values": budget_values},
# 				{"name": _("Actual Expense"), "chartType": "bar", "values": actual_values},
# 			],
# 		},
# 		"type": "bar",
# 	}




# # Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# # License: GNU General Public License v3. See license.txt
 
from __future__ import unicode_literals
import datetime
import frappe
from frappe import _
from frappe.utils import flt, formatdate

from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    if filters.get("budget_against_filter"):
        dimensions = filters.get("budget_against_filter")
    else:
        dimensions = get_cost_centers(filters)

    period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
    cam_map = get_dimension_account_month_map(filters)

    data = []
    for dimension in dimensions:
        dimension_items = cam_map.get(dimension)
        if dimension_items:
            data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, 0)

    chart = get_chart_data(filters, columns, data)

    return columns, data, None, chart


def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation):
    for account, monthwise_data in dimension_items.items():
        row = [dimension, account]
        totals = [0, 0, 0, ""]  # budget, actual, variance, variance%
        
        for year in get_fiscal_years(filters):
            last_total = 0
            for relevant_months in period_month_ranges:
                period_data = [0, 0, 0, ""]  # budget, actual, variance, variance%
                
                for month in relevant_months:
                    if monthwise_data.get(year[0]):
                        month_data = monthwise_data.get(year[0]).get(month, {})
                        for i, fieldname in enumerate(["target", "actual", "variance"]):
                            value = flt(month_data.get(fieldname))
                            period_data[i] += value
                            if i < 3:  # Don't add to totals for the percentage string
                                totals[i] += value

                period_data[0] += last_total

                if DCC_allocation:
                    period_data[0] = period_data[0] * (DCC_allocation / 100)
                    period_data[1] = period_data[1] * (DCC_allocation / 100)

                if filters.get("show_cumulative"):
                    last_total = period_data[0] - period_data[1]

                period_data[2] = period_data[0] - period_data[1]
                
                # Calculate variance percentage
                if period_data[0] != 0:
                    variance_pct = flt((period_data[2] / abs(period_data[0])) * 100)
                    period_data[3] = "{0:.3f}%".format(variance_pct)
                else:
                    period_data[3] = "0.000%"
                
                row += period_data
        
        # Calculate total variance percentage
        totals[2] = totals[0] - totals[1]
        if totals[0] != 0:
            total_variance_pct = flt((totals[2] / abs(totals[0])) * 100)
            totals.append("{0:.3f}%".format(total_variance_pct))
        else:
            totals.append("0.000%")
        
        if filters["period"] != "Yearly":
            row += totals
        data.append(row)

    return data


def get_columns(filters):
    columns = [
        {
            "label": _(filters.get("budget_against")),
            "fieldtype": "Link",
            "fieldname": "budget_against",
            "options": filters.get("budget_against"),
            "width": 150,
        },
        {
            "label": _("Account"),
            "fieldname": "Account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 150,
        },
    ]

    group_months = False if filters["period"] == "Monthly" else True

    fiscal_year = get_fiscal_years(filters)

    for year in fiscal_year:
        for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
            if filters["period"] == "Yearly":
                labels = [
                    _("Budget") + " " + str(year[0]),
                    _("Actual Used") + " " + str(year[0]),
                    _("Variance") + " " + str(year[0]),
                    _("Variance %") + " " + str(year[0]),
                ]
                for label in labels:
                    fieldtype = "Float" if "%" not in label else "Data"
                    columns.append(
                        {"label": label, "fieldtype": fieldtype, "fieldname": frappe.scrub(label), "width": 150}
                    )
            else:
                labels = [
                    (_("Budget"), str(year[0])),
                    (_("Actual Used"), str(year[0])),
                    (_("Variance"), str(year[0])),
                    (_("Variance %"), str(year[0])),
                ]
                for label, year_str in labels:
                    base_label = label + " ({0}) " + year_str
                    if group_months:
                        formatted_label = base_label.format(
                            formatdate(from_date, format_string="MMM")
                            + "-"
                            + formatdate(to_date, format_string="MMM")
                        )
                    else:
                        formatted_label = base_label.format(
                            formatdate(from_date, format_string="MMM")
                        )
                    
                    fieldtype = "Float" if "%" not in formatted_label else "Data"
                    columns.append(
                        {"label": formatted_label, "fieldtype": fieldtype, 
                         "fieldname": frappe.scrub(formatted_label), "width": 150}
                    )

    if filters["period"] != "Yearly":
        for label in [_("Total Budget"), _("Total Actual"), _("Total Variance"), _("Total Variance %")]:
            fieldtype = "Float" if "%" not in label else "Data"
            columns.append(
                {"label": label, "fieldtype": fieldtype, "fieldname": frappe.scrub(label), "width": 150}
            )

    return columns


def get_cost_centers(filters):
    order_by = ""
    if filters.get("budget_against") == "Cost Center":
        order_by = "order by lft"

    if filters.get("budget_against") in ["Cost Center", "Project"]:
        return frappe.db.sql_list(
            """
                select
                    name
                from
                    `tab{tab}`
                where
                    company = %s
                {order_by}
            """.format(tab=filters.get("budget_against"), order_by=order_by),
            filters.get("company"),
        )
    else:
        return frappe.db.sql_list(
            """
                select
                    name
                from
                    `tab{tab}`
            """.format(tab=filters.get("budget_against"))
        )


# def get_dimension_target_details(filters):
#     budget_against = frappe.scrub(filters.get("budget_against"))
#     cond = ""
#     if filters.get("budget_against_filter"):
#         cond += """ and b.{0} in ({1})""".format(
#             budget_against,
#             ", ".join(["%s"] * len(filters.get("budget_against_filter")))
#         )

#     return frappe.db.sql(
#         """
#             select
#                 b.{budget_against} as budget_against,
#                 b.monthly_distribution,
#                 ba.account,
#                 ba.budget_amount,
#                 b.fiscal_year,
#                 ifnull(ba.january,0) + ifnull(br_january,0) - ifnull(bs_january,0) as January, 
#                 ifnull(ba.february,0) + ifnull(br_february,0) - ifnull(bs_february,0) as February, 
#                 ifnull(ba.march,0) + ifnull(br_march,0) - ifnull(bs_march,0) as March, 
#                 ifnull(ba.april,0) + ifnull(br_april,0) - ifnull(bs_april,0) as April, 
#                 ifnull(ba.may,0) + ifnull(br_may,0) - ifnull(bs_may,0) as May, 
#                 ifnull(ba.june,0) + ifnull(br_june,0) - ifnull(bs_june,0) as June, 
#                 ifnull(ba.july,0) + ifnull(br_july,0) - ifnull(bs_july,0) as July, 
#                 ifnull(ba.august,0) + ifnull(br_august,0) - ifnull(bs_august,0) as August, 
#                 ifnull(ba.september,0) + ifnull(br_september,0) - ifnull(bs_september,0) as September, 
#                 ifnull(ba.october,0) + ifnull(br_october,0) - ifnull(bs_october,0) as October, 
#                 ifnull(ba.november,0) + ifnull(br_november,0) - ifnull(bs_november,0) as November, 
#                 ifnull(ba.december,0) + ifnull(br_december,0) - ifnull(bs_december,0) as December
#             from
#                 `tabBudget` b,
#                 `tabBudget Account` ba
#             where
#                 b.name = ba.parent
#                 and b.docstatus = 1
#                 and b.fiscal_year between %s and %s
#                 and b.budget_against = %s
#                 and b.company = %s
#                 {cond}
#             order by
#                 b.fiscal_year
#         """.format(budget_against=budget_against, cond=cond),
#         tuple(
#             [
#                 filters.from_fiscal_year,
#                 filters.to_fiscal_year,
#                 filters.budget_against,
#                 filters.company,
#             ]
#             + (filters.get("budget_against_filter") or [])
#         ),
#         as_dict=True,
#     )


def get_dimension_target_details(filters):
    budget_against = frappe.scrub(filters.get("budget_against"))
    cond = ""
    if filters.get("budget_against_filter"):
        cond += """ and b.{0} in ({1})""".format(
            budget_against,
            ", ".join(["%s"] * len(filters.get("budget_against_filter")))
        )

    return frappe.db.sql(
        """
            select
                b.{budget_against} as budget_against,
                b.monthly_distribution,
                ba.account,
                ba.budget_amount,
                b.fiscal_year,
                ifnull(ba.january,0) + ifnull(br_january,0) - ifnull(bs_january,0) as January, 
                ifnull(ba.february,0) + ifnull(br_february,0) - ifnull(bs_february,0) as February, 
                ifnull(ba.march,0) + ifnull(br_march,0) - ifnull(bs_march,0) as March, 
                ifnull(ba.april,0) + ifnull(br_april,0) - ifnull(bs_april,0) as April, 
                ifnull(ba.may,0) + ifnull(br_may,0) - ifnull(bs_may,0) as May, 
                ifnull(ba.june,0) + ifnull(br_june,0) - ifnull(bs_june,0) as June, 
                ifnull(ba.july,0) + ifnull(br_july,0) - ifnull(bs_july,0) as July, 
                ifnull(ba.august,0) + ifnull(br_august,0) - ifnull(bs_august,0) as August, 
                ifnull(ba.september,0) + ifnull(br_september,0) - ifnull(bs_september,0) as September, 
                ifnull(ba.october,0) + ifnull(br_october,0) - ifnull(bs_october,0) as October, 
                ifnull(ba.november,0) + ifnull(br_november,0) - ifnull(bs_november,0) as November, 
                ifnull(ba.december,0) + ifnull(br_december,0) - ifnull(bs_december,0) as December
            from
                `tabBudget` b,
                `tabBudget Account` ba
            where
                b.name = ba.parent
                and b.docstatus = 1
                and b.fiscal_year between %s and %s
                and b.budget_against = %s
                and ba.budget_amount > 0
                and (
                    ifnull(ba.january,0) > 0 OR
                    ifnull(ba.february,0) > 0 OR
                    ifnull(ba.march,0) > 0 OR
                    ifnull(ba.april,0) > 0 OR
                    ifnull(ba.may,0) > 0 OR
                    ifnull(ba.june,0) > 0 OR
                    ifnull(ba.july,0) > 0 OR
                    ifnull(ba.august,0) > 0 OR
                    ifnull(ba.september,0) > 0 OR
                    ifnull(ba.october,0) > 0 OR
                    ifnull(ba.november,0) > 0 OR
                    ifnull(ba.december,0) > 0
                )
                and b.company = %s 
                {cond}
            order by
                b.fiscal_year
        """.format(budget_against=budget_against, cond=cond),
        tuple(
            [
                filters.from_fiscal_year,
                filters.to_fiscal_year,
                filters.budget_against,
                filters.company,
            ]
            + (filters.get("budget_against_filter") or [])
        ),
        as_dict=True,
    )


def get_target_distribution_details(filters):
    target_details = {}
    for d in frappe.db.sql(
        """
            select
                md.name,
                mdp.month,
                mdp.percentage_allocation
            from
                `tabMonthly Distribution Percentage` mdp,
                `tabMonthly Distribution` md
            where
                mdp.parent = md.name
                and md.fiscal_year between %s and %s
            order by
                md.fiscal_year
        """,
        (filters.from_fiscal_year, filters.to_fiscal_year),
        as_dict=1,
    ):
        target_details.setdefault(d.name, {}).setdefault(d.month, flt(d.percentage_allocation))

    return target_details


def get_actual_details(name, filters):
    budget_against = frappe.scrub(filters.get("budget_against"))
    cond = ""

    if filters.get("budget_against") == "Cost Center" and filters.get("budget_against_filter"):
        cc_lft, cc_rgt = frappe.db.get_value("Cost Center", filters.get("budget_against_filter"), ["lft", "rgt"])
        cond = """
                and lft >= {cc_lft}
                and rgt <= {cc_rgt}
            """.format(cc_lft=cc_lft, cc_rgt=cc_rgt)

    ac_details = frappe.db.sql(
        """
            select
                gl.account,
                gl.debit,
                gl.credit,
                gl.fiscal_year,
                MONTHNAME(gl.posting_date) as month_name,
                b.{budget_against} as budget_against
            from
                `tabGL Entry` gl,
                `tabBudget Account` ba,
                `tabBudget` b
            where
                b.name = ba.parent
                and b.docstatus = 1
                and ba.account=gl.account
                and b.{budget_against} = gl.{budget_against}
                and gl.fiscal_year between %s and %s
                and b.{budget_against} = %s
                and exists(
                    select
                        name
                    from
                        `tab{filters.budget_against}`
                    where
                        name = gl.{budget_against}
                        {cond}
                )
            group by
                gl.name
            order by gl.fiscal_year
        """.format(
            budget_against=budget_against,
            cond=cond,
            filters=filters
        ),
        (filters.from_fiscal_year, filters.to_fiscal_year, name),
        as_dict=1,
    )

    cc_actual_details = {}
    for d in ac_details:
        cc_actual_details.setdefault(d.account, []).append(d)

    return cc_actual_details


def get_dimension_account_month_map(filters):
    dimension_target_details = get_dimension_target_details(filters)
    tdd = get_target_distribution_details(filters)

    cam_map = {}

    for ccd in dimension_target_details:
        actual_details = get_actual_details(ccd.budget_against, filters)

        for month_id in range(1, 13):
            month = datetime.date(2013, month_id, 1).strftime("%B")
            cam_map.setdefault(ccd.budget_against, {}).setdefault(ccd.account, {}).setdefault(
                ccd.fiscal_year, {}
            ).setdefault(month, frappe._dict({"target": 0.0, "actual": 0.0}))
            tav_dict = cam_map[ccd.budget_against][ccd.account][ccd.fiscal_year][month]
            month_percentage = (
                tdd.get(ccd.monthly_distribution, {}).get(month, 0)
                if ccd.monthly_distribution
                else 100.0 / 12
            )

            tav_dict.target = flt(ccd[month])

            for ad in actual_details.get(ccd.account, []):
                if ad.month_name == month and ad.fiscal_year == ccd.fiscal_year:
                    tav_dict.actual += flt(ad.debit) - flt(ad.credit)

    return cam_map


def get_fiscal_years(filters):
    fiscal_year = frappe.db.sql(
        """
            select
                name
            from
                `tabFiscal Year`
            where
                name between %(from_fiscal_year)s and %(to_fiscal_year)s
        """,
        {"from_fiscal_year": filters["from_fiscal_year"], "to_fiscal_year": filters["to_fiscal_year"]},
    )

    return fiscal_year


def get_chart_data(filters, columns, data):
    if not data:
        return None

    labels = []

    fiscal_year = get_fiscal_years(filters)
    group_months = False if filters["period"] == "Monthly" else True

    for year in fiscal_year:
        for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
            if filters["period"] == "Yearly":
                labels.append(year[0])
            else:
                if group_months:
                    label = (
                        formatdate(from_date, format_string="MMM")
                        + "-"
                        + formatdate(to_date, format_string="MMM")
                    )
                    labels.append(label)
                else:
                    label = formatdate(from_date, format_string="MMM")
                    labels.append(label)

    no_of_columns = len(labels)

    budget_values, actual_values = [0] * no_of_columns, [0] * no_of_columns
    for d in data:
        values = d[2:]
        index = 0

        for i in range(no_of_columns):
            budget_values[i] += values[index]
            actual_values[i] += values[index + 1]
            index += 4  # Accounts for budget, actual, variance, variance% columns

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Budget"), "chartType": "bar", "values": budget_values},
                {"name": _("Actual Expense"), "chartType": "bar", "values": actual_values},
            ],
        },
        "type": "bar",
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# # # Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# # # License: GNU General Public License v3. See license.txt
 
# from __future__ import unicode_literals
# import datetime
# import frappe
# from frappe import _
# from frappe.utils import flt, formatdate

# from erpnext.controllers.trends import get_period_date_ranges, get_period_month_ranges


# def execute(filters=None):
#     if not filters:
#         filters = {}

#     columns = get_columns(filters)
#     if filters.get("budget_against_filter"):
#         dimensions = filters.get("budget_against_filter")
#     else:
#         dimensions = get_cost_centers(filters)

#     period_month_ranges = get_period_month_ranges(filters["period"], filters["from_fiscal_year"])
#     cam_map = get_dimension_account_month_map(filters)

#     data = []
#     for dimension in dimensions:
#         dimension_items = cam_map.get(dimension)
#         if dimension_items:
#             data = get_final_data(dimension, dimension_items, filters, period_month_ranges, data, 0)

#     chart = get_chart_data(filters, columns, data)

#     return columns, data, None, chart


# def get_final_data(dimension, dimension_items, filters, period_month_ranges, data, DCC_allocation):
#     for account, monthwise_data in dimension_items.items():
#         row = [dimension, account]
#         totals = [0, 0, 0, ""]  
        
#         for year in get_fiscal_years(filters):
#             last_total = 0
#             for relevant_months in period_month_ranges:
#                 period_data = [0, 0, 0, ""] 
                
#                 for month in relevant_months:
#                     if monthwise_data.get(year[0]):
#                         month_data = monthwise_data.get(year[0]).get(month, {})
#                         for i, fieldname in enumerate(["target", "actual", "variance"]):
#                             value = flt(month_data.get(fieldname))
#                             period_data[i] += value
#                             if i < 3:
#                                 totals[i] += value

#                 period_data[0] += last_total

#                 if DCC_allocation:
#                     period_data[0] = period_data[0] * (DCC_allocation / 100)
#                     period_data[1] = period_data[1] * (DCC_allocation / 100)

#                 if filters.get("show_cumulative"):
#                     last_total = period_data[0] - period_data[1]

#                 period_data[2] = period_data[0] - period_data[1]
                
#                 if period_data[0] != 0:
#                     variance_pct = flt((period_data[2] / abs(period_data[0])) * 100)
#                     period_data[3] = "{0:.3f}%".format(variance_pct) if variance_pct != 0 else ""
#                 else:
#                     period_data[3] = ""

#                 for i in range(3):
#                     if period_data[i] == 0:
#                         period_data[i] = ""
                
#                 row += period_data
        
#         totals[2] = totals[0] - totals[1]
#         if totals[0] != 0:
#             total_variance_pct = flt((totals[2] / abs(totals[0])) * 100)
#             totals.append("{0:.3f}%".format(total_variance_pct) if total_variance_pct != 0 else "")
#         else:
#             totals.append("")
#         for i in range(3):
#             if totals[i] == 0:
#                 totals[i] = ""
        
#         if filters["period"] != "Yearly":
#             row += totals
#         data.append(row)

#     return data


# def get_columns(filters):
#     columns = [
#         {
#             "label": _(filters.get("budget_against")),
#             "fieldtype": "Link",
#             "fieldname": "budget_against",
#             "options": filters.get("budget_against"),
#             "width": 150,
#         },
#         {
#             "label": _("Account"),
#             "fieldname": "Account",
#             "fieldtype": "Link",
#             "options": "Account",
#             "width": 150,
#         },
#     ]

#     group_months = False if filters["period"] == "Monthly" else True

#     fiscal_year = get_fiscal_years(filters)

#     for year in fiscal_year:
#         for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
#             if filters["period"] == "Yearly":
#                 labels = [
#                     _("Budget") + " " + str(year[0]),
#                     _("Actual Used") + " " + str(year[0]),
#                     _("Variance") + " " + str(year[0]),
#                     _("Variance %") + " " + str(year[0]),
#                 ]
#                 for label in labels:
#                     fieldtype = "Float" if "%" not in label else "Data"
#                     columns.append(
#                         {"label": label, "fieldtype": fieldtype, "fieldname": frappe.scrub(label), "width": 150}
#                     )
#             else:
#                 labels = [
#                     (_("Budget"), str(year[0])),
#                     (_("Actual Used"), str(year[0])),
#                     (_("Variance"), str(year[0])),
#                     (_("Variance %"), str(year[0])),
#                 ]
#                 for label, year_str in labels:
#                     base_label = label + " ({0}) " + year_str
#                     if group_months:
#                         formatted_label = base_label.format(
#                             formatdate(from_date, format_string="MMM")
#                             + "-"
#                             + formatdate(to_date, format_string="MMM")
#                         )
#                     else:
#                         formatted_label = base_label.format(
#                             formatdate(from_date, format_string="MMM")
#                         )
                    
#                     fieldtype = "Float" if "%" not in formatted_label else "Data"
#                     columns.append(
#                         {"label": formatted_label, "fieldtype": fieldtype, 
#                          "fieldname": frappe.scrub(formatted_label), "width": 150}
#                     )

#     if filters["period"] != "Yearly":
#         for label in [_("Total Budget"), _("Total Actual"), _("Total Variance"), _("Total Variance %")]:
#             fieldtype = "Float" if "%" not in label else "Data"
#             columns.append(
#                 {"label": label, "fieldtype": fieldtype, "fieldname": frappe.scrub(label), "width": 150}
#             )

#     return columns


# def get_cost_centers(filters):
#     order_by = ""
#     if filters.get("budget_against") == "Cost Center":
#         order_by = "order by lft"

#     if filters.get("budget_against") in ["Cost Center", "Project"]:
#         return frappe.db.sql_list(
#             """
#                 select
#                     name
#                 from
#                     `tab{tab}`
#                 where
#                     company = %s
#                 {order_by}
#             """.format(tab=filters.get("budget_against"), order_by=order_by),
#             filters.get("company"),
#         )
#     else:
#         return frappe.db.sql_list(
#             """
#                 select
#                     name
#                 from
#                     `tab{tab}`
#             """.format(tab=filters.get("budget_against"))
#         )


# def get_dimension_target_details(filters):
#     budget_against = frappe.scrub(filters.get("budget_against"))
#     cond = ""
#     if filters.get("budget_against_filter"):
#         cond += """ and b.{0} in ({1})""".format(
#             budget_against,
#             ", ".join(["%s"] * len(filters.get("budget_against_filter")))
#         )

#     return frappe.db.sql(
#         """
#             select
#                 b.{budget_against} as budget_against,
#                 b.monthly_distribution,
#                 ba.account,
#                 ba.budget_amount,
#                 b.fiscal_year,
#                 ifnull(ba.january,0) + ifnull(br_january,0) - ifnull(bs_january,0) as January, 
#                 ifnull(ba.february,0) + ifnull(br_february,0) - ifnull(bs_february,0) as February, 
#                 ifnull(ba.march,0) + ifnull(br_march,0) - ifnull(bs_march,0) as March, 
#                 ifnull(ba.april,0) + ifnull(br_april,0) - ifnull(bs_april,0) as April, 
#                 ifnull(ba.may,0) + ifnull(br_may,0) - ifnull(bs_may,0) as May, 
#                 ifnull(ba.june,0) + ifnull(br_june,0) - ifnull(bs_june,0) as June, 
#                 ifnull(ba.july,0) + ifnull(br_july,0) - ifnull(bs_july,0) as July, 
#                 ifnull(ba.august,0) + ifnull(br_august,0) - ifnull(bs_august,0) as August, 
#                 ifnull(ba.september,0) + ifnull(br_september,0) - ifnull(bs_september,0) as September, 
#                 ifnull(ba.october,0) + ifnull(br_october,0) - ifnull(bs_october,0) as October, 
#                 ifnull(ba.november,0) + ifnull(br_november,0) - ifnull(bs_november,0) as November, 
#                 ifnull(ba.december,0) + ifnull(br_december,0) - ifnull(bs_december,0) as December
#             from
#                 `tabBudget` b,
#                 `tabBudget Account` ba
#             where
#                 b.name = ba.parent
#                 and b.docstatus = 1
#                 and b.fiscal_year between %s and %s
#                 and b.budget_against = %s
#                 and b.company = %s
#                 {cond}
#             order by
#                 b.fiscal_year
#         """.format(budget_against=budget_against, cond=cond),
#         tuple(
#             [
#                 filters.from_fiscal_year,
#                 filters.to_fiscal_year,
#                 filters.budget_against,
#                 filters.company,
#             ]
#             + (filters.get("budget_against_filter") or [])
#         ),
#         as_dict=True,
#     )


# def get_target_distribution_details(filters):
#     target_details = {}
#     for d in frappe.db.sql(
#         """
#             select
#                 md.name,
#                 mdp.month,
#                 mdp.percentage_allocation
#             from
#                 `tabMonthly Distribution Percentage` mdp,
#                 `tabMonthly Distribution` md
#             where
#                 mdp.parent = md.name
#                 and md.fiscal_year between %s and %s
#             order by
#                 md.fiscal_year
#         """,
#         (filters.from_fiscal_year, filters.to_fiscal_year),
#         as_dict=1,
#     ):
#         target_details.setdefault(d.name, {}).setdefault(d.month, flt(d.percentage_allocation))

#     return target_details


# def get_actual_details(name, filters):
#     budget_against = frappe.scrub(filters.get("budget_against"))
#     cond = ""

#     if filters.get("budget_against") == "Cost Center" and filters.get("budget_against_filter"):
#         cc_lft, cc_rgt = frappe.db.get_value("Cost Center", filters.get("budget_against_filter"), ["lft", "rgt"])
#         cond = """
#                 and lft >= {cc_lft}
#                 and rgt <= {cc_rgt}
#             """.format(cc_lft=cc_lft, cc_rgt=cc_rgt)

#     ac_details = frappe.db.sql(
#         """
#             select
#                 gl.account,
#                 gl.debit,
#                 gl.credit,
#                 gl.fiscal_year,
#                 MONTHNAME(gl.posting_date) as month_name,
#                 b.{budget_against} as budget_against
#             from
#                 `tabGL Entry` gl,
#                 `tabBudget Account` ba,
#                 `tabBudget` b
#             where
#                 b.name = ba.parent
#                 and b.docstatus = 1
#                 and ba.account=gl.account
#                 and b.{budget_against} = gl.{budget_against}
#                 and gl.fiscal_year between %s and %s
#                 and b.{budget_against} = %s
#                 and exists(
#                     select
#                         name
#                     from
#                         `tab{filters.budget_against}`
#                     where
#                         name = gl.{budget_against}
#                         {cond}
#                 )
#             group by
#                 gl.name
#             order by gl.fiscal_year
#         """.format(
#             budget_against=budget_against,
#             cond=cond,
#             filters=filters
#         ),
#         (filters.from_fiscal_year, filters.to_fiscal_year, name),
#         as_dict=1,
#     )

#     cc_actual_details = {}
#     for d in ac_details:
#         cc_actual_details.setdefault(d.account, []).append(d)

#     return cc_actual_details


# def get_dimension_account_month_map(filters):
#     dimension_target_details = get_dimension_target_details(filters)
#     tdd = get_target_distribution_details(filters)

#     cam_map = {}

#     for ccd in dimension_target_details:
#         actual_details = get_actual_details(ccd.budget_against, filters)

#         for month_id in range(1, 13):
#             month = datetime.date(2013, month_id, 1).strftime("%B")
#             cam_map.setdefault(ccd.budget_against, {}).setdefault(ccd.account, {}).setdefault(
#                 ccd.fiscal_year, {}
#             ).setdefault(month, frappe._dict({"target": 0.0, "actual": 0.0}))
#             tav_dict = cam_map[ccd.budget_against][ccd.account][ccd.fiscal_year][month]
#             month_percentage = (
#                 tdd.get(ccd.monthly_distribution, {}).get(month, 0)
#                 if ccd.monthly_distribution
#                 else 100.0 / 12
#             )

#             tav_dict.target = flt(ccd[month])

#             for ad in actual_details.get(ccd.account, []):
#                 if ad.month_name == month and ad.fiscal_year == ccd.fiscal_year:
#                     tav_dict.actual += flt(ad.debit) - flt(ad.credit)

#     return cam_map


# def get_fiscal_years(filters):
#     fiscal_year = frappe.db.sql(
#         """
#             select
#                 name
#             from
#                 `tabFiscal Year`
#             where
#                 name between %(from_fiscal_year)s and %(to_fiscal_year)s
#         """,
#         {"from_fiscal_year": filters["from_fiscal_year"], "to_fiscal_year": filters["to_fiscal_year"]},
#     )

#     return fiscal_year


# def get_chart_data(filters, columns, data):
#     if not data:
#         return None

#     labels = []

#     fiscal_year = get_fiscal_years(filters)
#     group_months = False if filters["period"] == "Monthly" else True

#     for year in fiscal_year:
#         for from_date, to_date in get_period_date_ranges(filters["period"], year[0]):
#             if filters["period"] == "Yearly":
#                 labels.append(year[0])
#             else:
#                 if group_months:
#                     label = (
#                         formatdate(from_date, format_string="MMM")
#                         + "-"
#                         + formatdate(to_date, format_string="MMM")
#                     )
#                     labels.append(label)
#                 else:
#                     label = formatdate(from_date, format_string="MMM")
#                     labels.append(label)

#     no_of_columns = len(labels)

#     budget_values, actual_values = [0] * no_of_columns, [0] * no_of_columns
#     for d in data:
#         values = d[2:]
#         index = 0

#         for i in range(no_of_columns):
#             budget_values[i] += flt(values[index])
#             actual_values[i] += flt(values[index + 1])
#             index += 4  # Accounts for budget, actual, variance, variance% columns

#     return {
#         "data": {
#             "labels": labels,
#             "datasets": [
#                 {"name": _("Budget"), "chartType": "bar", "values": budget_values},
#                 {"name": _("Actual Expense"), "chartType": "bar", "values": actual_values},
#             ],
#         },
#         "type": "bar",
#     }