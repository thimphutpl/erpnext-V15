// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Expenditure Statement"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "broad_head",
			label: __("Broad Head"),
			fieldtype: "Link",
			options: "Account",
			get_query: function () {
				return {
					filters: {
						is_group: 1
					}
				};
			}
		},
		{
			fieldname: "account",
			label: __("Account"),
			fieldtype: "Link",
			options: "Account",
			get_query: function() {
				return {
					filters: {
						"is_group": 0  // Show only leaf accounts by default
					}
				};
			}
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			default: frappe.defaults.get_user_default("Cost Center"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: 120
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: 120
		}
	]
};
