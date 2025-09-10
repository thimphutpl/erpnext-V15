// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["TDS Register"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options:"Company",
			reqd: 1,
		},
		
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "80",
			reqd: 1,
			default: frappe.datetime.get_today(),
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
			"options": ["", "Supplier", "Customer"],
		},
	]
};
