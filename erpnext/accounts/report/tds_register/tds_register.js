// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["TDS Register"] = {
	"filters": [
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"reqd": 1,
			"get_query": function() {return {'filters': [['Cost Center', 'disabled', '!=', '1'], ['Cost Center', 'is_group', '!=', '1']]}}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "tax_withholding_category",
			"label": __("Tax Withholding Category"),
			"fieldtype": "Link",
			"options": "Tax Withholding Category",
			"reqd": 1
		},
		{
			"fieldname": "party_type",
			"label": __("Party Type"),
			"fieldtype": "Select",
			"options": "\nSupplier\nCustomer",
			"default":"Supplier",
		},
	]
};
