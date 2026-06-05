// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Advance Summary Report"] = {
	filters: [
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: function () {
				return {
					filters: {
						company: "GYALSUNG INFRA"
					}
				};
			}
		},
		{
			fieldname: "from_date",
			label: __("Start Date"),
			fieldtype: "Date",
			default: "2020-01-01",
			reqd: 1,
			read_only: 1
		},
		{
			fieldname: "to_date",
			label: __("End Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			read_only: 1
		},
		{
			fieldname: "advance_account",
			label: __("Advance Account"),
			fieldtype: "Select",
			options: [
				"",
				"A202022001 - Advance to Staff (Other) - GYALSUNG",
				"A202022002 - Advance to Staff (Salary) - GYALSUNG",
				"A202022003 - Advance to Staff (Travel) - GYALSUNG",
				"A202022004 - Advance to Supplier - GYALSUNG",
				"A202022005 - Mobilisation advance Paid - GYALSUNG",
				"A202022006 - Musterroll Advance - GYALSUNG",
				"L202030101 - Advance from Customer - GYALSUNG",
				"L202030102 - Advance from Other - GYALSUNG",
				"L202030107 - Mobilization advance Received - GYALSUNG"
			].join("\n")
		},
		
		{
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Select",
			options: "\nSupplier\nEmployee",
			on_change: function () {
				let party_type = frappe.query_report.get_filter_value("party_type");

				frappe.query_report.set_filter_value("party", "");

				let party_filter = frappe.query_report.get_filter("party");
				party_filter.df.options = party_type || "";
				party_filter.refresh();
			}
		},
		
		{
			fieldname: "supplier_type",
			label: __("Supplier Type"),
			fieldtype: "Select",
			options: "\nIndian Vendor\nInternational Vendor\nDomestic Vendor",
			depends_on: "eval:doc.party_type == 'Supplier'",
			on_change: function () {
				frappe.query_report.set_filter_value("party", "");
			}
		},
		
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "Link",
			options: "Supplier",
			get_query: function () {
				let party_type = frappe.query_report.get_filter_value("party_type");
				let supplier_type = frappe.query_report.get_filter_value("supplier_type");

				if (party_type === "Supplier") {
					let filters = {};

					if (supplier_type) {
						filters["supplier_type"] = supplier_type;
					}

					return {
						doctype: "Supplier",
						filters: filters
					};
				}

				if (party_type === "Employee") {
					return {
						doctype: "Employee"
					};
				}

				return {
					doctype: "Supplier"
				};
			}
		}
	]
};