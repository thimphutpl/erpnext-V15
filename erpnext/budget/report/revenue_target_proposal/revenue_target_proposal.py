# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    if not filters or not filters.get("fiscal_year"):
        frappe.throw(_("Fiscal Year is required"))

    columns, grand_total_dict = get_columns(filters)
    data = get_data(filters, grand_total_dict)
    return columns, data

def get_data(filters, grand_total):
    data = []
    cc_amount = {}

    all_data = frappe.db.sql("""
        SELECT ra.account, ra.account_number, ra.cost_center, ra.target_amount
        FROM `tabRevenue Target Account` ra, `tabRevenue Target` rt
        WHERE ra.parent = rt.name AND rt.fiscal_year = %s
        ORDER BY ra.account_number
    """, filters.fiscal_year, as_dict=True)

    for a in all_data:
        acc = str(a.account).rstrip(" - CDCL").replace(' ', '_').strip().lower()
        cc = str(a.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower()

        if acc in cc_amount:
            cc_amount[acc][cc] = a.target_amount
        else:
            cc_amount[acc] = {"account": a.account, "account_number": a.account_number, cc: a.target_amount}

    for acc, acc_data in cc_amount.items():
        row = {"account": acc_data["account"], "account_number": acc_data["account_number"]}
        total = 0
        for cc_key, value in acc_data.items():
            if cc_key not in ("account", "account_number"):
                total += flt(value)
                row[cc_key] = flt(value)
        row["total"] = total
        data.append(row)

    data.append(grand_total)
    return data

def get_columns(filters):
    gtot = 0.0
    total_dict = {"account_number": "Total"}
    cols = [
        {"fieldname": "account", "label": "Account", "fieldtype": "Link", "options": "Account", "width": 300},
        {"fieldname": "account_number", "label": "Account Code", "fieldtype": "Data", "width": 150},
    ]

    ccs = frappe.db.sql("""
        SELECT ra.cost_center, SUM(ra.target_amount) AS grand_total
        FROM `tabRevenue Target Account` ra, `tabRevenue Target` rt
        WHERE ra.parent = rt.name AND rt.docstatus < 2 AND rt.fiscal_year = %s
        GROUP BY ra.cost_center
        ORDER BY ra.cost_center ASC
    """, filters.fiscal_year, as_dict=True)

    for cc in ccs:
        cc_key = str(cc.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower()
        cols.append({
            "fieldname": cc_key,
            "label": cc.cost_center,
            "fieldtype": "Currency",
            "width": 180
        })
        total_dict[cc_key] = flt(cc.grand_total)
        gtot += flt(cc.grand_total)

    cols.append({"fieldname": "total", "label": "Total", "fieldtype": "Currency", "width": 180})
    total_dict["total"] = gtot
    return cols, total_dict



# def execute(filters=None):
# 	columns, grand_total_dict = get_columns(filters)
# 	data = get_data(filters, grand_total_dict)
# 	return columns, data

# def get_data(filters, grand_total):
# 	data = []
# 	cc_amount = {}
# 	all_data = frappe.db.sql("select ra.account, ra.account_number, ra.cost_center, ra.target_amount as target_amount from `tabRevenue Target Account` ra, `tabRevenue Target` rt where ra.parent = rt.name and rt.fiscal_year = %s order by ra.account_number", filters.fiscal_year, as_dict=True) 
# 	#frappe.msgprint("{0}".format(all_data))
# 	for a in all_data:
# 		acc = str(a.account).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')
# 		cc = str(a.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')
# 		if acc in cc_amount:
# 			cc_amount[acc][cc] = a.target_amount
# 		else:
# 			row = {"account": str(a.account), "account_number": str(a.account_number), cc: a.target_amount}
# 			cc_amount[acc] = row;

# 	for a in cc_amount:
# 		row = {}
# 		total = 0
# 		for b in cc_amount[a]:
# 			row[b] = cc_amount[a][b]
# 			if b not in ('account','account_number'):
# 				total = flt(total) + flt(cc_amount[a][b])
# 		row['total'] = flt(total)
# 		data.append(row)
# 	data.append(grand_total)
# 	return data

# def get_columns(filters):
# 	gtot = 0.0
# 	total_dict = {"account_number": "Total"}
# 	cols = [
# 		{
# 			"fieldname": "account",
# 			"label": "Account",
# 			"fieldtype": "Link",
# 			"options": "Account",
# 			"width": 300
# 		},
# 		{
# 			"fieldname": "account_number",
# 			"label": "Account Code",
# 			"fieldtype": "Data",
# 			"width": 150
# 		},
# 	]
# 	ccs = frappe.db.sql("select ra.cost_center, sum(ra.target_amount) as grand_total from `tabRevenue Target Account` ra, `tabRevenue Target` rt where ra.parent = rt.name and rt.docstatus < 2 and rt.fiscal_year = %s group by ra.cost_center order by ra.cost_center ASC", filters.fiscal_year, as_dict=True)
# 	for cc in ccs:
# 		cc_key = str(cc.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')
# 		row = {}
# 		row['fieldname'] = cc_key
# 		row['label'] = cc.cost_center
# 		row['fieldtype'] = "Currency"
# 		row['width'] = 180
# 		cols.append(row)
# 		total_dict[cc_key] = flt(cc.grand_total)
# 		gtot += flt(cc.grand_total)
# 	cols.append({"fieldname": "total", "label": "Total", "fieldtype": "Currency", "width": 180})
# 	total_dict['total'] = flt(gtot)
# 	#frappe.msgprint(_("{0}").format(total_dict))
# 	return cols, total_dict

