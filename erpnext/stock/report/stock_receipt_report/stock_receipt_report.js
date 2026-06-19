// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Receipt Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Link",
 			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"purpose",
			"label": __("Purpose"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["Material Receipt", "Material Transfer"],
			"reqd": 1
		},
		{
            "fieldname": "cost_center",
            "label": __("Parent Cost Center"),
			"fieldtype": "Link",
            "width": "80",
			"options": "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						disabled: 0,
						company: company,
						is_group: 1
					}
				};
			},
			// "on_change": function(){
			// 	var cost_center = frappe.query_report.get_filter_value("cost_center");
			// 	var from_date = frappe.query_report.get_filter_value("from_date");
			// 	var to_date = frappe.query_report.get_filter_value("to_date");
			// 	if(cost_center)
			// 	{
			// 		frappe.call({
			// 			method:"erpnext.stock.report.stock_balance_report.stock_balance_report.get_warehouse",
			// 			args:{"cost_center":cost_center, "from_date":from_date, "to_date": to_date},
			// 			callback: function(r){
			// 				if(r.message)
			// 				{
			// 					options = []
			// 					for (i = 0; i < r.message.length; i++) { 
			// 						options[i]= r.message[i].warehouse
			// 					}
			// 					let warehouse = frappe.query_report.get_filter_value("warehouse");
			// 					warehouse.df.options = options;
			// 					warehouse.refresh();
			// 					frappe.query_report.refresh();

			// 					// frappe.query_report.filters_by_name.challan_no.refresh();
			// 					// frappe.query_reports["Production Report"].filters[19].options = options
			// 					// frappe.query_report.filters_by_name.challan_no.refresh();
			// 					// frappe.query_report.refresh();
			// 				}
			// 			}
						
			// 		});
			// 	}
			// },
		},
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
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
				}
			},
			// "on_change": function(){
			// 	var branch = frappe.query_report.get_filter_value("branch");
			// 	frappe.call({
			// 		method:"erpnext.stock.report.stock_balance_report.stock_balance_report.get_warehouse",
			// 		args:{"branch":branch, "from_date":from_date, "to_date": to_date},
			// 		callback: function(r){
			// 			if(r.message)
			// 			{
			// 				options = []
			// 				for (i = 0; i < r.message.length; i++) { 
			// 					options[i]= r.message[i].warehouse
			// 				}
							
			// 				let warehouse = frappe.query_report.get_filter_value("warehouse");
			// 				warehouse.df.options = options;
			// 				warehouse.refresh();
			// 				frappe.query_report.refresh();
			// 			}
			// 		}
			// 	})

			// }
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.year_start(),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Warehouse"
		},

		{
			"fieldname": "item_code",
			"label": __("Material Code"),
			"fieldtype": "Link",
			"width": "80",
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
			"fieldname": "uom",
			"label": ("UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
		{
			"fieldname": "lot_number",
			"label": __("Lot Number"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Lot List"
		}

	]
}
