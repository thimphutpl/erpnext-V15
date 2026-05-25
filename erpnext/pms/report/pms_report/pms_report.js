// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */



frappe.query_reports["PMS Report"] = {

	onload: function (report) {
		// default UI setup
		report.get_filter("workflow_state").toggle(true);
		report.get_filter("docstatus").toggle(false);
	},

	filters: [

		// -----------------------------
		// Fiscal Year / PMS Calendar
		// -----------------------------
		{
			"fieldname": "eas_calendar",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1
		},

		// -----------------------------
		// Workflow State (dynamic)
		// -----------------------------
		{
			"fieldname": "workflow_state",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Draft", "Waiting Supervisor Approval", "Waiting Reviewer Approval", "Approved", "Rejected"],
			"default": "Approved"
		},

		// -----------------------------
		// Docstatus (hidden)
		// -----------------------------
		{
			"fieldname": "docstatus",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Draft", "Submitted"],
			"hidden": 1
		},

		// -----------------------------
		// Report Type (MAIN LOGIC)
		// -----------------------------
		{
			"fieldname": "type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"options": [
				"Target Setup Report",
				"Review Report",
				"Performance Evaluation Report"
			],
			"default": "Performance Evaluation Report",
			"reqd": 1,

			on_change: function (query_report) {

				const type = query_report.get_filter_value("type");
				const workflow_state = query_report.get_filter("workflow_state");

				let options = [""];

				// -------------------------
				// TARGET SETUP REPORT
				// -------------------------
				if (type === "Target Setup Report") {
					options = [
						"",
						"Draft",
						"Waiting Supervisor Approval",
						"Approved",
						"Rejected",
						"Cancelled"

					];
				}

				// -------------------------
				// REVIEW REPORT
				// -------------------------
				else if (type === "Review Report") {
					options = [
						"",
						"Draft",
						"Waiting Supervisor Approval",
						"Approved",
						"Rejected",
						"Cancelled"
					];
				}

				// -------------------------
				// PERFORMANCE EVALUATION
				// -------------------------
				else if (type === "Performance Evaluation Report") {
					options = [
						"",
						"Draft",
						"Waiting Supervisor Approval",
						"Waiting Reviewer Approval",
						"Approved",
						"Rejected",
						"Cancelled"

					];
				}

				// apply options
				workflow_state.df.options = options;
				workflow_state.refresh();
				workflow_state.set_value("");

				frappe.query_report.refresh();
			}
		},

		// -----------------------------
		// Branch Filter
		// -----------------------------
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		}

		// (Optional filters kept commented for future use)

		/*
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		}
		*/

	]
};
//coded by kiznang.n till here






// frappe.query_reports["PMS Report"] = {
// 	"filters": [
// 		{
// 			"fieldname": "eas_calendar",
// 			"label": __("Fiscal Year"),
// 			"fieldtype": "Link",
// 			"options": "Fiscal Year",
// 			"default": frappe.defaults.get_user_default("fiscal_year"),
// 			"reqd": 1
// 		},
// 		{
// 			"fieldname": "workflow_state",
// 			"label": __("Status"),
// 			"fieldtype": "Select",
// 			"options": ["", "Draft", "Waiting Approval", "Approved", "Rejected"],
// 			"default": "Approved"
// 		},
// 		{
// 			"fieldname": "docstatus",
// 			"label": __("Status"),
// 			"fieldtype": "Select",
// 			"options": ["", "Draft", "Submitted"],
// 			"default": "Approved",
// 			"hidden": 1
// 		},
// 		{
// 			"fieldname": "type",
// 			"label": __("Report Type"),
// 			"fieldtype": "Select",
// 			"options": ["Target Setup Report", "Review Report", "Performance Evaluation Report"],
// 			"default": "Performance Evaluation Report",
// 			"reqd": 1,
// 			on_change: function (query_report) {
// 				var type = query_report.get_filter_value('type')
// 				if (type == "Performance Evaluation Report") {
// 					query_report.get_filter("workflow_state").toggle(true);
// 					query_report.get_filter("docstatus").toggle(false);
// 					// var workflow_state = query_report.get_filter("workflow_state"); workflow_state.toggle(true);
// 					// var docstatus = query_report.get_filter("docstatus"); docstatus.toggle(false);
// 					// query_report.get_filter('reason').toggle(type == "Performance Evaluation Report" ? 1 : 0)
// 					// query_report.get_filter('from_date').toggle(type == "Performance Evaluation Report" ? 1 : 0)
// 					// query_report.get_filter('to_date').toggle(type == "Performance Evaluation Report" ? 1 : 0)
// 				}
// 				// TARGET SETUP REPORT
// 				else if (type == "Target Setup Report") {

// 					query_report.get_filter("workflow_state").toggle(true);
// 					query_report.get_filter("docstatus").toggle(false);

// 				}
// 				// REVIEW REPORT
// 				else if (type == "Review Report") {

// 					query_report.get_filter("workflow_state").toggle(true);
// 					query_report.get_filter("docstatus").toggle(false);

// 				}
// 				// else if (type == "PMS Summary") {

// 				// 	query_report.get_filter("workflow_state").toggle(true);
// 				// 	query_report.get_filter("docstatus").toggle(false);
// 				// }
// 				else {
// 					query_report.get_filter('reason').toggle(type == "Performance Evaluation Report" ? 0 : 1)
// 					query_report.get_filter('from_date').toggle(type == "Performance Evaluation Report" ? 0 : 1)
// 					query_report.get_filter('to_date').toggle(type == "Performance Evaluation Report" ? 0 : 1)
// 					var workflow_state = query_report.get_filter("workflow_state"); workflow_state.toggle(true);
// 					var docstatus = query_report.get_filter("docstatus"); docstatus.toggle(false);
// 				}
// 				frappe.query_report.refresh()
// 			}
// 		},
// 		{
// 			"fieldname": "branch",
// 			"label": __("Branch"),
// 			"fieldtype": "Link",
// 			"options": "Branch",
// 			"reqd": 0
// 		},
// {
// 	"fieldname": "department",
// 	"label": __("Department"),
// 	"fieldtype": "Link",
// 	"options": "Department",
// 	"reqd": 0
// },
// {
// 	"fieldname": "division",
// 	"label": __("Division"),
// 	"fieldtype": "Link",
// 	"options": "Division",
// 	"reqd": 0
// },
// {
// 	"fieldname":"region",
// 	"label": __("Region"),
// 	"fieldtype": "Link",
// 	"options": "Region",
// 	"reqd": 0
// },
// {
// 	"fieldname": "section",
// 	"label": __("Section"),
// 	"fieldtype": "Link",
// 	"options": "Section",
// 	"reqd": 0
// },
// {
// 	"fieldname": "unit",
// 	"label": __("Unit"),
// 	"fieldtype": "Link",
// 	"options": "Unit",
// 	"reqd": 0
// },
// {
// 	"fieldname": "reason",
// 	"label": __("Reason"),
// 	"fieldtype": "Select",
// 	"options": "\nChange In Section/Division/Department\nSuperannuation/Left\nTransfer\nChange In PMS Group",
// 	"hidden": 0
// },
// {
// 	"fieldname": "from_date",
// 	"label": __("Appointed From Date"),
// 	"fieldtype": "Date",
// 	"hidden": 0
// },
// {
// 	"fieldname": "to_date",
// 	"label": __("Appointed To Date"),
// 	"fieldtype": "Date",
// 	"hidden": 0
// },
// {
// 	"fieldname": "gender",
// 	"label": __("Gender"),
// 	"fieldtype": "Select",
// 	"options": ["", "Male", "Female"],
// 	"reqd": 0
// },
// 	]
// };
