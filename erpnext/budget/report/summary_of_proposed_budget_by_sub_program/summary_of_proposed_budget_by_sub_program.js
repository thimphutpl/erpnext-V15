// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Summary of Proposed Budget by Sub Program"] = {
	"filters": [
		{
            "fieldname": "fiscal_year",
            "label": "Fiscal Year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "reqd": 0
        },
        {
            "fieldname": "company",
            "label": "Company",
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 0
        },
        {
            "fieldname": "account",
            "label": "Account",
            "fieldtype": "Link",
            "options": "Account",
            "reqd": 0
        },

	]
};
