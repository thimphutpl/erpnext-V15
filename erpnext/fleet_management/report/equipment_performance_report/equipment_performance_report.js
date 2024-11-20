// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Equipment Performance Report"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Equipment Performance Report"] = {
	"filters": [
		{
                        "fieldname": "branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Branch",


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
                        "fieldname": "not_cdcl",
                        "label": ("Include Only CDCL Equipments"),
                        "fieldtype": "Check",
                        "default": 1
                },

		{	
                        "fieldname": "include_disabled",
                        "label": ("Include Disbaled Equipments"),
                        "fieldtype": "Check",
                        "default": 0
                }


        ]
}
