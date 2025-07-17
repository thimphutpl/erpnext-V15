// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Fabrication And Bailly Bridge Report"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		}

	],
	onload: function(report) {
        report.page.add_inner_button("Clear Filters", function () {
            report.set_filter_value("branch", null);
            report.set_filter_value("cost_center", null);
            report.set_filter_value("company", null);
        });
    },
};
