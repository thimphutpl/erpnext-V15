// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Asset by Category"] = {
	"filters": [
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 0 // Set to 1 if you want to make this filter mandatory
        },
		{
            "fieldname": "category",
            "label": __("Asset Category"),
            "fieldtype": "Link",
            "options": "Asset Category",
            "reqd": 0 // Set to 1 if you want to make this filter mandatory
        }
	]
	
};
