// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Overall Sales Report"] = {
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
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Branch"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldtype: "Break",
		},
		{
			fieldname: "item_group",
			label: __("Material Group"),
			fieldtype: "Link",
			options: "Item Group",
			get_query: () => {
				return {
					filters: {
						is_group: 1
					}
				};
			},
		},
		{
			fieldname: "item_sub_group",
			label: __("Material Sub Group"),
			fieldtype: "Link",
			options: "Item Sub Group",
			get_query: () => {
				var item_group = frappe.query_report.get_filter_value("item_group")
				return {
					filters: {
						item_group: item_group,
						// is_group: 0
					}
				};
				// return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
			}
		},
		{
			fieldname: "item",
			label: __("Material"),
			fieldtype: "Link",
			options: "Item",
			get_query: () => {
				var sub_group = frappe.query_report.get_filter_value("item_sub_group")
				return {
					filters: {
						item_sub_group: sub_group,
						disabled: 0
					}
				};

			}
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
			get_query: () => {
				return {
					filters: {
						disabled: 0
					}
				};
				// return {"doctype": "Warehouse", "filters": {"disabled": 0}}
			}
		},
		{
			fieldname: "report_by",
			label: "Report Base On",
			fieldtype: "Select",
			options: ["Sales Order", "Delivery Note", "Sales Invoice"],
			default: "Sales Order",
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			get_query: () => {
				return {
					filters: {
						disabled: 0
					}
				};
				// return {"doctype": "Customer", "filters": {"disabled": 0}}
			}
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "Link",
			options: "Customer Group"
		},
		{
			fieldname: "volume",
			label: __("Volume or Qty"),
			fieldtype: "Float"
		},
		{
			fieldname: "aggregate",
			label: __("Show Aggregate"),
			fieldtype: "Check",
			default: 0
		},
		{
			fieldname: "summary",
			label: __("Show Summary"),
			fieldtype: "Check",
			default: 0
		},
		{
			fieldname: "transaction_id",
			label: __("Transaction ID"),
			fieldtype: "Link",
			options: function () {
				var link = frappe.query_report.get_filter_value("report_by")
				return link
			}
		},
	]
}
