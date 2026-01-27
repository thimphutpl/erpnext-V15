// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Over Head Cost"] = {
	"filters": [
		{	
			"fieldname": "cost_center",
			"label": ("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": "100"
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{	
			"fieldname": "account",
			"label": ("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": "100",
			"get_query": function() {
                return {
                    filters: {
                        root_type: "Expense"
                    }
                };
            }
		}
	]
};
