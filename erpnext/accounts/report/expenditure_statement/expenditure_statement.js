// // Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt

// frappe.query_reports["Expenditure Statement"] = {
// 	"filters": [
// 		{
// 			fieldname: "company",
// 			label: __("Company"),
// 			fieldtype: "Link",
// 			options: "Company",
// 			default: frappe.defaults.get_user_default("Company"),
// 		},
// 		{
// 			fieldname: "cost_center",
// 			label: __("Cost Center"),
// 			fieldtype: "Link",
// 			options: "Cost Center",
// 			default: frappe.defaults.get_user_default("Cost Center"),
// 		},
// 	]
// };


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
			reqd: 1,
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year"),
			reqd: 1,
			on_change: function() {
				var fiscal_year = frappe.query_report.get_filter_value('fiscal_year');
				if (fiscal_year) {
					frappe.call({
						method: "frappe.client.get_value",
						args: {
							doctype: "Fiscal Year",
							filters: { name: fiscal_year },
							fieldname: ["year_start_date", "year_end_date"]
						},
						callback: function(r) {
							if (r.message) {
								frappe.query_report.set_filter_value('from_date', r.message.year_start_date);
								frappe.query_report.set_filter_value('to_date', r.message.year_end_date);
							}
						}
					});
				}
			}
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: function() {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
						is_group: 0
					}
				};
			}
		},
	]
};