// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Stock Ledger"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
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
			"fieldname":"item_code",
			"label": __("Material Code"),
			"fieldtype": "Link",
			"options": "Item"
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
			"fieldname": "uom",
			"label": __("UOM"),
			"fieldtype": "Link",
			"width": "80",
			"options": "UOM"
		},
		{
			"fieldname": "timber_prod_group",
			"label": ("Timber Product Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"get_query": function() {
					return {"doctype": "Item Sub Group", "filters": {"for_report": 1}}
			},
			"on_change": function(){
				var item_group = frappe.query_report.get_filter_value('timber_prod_group');
				frappe.call({
					method:"erpnext.selling.report.timber_sales_report.timber_sales_report.get_item_sub_group",
					args:{"item_group": item_group},
					callback: function(r){
						// console.log(r.message)
						// frappe.query_report.filters_by_name.warehouse.set_option(r.message)					
						if(r.message)
						{
							let options = []
							for (let i = 0; i < r.message.length; i++) { 
								options[i]= r.message[i].name
							}
							// console.log(options)
							frappe.query_reports["Stock Ledger"].filters[10].options = options
							frappe.query_report.get_filter('tp_sub_group').refresh();
							frappe.query_report.refresh();
							// **I have set options dynamically to the below select fieldtype but I need to refresh that field to show that new options.**
							// console.log(frappe.query_reports["Stock Balance Report"].filters[4].options)
						}
					}
					/*	console.log(r.message)
						$.each(r.message, function(i, data){
							$('.input-with-feedback').append(new Option(data.name))
						});
					frappe.query_reports.filters[1].refresh();
					} */
				});
			}
		},
		{
			"fieldname": "tp_sub_group",
			"label": ("Timber Product Sub Group"),
			"fieldtype": "Select",
			"options": [],
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
			"fieldname": "transaction_type",
			"label": __("Transaction Type"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["Stock Entry", "Raw Materials", "Production", "Delivery Note", "Stock Reconciliation", "Purchase Receipt"]
		},
		{
			"fieldname":"voucher_no",
			"label": __("Voucher #"),
			"fieldtype": "Data"
		}
	]
}
