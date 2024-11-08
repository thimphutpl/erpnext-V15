// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Expenditure Statement"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
			"on_change": function() {
				// Clear fiscal year when company changes
				frappe.query_report.set_filter_value('fiscal_year', '');
				// Refresh cost center filter when company is changed
				frappe.query_report.set_filter_value('cost_center', '');
			}
		},
		{
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "reqd": 1,
			"get_query": function() {
                var company = frappe.query_report.get_filter_value('company');
                return {
                    filters: {
                        "company": company
                    }
                };
            }
        },
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][new Date().getMonth()],
			"reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				var company = frappe.query_report.get_filter_value('company');
				return {
					"filters": {
						"company": company,
						"is_group": 0
					}
				};
			},
			"default": frappe.defaults.get_user_default("Cost Center"),
		},
		{
			"fieldname": "business_activity",
			"label": __("Business Activity"),
			"fieldtype": "Link",
			"options": "Business Activity",
		}
	],
};
