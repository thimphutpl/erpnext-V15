// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Production and Disposal Target Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1,
		}, 
		{
			"fieldname": "uinput",
			"label": ("Options"),
			"fieldtype": "Select",
			"options": ["Production", "Disposal"],
			"reqd" : 1,
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
			},
			"on_change": function(query_report) {
				var cost_center = frappe.query_report.get_filter_value("cost_center");
				query_report.trigger_refresh();
				if (cost_center) {
					frappe.call({
						method: "erpnext.custom_utils.get_branch_from_cost_center",
						args: {
							"cost_center": cost_center,
						},
						callback: function(r) {
							query_report.set_filter_value("branch", r.message);
							query_report.trigger_refresh();
						}
					})
				}
			},
			"reqd": 1,
		},
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			// "read_only": 1,
			// "get_query": function() {
			//         var company = frappe.query_report.filters_by_name.company.get_value();
			//         return {"doctype": "Branch", "filters": {"company": company, "is_disabled": 0}}
			// }
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
				}
			}
		},
		{
			"fieldname": "location",
			"label": ("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"get_query": function() {
				var branch = frappe.query_report.filters_by_name.branch.get_value();
				branch = branch.replace(' - NRDCL','');
				return {
					filters: {
						is_disabled: 0,
						branch: branch,
					}
				};
			}
		},
		{
			"fieldname": "item_group",
			"label": __("Material Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			// "reqd": 1,
		},
                {
			"fieldname": "uom",
			"label": __("UOM"),
			"fieldtype": "Link",
			"options": "UOM",
			// "reqd": 1,
		},
	]
}
