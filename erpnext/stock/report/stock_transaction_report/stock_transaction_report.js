// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Transaction Report"] = {
	
	"filters": [
			
			{
				fieldname:"purpose",
				label: __("Purpose"),
				fieldtype: "Link",
				options: "Stock Entry Type",
				default:'',
			},
			{
				fieldname:"from_date",
				label: __("From Date"),
				fieldtype: "Datetime",
				default: ''
			},
			{
				fieldname:"to_date",
				label: __("To Date"),
				fieldtype: "Datetime",
				default: ''
			},
			{
				fieldname:"s_warehouse",
				label: __("Source Warehouse"),
				fieldtype: "Link",
				options:"Warehouse",
				default: "",
			},
			{
				fieldname:"t_warehouse",
				label: __("Target Warehouse"),
				fieldtype: "Link",
				options:"Warehouse",
				default: "",
			},
			{
				fieldname:"item_code",
				label: __("Material Code"),
				fieldtype: "Link",
				options:"Item",
				default: "",
			},
			


		]
	};
