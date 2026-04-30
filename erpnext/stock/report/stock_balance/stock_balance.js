// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance"] = {
	filters: [
		{
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Link",
 			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_code",
			"label": __("Material Code"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
		},
		{
            "fieldname": "cost_center",
            "label": __("Parent Cost Center"),
			"fieldtype": "Link",
            "width": "80",
			"options": "Cost Center",
			"get_query": function() {
				var company = frappe.query_report.get_filter_value('company');
				return {
						'doctype': "Cost Center",
						'filters': [
								['disabled', '!=', '1'],
								['company', '=', company],
								['is_group', '=', '1']
						]
				}
			},
		},
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
					var cost_center = frappe.query_report.get_filter_value('cost_center');
					var company = frappe.query_report.get_filter_value('company');
					if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
					{
							return {"doctype": "Cost Center", "filters": {"company": company, "disabled": 0, "parent_cost_center": cost_center}}
					}
					else
					{
							return {"doctype": "Cost Center", "filters": {"company": company, "disabled": 0, "is_group": 0}}
					}
			},
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
			get_query: function () {
                let branch = frappe.query_report.get_filter_value('branch');

                if (!branch) {
                    return {};
                }

                return {
                    query: "erpnext.stock.report.stock_balance.stock_balance.get_filtered_warehouse",
                    filters: {
                        branch: branch
                    }
                };
            }
		},
		{
			"fieldname": "item_group",
			"label": __("Material Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		{
			"fieldname": "item_sub_group",
			"label": __("Material Sub Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Sub Group",
			"get_query":function(){
				var item_group = frappe.query_report.get_filter_value('item_group');
				return {
					'doctype': "Item Sub Group",
					'filters': [
						['item_group', '=', item_group],
					]
				}
			} 
		},
		{
			"fieldname": "timber_prod_group",
			"label": ("Timber Product Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group",
		},
		{
			"fieldname": "tp_sub_group",
			"label": ("Timber Product Sub Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group",
			// "get_query": function() {
			// 		var item_group = "Timber Products";
			// 		return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
			// }
		},
		{
			"fieldname":"timber_class",
			"label": __("Timber Class"),
			"fieldtype": "Link",
			"options": "Timber Class"
		},
		{
			"fieldname": "uom",
			"label": ("UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
	]
}
