// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Advance Report"] = {
	filters: [
		{
			fieldname:"branch",
			label: "Branch",
			fieldtype: "Link",
			options : "Branch",
			reqd: 1
		},
		{
			fieldname:"from_date",
			label: "From Date",
			fieldtype: "Date",
		},
		{
			fieldname:"to_date",
			label: "To Date",
			fieldtype: "Date",
		},
		{
			fieldname:"party_type",
			label: "Party Type",
			fieldtype: "Select",
			options : ["Supplier", "Customer"],
			reqd: 1,
			on_change: function (query_report) {
				let party_type = query_report.get_values().party_type;
			
				query_report.set_filter_value("party", null);
				query_report.set_filter_value("item", null);
			
				if (!party_type) {
					query_report.set_filter_value("advance_on", null);
					return;
				}
			
				if (party_type === "Supplier") {
					query_report.set_filter_value("advance_on", "Purchase Order");
				} else {
					query_report.set_filter_value("advance_on", "Sales Order");
				}
			}
        },
		{
			fieldname:"party",
			label: "Party",
			fieldtype: "Dynamic Link",
			get_options: function() {
				var party_type = frappe.query_report.get_filter_value("party_type");
				return party_type;
			}
        },
		{
			fieldname:"advance_on",
			label: "Advance On",
			fieldtype: "Select",
			options : ["Sales Order", "Purchase Order"],
			read_only: 1
        },
		{
			fieldname:"item",
			label: "Particular",
			fieldtype: "Dynamic Link",
			get_options: function() {
				var party_type = frappe.query_report.get_filter_value("advance_on");
				return party_type;
			},
			get_query: function() {
				var branch = frappe.query_report.get_filter_value("branch");
				var party_type = frappe.query_report.get_filter_value("advance_on");
				let filters = {
					docstatus: 1
				};

				if (branch) {
					filters.branch = branch;
				}
			
				return {
					doctype: party_type,
					filters: filters
				};
			}
        },
	]
}


