// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Receipts and Payments Statement"] = {
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
            }
        },
		// {
		// 	"fieldname": "company_account",
		// 	"label": __("Bank Account"),
		// 	"fieldtype": "Link",
		// 	"options": "Account",
		// 	"get_query": function() {
		// 		var company = frappe.query_report.get_filter_value('company');
		// 		return {'filters': [
		// 							['Account', 'disabled', '!=', '1'],
		// 							['Account', 'company', '=', company],
		// 							['Account', 'account_type', '=', 'Bank'],
		// 							['Account', 'is_group', '=', 0]
		// 						]
		// 				}
		// 	},
		// },
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
					filters: [
						['Cost Center', 'disabled', '!=', 1],
						['Cost Center', 'company', '=', company]
					]
				};
			}
		},
		{
			"fieldname": "business_activity",
			"label": __("Business Activity"),
			"fieldtype": "Link",
			"options": "Business Activity",
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
			"fieldname": "with_period_closing_entry",
			"label": __("Period Closing Entry"),
			"fieldtype": "Check",
			"default": 1
		}
	],

	onload: function(report) {
		setTimeout(() => {
            // Set company filter width
            $('div[data-fieldname="company"] input').css("width", "200px");
            // Set fiscal year filter width
            // $('div[data-fieldname="fiscal_year"] input').css("width", "120px");
        }, 100);
    }
};

erpnext.utils.add_dimensions("Receipts and Payments Statement", 15);