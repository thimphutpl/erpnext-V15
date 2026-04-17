// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Advance Report"] = {
	filters: [
		// {
		// 	fieldname: "account",
		// 	label: __("Account"),
		// 	fieldtype: "Link",
		// 	options: "Account",
		// 	get_query: function() {
		// 		return {
		// 			filters: {
		// 				"is_group": 0  // Show only leaf accounts by default
		// 			}
		// 		};
		// 	}
		// },
		// {
		// 	fieldname: "broad_head",
		// 	label: __("Parent Account"),
		// 	fieldtype: "Link",
		// 	options: "Account",
		// 	get_query: function() {
		// 		return {
		// 			filters: {
		// 				"is_group": 1  // Show only group accounts
		// 			}
		// 		};
		// 	},
		// 	description: __("Select a group account to view all transactions under this group")
		// },
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			width: 120
		},
		{
			fieldname: "advance_type",
			label: __("Advance Type"),
			fieldtype: "Link",
			options: "Advance Type",
			width: 120
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
