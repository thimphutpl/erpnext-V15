// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Expenditure Statement"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year"),
			reqd: 1,

			on_change: function () {
				var fiscal_year =
					frappe.query_report.get_filter_value("fiscal_year");

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
					callback: function (r) {
						if (r.message) {
							frappe.query_report.set_filter_value(
								"from_date",
								r.message.year_start_date
							);

							frappe.query_report.set_filter_value(
								"to_date",
								r.message.year_end_date
							);
						}
					}
				});
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
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",

			get_query: function () {
				return {
					filters: {
						company:
							frappe.query_report.get_filter_value(
								"company"
							),
						is_group: 0
					}
				};
			}
		}
	],

	formatter: function (
		value,
		row,
		column,
		data,
		default_formatter
	) {
		if (!data) {
			return default_formatter(
				value,
				row,
				column,
				data
			);
		}

		/*
		 * Combine Activity Code and Activity Name.
		 *
		 * Example:
		 * 001.00 - GENERAL ADMINISTRATION
		 */
		if (column.fieldname === "ac") {
			var activity_code = data.ac || "";
			var activity_name = data.ac_name || "";

			if (activity_code && activity_name) {
				value =
					activity_code +
					" - " +
					activity_name;
			}
			else if (activity_code) {
				value = activity_code;
			}
			else {
				value = activity_name;
			}
		}

		/*
		 * Combine FIC and Source of Fund Name.
		 *
		 * Example:
		 * 0105 - GOI Grant
		 */
		if (column.fieldname === "fic") {
			var fic_code = data.fic || "";
			var source_of_fund_name =
				data.fic_name || "";

			if (fic_code && source_of_fund_name) {
				value =
					fic_code +
					" - " +
					source_of_fund_name;
			}
			else if (fic_code) {
				value = fic_code;
			}
			else {
				value = source_of_fund_name;
			}
		}

		return default_formatter(
			value,
			row,
			column,
			data
		);
	}
};