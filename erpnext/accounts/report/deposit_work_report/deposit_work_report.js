// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Deposit Work Report"] = {
	"filters": [
		// {
		// 	"fieldname" : "branch",
		// 	"label" : ("Branch"),
		// 	"fieldtype" : "Link",
		// 	"options": "Branch",
		// 	"width" : "120",
		// },
		// {
		// 	"fieldname" : "from_date",
		// 	"label" : ("From Date"),
		// 	"fieldtype" : " Date",
		// 	"width" : "100",
		// },
		// {
		// 	"fieldname": "to_date",
		// 	"label" : ("To Date"),
		// 	"fieldtype" : "Date",
		// 	"width" : "100"
		// },

		{
			fieldname: "broad_head",
			label: __("Broad Head"),
			fieldtype: "Link",
			options: "Account",
			get_query: function () {
				return {
					filters: {
						is_group: 1,
					}
				};
			}
		},
        {
            "fieldname": "account",
            "label": "Account",
            "fieldtype": "Link",
            "options": "Account"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        }
	]
}
