// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Schedule  Report"] = {
	"filters": [
		{
			fieldname:"fiscal_year",
			label:__("Fiscal Year"),
			fieldtype:"Link",
			options:"Fiscal Year"
		},
		{
			fieldname: "from_date",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname:"month",
			label: __("Month"),
			fieldtype: "Select",
			options: 
			[	" ",
				"January", 
				"February", 
				"March", 
				"April", 
				"May",
				"June", 
				"July", 
				"August", 
				"September", 
				"October", 
				"November", 
				"December"
			],	

		},
		{
			fieldname:"report_type",
			label: __("Report Type"),
			fieldtype: "Select",
			options: [
				"",
				"Schedule of Fund Releases Included in the Monthly Accounts",
				"Schedule of Revenue Receipt & Remittances", 
				"Schedule of Other Recoveries & Remittances",
				"Schedule of Personal Accounts Advance",
				"Schedule of Miscellaneous Receipt & Payment",
				"Schedule of Suspense - PW Advances",
				"Schedule of Suspense - Intra Agency Assigments",
				"Schedule of Suspense - Deposits Works",
				"Schedule of Suspense - Others Deposits",
			],

		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),	
		}

	]
};
