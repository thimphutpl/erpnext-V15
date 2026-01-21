// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Work Order Report"] = {
	"filters": [
		{
			"fieldname": "report_type",
			"label": "Report Type",
			"fieldtype": "Select",
			"options": ["In_Progress", "Completed"],
			"reqd": 1,
			"default": "In_Progress",
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label": ("Parent Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						disabled: 0,
						company: company,
						is_group: 1
					}
				};
			}
		},
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			get_query: () => {
				var cost_center = frappe.query_report.get_filter_value("cost_center")
				var company = frappe.query_report.get_filter_value("company")
				if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
				{
					return {
						filters: {
							disabled: 0,
							company: company,
							parent_cost_center: cost_center
						}
					};
					// return {"doctype": "Cost Center", filters: {"company": company, "is_disabled": 0, "parent_cost_center": cost_center}}
				}
				else
				{
					return {
						filters: {
							disabled: 0,
							company: company,
							is_group: 0
						}
					};
				// return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "is_group": 0}}
				}
			}
		},
		{
			"fieldname": "item",
			"label": ("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					filters: {
						disabled: 0,
					}
				};
			},
		},
		// {
		// 	"fieldname": "item_sub_group_type",
		// 	"label": ("Item Sub Group Type"),
		// 	"fieldtype": "Link",
		// 	"options": "Item Sub Group Type",
		// }
	]
}
