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
			fieldname: "cost_center",
			label: __("Parent Branch"),
			fieldtype: "Link",
			options: "Cost Center", 
			reqd: 1,
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						disabled: 0,
						company: company,
						is_group: 1
					}
				};
			}
		},
		{
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: () => {
				var cost_center = frappe.query_report.get_filter_value("cost_center")
				var company = frappe.query_report.get_filter_value("company")
				if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
				{
					return {
						filters: {
							disabled: 0,
							company: company,
							parent_cost_center: cost_center
						}
					};
					// return {"doctype": "Cost Center", filters: {"company": company, "is_disabled": 0, "parent_cost_center": cost_center}}
				}
				else
				{
					return {
						filters: {
							disabled: 0,
							company: company,
							is_group: 0
						}
					};
					// return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "is_group": 0}}
				}
			}
		},
		{
			fieldname: "location",
			label: __("Location"),
			fieldtype: "Link",
			options: "Location",
			get_query: () => {
				var branch = frappe.query_report.get_filter_value("branch")
				branch = branch.replace(' - NRDCL','');
				return {
					filters: {
						is_disabled: 0,
						branch: branch
					}
				};
				// return {"doctype": "Location", "filters": {"branch": branch, "is_disabled": 0}}
			}
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
						// is_production_group: 1,
						is_group: 1
					}
				};
				// return {"doctype": "Item Group", "filters": {"is_group": 0, "is_production_group": 1}}
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
						is_production_item: 1
					}
				};
				// return {"doctype": "Item", "filters": {"item_sub_group": sub_group, "is_production_item": 1}}
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
			options: ["Sales Order","Delivery Note","Sales Invoice"],
			default: "Sales Order",
		},
		{
			fieldname: "transaction_type",
			label: __("Transaction Type"),
			fieldtype: "Select",
			width: "80",
			options: ["","Is Allotment", "Is Credit Sale", "Is Rural Sale", "Is Export", "Is Kidu Sale", "None"],
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
		// {
		// 	fieldname: "uom",
		// 	label: __("UOM"),
		// 	fieldtype: "Link",
		// 	options: "UOM"
		// },
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
			fieldname: "has_challan_cost",
			label: __("Has Challan Cost"),
			fieldtype: "Check",
			default: 0
		},
		{
			fieldname: "has_loading_cost",
			label: __("Has Loading Cost"),
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
