// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

/* eslint-disable */

frappe.query_reports["Supplementary Budget Report"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			"on_change": function (query_report) {
                set_program_code(query_report);
            }
		

			// on_change: function (query_report) {
			// 	clear_filter_value(query_report, "to_cc");
			// 	clear_filter_value(query_report, "to_project");
			// 	clear_filter_value(query_report, "to_acc");
			// }
		},

		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year"),
			reqd: 1,

			on_change: function (query_report) {
				set_fiscal_year_dates(query_report, true);
			}
		},

		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1
		},

		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1
		},

		{
			fieldname: "budget_against",
			label: __("Budget Against"),
			fieldtype: "Select",
			options: [
				"Cost Center",
				"Project"
			],
			default: "Cost Center",
			reqd: 1,

			on_change: function (query_report) {
				set_budget_against_filter_visibility(query_report);
				query_report.trigger_refresh();
			}
		},

		{
			fieldname: "to_project",
			label: __("To Project"),
			fieldtype: "Link",
			options: "Project",
			hidden: 1,

			get_query: function () {
				var company = frappe.query_report.get_filter_value("company");

				var filters = [
					["Project", "status", "!=", "Completed"]
				];

				if (company) {
					filters.push(["Project", "company", "=", company]);
				}

				return {
					filters: filters
				};
			}
		},

		{
			fieldname: "to_cc",
			label: __("To Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",

			get_query: function () {
				var company = frappe.query_report.get_filter_value("company");

				var filters = [
					["Cost Center", "disabled", "=", 0]
				];

				if (company) {
					filters.push(["Cost Center", "company", "=", company]);
				}

				return {
					filters: filters
				};
			}
		},

		{
			fieldname: "to_acc",
			label: __("To Account"),
			fieldtype: "Link",
			options: "Account",

			get_query: function () {
				var company = frappe.query_report.get_filter_value("company");

				var filters = [
					["Account", "disabled", "=", 0],
					["Account", "is_group", "=", 0]
				];

				if (company) {
					filters.push(["Account", "company", "=", company]);
				}

				return {
					filters: filters
				};
			}
		}
	],

	onload: function (query_report) {
		set_budget_against_filter_visibility(query_report);

		var fiscal_year = query_report.get_filter_value("fiscal_year");
		var from_date = query_report.get_filter_value("from_date");
		var to_date = query_report.get_filter_value("to_date");

		if (fiscal_year && (!from_date || !to_date)) {
			set_fiscal_year_dates(query_report, false);
		}
	}
};


function set_budget_against_filter_visibility(query_report) {
	var budget_against =
		query_report.get_filter_value("budget_against") || "Cost Center";

	var project_filter = query_report.get_filter("to_project");
	var cost_center_filter = query_report.get_filter("to_cc");
	var account_filter = query_report.get_filter("to_acc");

	if (budget_against === "Project") {
		if (project_filter) {
			project_filter.toggle(true);
		}

		if (cost_center_filter) {
			cost_center_filter.toggle(false);

			if (query_report.get_filter_value("to_cc")) {
				cost_center_filter.set_value("");
			}
		}

		/*
			Account remains visible because every Supplementary Budget
			child row contains an Account.
		*/
		if (account_filter) {
			account_filter.toggle(true);
		}

	} else {
		if (project_filter) {
			project_filter.toggle(false);

			if (query_report.get_filter_value("to_project")) {
				project_filter.set_value("");
			}
		}

		if (cost_center_filter) {
			cost_center_filter.toggle(true);
		}

		if (account_filter) {
			account_filter.toggle(true);
		}
	}
}


function set_fiscal_year_dates(query_report, force_update) {
	var fiscal_year = query_report.get_filter_value("fiscal_year");

	if (!fiscal_year) {
		return;
	}

	frappe.call({
		method: "frappe.client.get_value",

		args: {
			doctype: "Fiscal Year",
			filters: {
				name: fiscal_year
			},
			fieldname: [
				"year_start_date",
				"year_end_date"
			]
		},

		callback: function (response) {
			if (!response.message) {
				return;
			}

			var from_date_filter = query_report.get_filter("from_date");
			var to_date_filter = query_report.get_filter("to_date");

			var current_from_date =
				query_report.get_filter_value("from_date");

			var current_to_date =
				query_report.get_filter_value("to_date");

			if (
				from_date_filter &&
				(force_update || !current_from_date)
			) {
				from_date_filter.set_value(
					response.message.year_start_date
				);
			}

			if (
				to_date_filter &&
				(force_update || !current_to_date)
			) {
				to_date_filter.set_value(
					response.message.year_end_date
				);
			}

			query_report.trigger_refresh();
		}
	});
}


function clear_filter_value(query_report, fieldname) {
	var filter = query_report.get_filter(fieldname);

	if (
		filter &&
		query_report.get_filter_value(fieldname)
	) {
		filter.set_value("");
	}
}

function set_program_code(report) {
	
    let company = report.get_filter_value("company");

    if (!company) {
        report.program_code = "";
        report.program_name = "";
        report.refresh();
        return;
    }

    frappe.db.get_value(
        "Company",
        company,
        [
            "program_code",
            "program_name"
        ]
    ).then(r => {

        report.program_code = r.message.program_code || "";
        report.program_name = r.message.program_name || "";

        report.refresh();

    });
}
