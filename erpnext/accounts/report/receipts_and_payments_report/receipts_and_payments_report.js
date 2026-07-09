// frappe.require("assets/erpnext/js/financial_statements.js", function() {

frappe.query_reports["Receipts and Payments Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"on_change": function(query_report) {
				let fiscal_year = query_report.get_filter_value("fiscal_year");

				if (!fiscal_year) {
					return;
				}

				// Correct refresh method
				query_report.refresh();
			}
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
			"reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				return {
					"filters": [
						["Cost Center", "is_disabled", "!=", 1]
					]
				};
			}
		},
		{
			"fieldname": "business_activity",
			"label": __("Business Activity"),
			"fieldtype": "Link",
			"options": "Business Activity"
		},
		{
			"fieldname": "with_period_closing_entry",
			"label": __("Period Closing Entry"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "show_zero_values",
			"label": __("Show zero values"),
			"fieldtype": "Check"
		}
	],

	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (!data) {
			return value;
		}

		if (!data.parent_account || data.account_name === "Total") {
			value = "<span style='font-weight: bold'>" + value + "</span>";
		}

		return value;
	},

	"tree": true,
	"name_field": "account",
	"parent_field": "parent_account",
	"initial_depth": 3
};

// });