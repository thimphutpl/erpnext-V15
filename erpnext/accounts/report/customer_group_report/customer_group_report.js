// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Group Report"] = {
	filters: [
		{
			fieldname: "company",
			label: ("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_start_date"),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_end_date"),
		},
		{
			fieldname: "cost_center",
			label: ("Parent Branch"),
			fieldtype: "Link",
			options: "Cost Center",
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
			reqd: 1,
		},
		{
			fieldname: "branch",
			label: ("Branch"),
			fieldtype: "Link",
			options: "Cost Center",
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
	]
}
