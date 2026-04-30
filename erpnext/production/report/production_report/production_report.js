// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Production Report"] = {
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
			"fieldname": "cost_center",
			"label": ("Parent Branch"),
			"fieldtype": "Link",
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
			"on_change": function(){
				var cost_center = frappe.query_report.get_filter_value("cost_center");
				var from_date = frappe.query_report.get_filter_value("from_date");
				var to_date = frappe.query_report.get_filter_value("to_date");
				if(cost_center)
				{
					frappe.call({
						method: "erpnext.production.report.production_report.production_report.get_cc_challan",
						args:{"cost_center":cost_center, "from_date":from_date, "to_date": to_date},
						callback: function(r){
							if(r.message)
							{
								options = []
								for (i = 0; i < r.message.length; i++) { 
									options[i]= r.message[i].challan_no
								}
								let challan = frappe.query_report.get_filter_value("challan_no");
								challan.df.options = options;
								challan.refresh();
								frappe.query_report.refresh();

								// frappe.query_report.filters_by_name.challan_no.refresh();
								// frappe.query_reports["Production Report"].filters[19].options = options
								// frappe.query_report.filters_by_name.challan_no.refresh();
								// frappe.query_report.refresh();
							}
						}
						
					});
				}
			},
			"reqd": 1,
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
			"on_change": function(){
				var branch = frappe.query_report.get_filter_value("branch");
				var from_date = frappe.query_report.get_filter_value("from_date");
				var to_date = frappe.query_report.get_filter_value("to_date")
				if(branch)
				{
					frappe.call({
						method: "erpnext.production.report.production_report.production_report.get_branch_challan",
						args:{"branch":branch, "from_date":from_date, "to_date": to_date},
						callback: function(r){
							if(r.message)
							{
								options = []
								for (i = 0; i < r.message.length; i++) { 
									options[i]= r.message[i].challan_no
								}
								
								let challan = frappe.query_report.get_filter_value("challan_no");
								challan.df.options = options;
								challan.refresh();
								frappe.query_report.refresh();
								// console.log(options)
								// frappe.query_reports["Production Report"].filters[19].options = options
								// frappe.query_report.filters_by_name.challan_no.refresh();
								// frappe.query_report.refresh();
							}
						}
					})
				}

			}
		},
		{
			"fieldname": "location",
			"label": ("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"get_query": function() {
				var branch = frappe.query_report.get_filter_value("branch");
				branch = branch.replace(' - NRDCL','');
				return {
					filters: {
						is_disabled: 0,
						branch: branch,
					}
				};
				// return {"doctype": "Location", "filters": {"branch": branch, "is_disabled": 0}}
			},
			"on_change": function(){
				var location = frappe.query_report.get_filter_value("location")
				var from_date = frappe.query_report.get_filter_value("from_date")
				var to_date = frappe.query_report.get_filter_value("to_date")
				if(location)
				{
					frappe.call({
						method: "erpnext.production.report.production_report.production_report.get_location_challan",
						args:{"location":location, "from_date":from_date, "to_date": to_date},
						callback: function(r){
							if(r.message)
							{
								options = []
								for (i = 0; i < r.message.length; i++) { 
									options[i]= r.message[i].challan_no
								}
								let challan = frappe.query_report.get_filter_value("challan_no");
								challan.df.options = options;
								challan.refresh();
								frappe.query_report.refresh();
							}
						}
					})
				}
			}
		},
		{
			"fieldname": "adhoc_production",
			"label": ("Adhoc Production"),
			"fieldtype": "Link",
 			"options": "Adhoc Production",
			"get_query": function() {
				var loc = frappe.query_report.get_filter_value("location");
				return {
					filters: {
						is_disabled: 0,
						location: loc,
					}
				};
				// return {"doctype": "Adhoc Production", "filters": {"location": loc, "is_disabled": 0}}
			}
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.year_start(),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.year_end(),
			"reqd": 1,
		},
		{
			"fieldname": "item_group",
			"label": ("Material Group"),
			"fieldtype": "Link",
 			"options": "Item Group",
			"get_query": function() {
				return {
					filters: {
						// is_disabled: 0,
						is_group: 1,
					}
				};
				// return {"doctype": "Item Group", "filters": {"is_group": 0, "is_production_group": 1}}
			},
		},
		{
			"fieldname": "item_sub_group",
			"label": ("Material Sub Group"),
			"fieldtype": "Link",
 			"options": "Item Sub Group",
			"get_query": function() {
				var item_group = frappe.query_report.get_filter_value("item_group");
				return {
					filters: {
						// is_disabled: 0,
						item_group: item_group,
					}
				};
				// return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
			}
		},
		{
			"fieldname": "item",
			"label": ("Material"),
			"fieldtype": "Link",
 			"options": "Item",
			"get_query": function() {
				// var sub_group = frappe.query_report.filters_by_name.item_sub_group.get_value();
				var item_sub_group = frappe.query_report.get_filter_value("item_sub_group");
				return {
					filters: {
						is_production_item: 1,
						item_sub_group: item_sub_group,
					}
				};
				// return {"doctype": "Item", "filters": {"item_sub_group": sub_group, "is_production_item": 1}}
			}
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname": "timber_prod_group",
			"label": ("Timber Product Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"get_query": function() {
				return {
					filters: {
						for_report: 1,
					}
				};
					// return {"doctype": "Item Sub Group", "filters": {"for_report": 1}}
			},
			"on_change": function(){
				var item_group = frappe.query_report.get_filter_value("timber_prod_group");
				// frappe.msgprint(branch)
				frappe.call({
					method:"erpnext.selling.report.timber_sales_report.timber_sales_report.get_item_sub_group",
					args:{"item_group":item_group},
					callback: function(r){
						// console.log(r.message)
						// frappe.query_report.filters_by_name.warehouse.set_option(r.message)					
						if(r.message)
						{
							options = []
							for (i = 0; i < r.message.length; i++) { 
								options[i]= r.message[i].name
							}
							// console.log(options)
							// frappe.query_reports["Production Report"].filters[13].options = options
							// frappe.query_report.filters_by_name.tp_sub_group.refresh();
							// frappe.query_report.refresh();
							
							let challan = frappe.query_report.get_filter_value("tp_sub_group");
							challan.df.options = options;
							challan.refresh();
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
			"fieldname": "timber_species",
			"label": ("Timber Species"),
			"fieldtype": "Link",
 			"options": "Timber Species",
			"get_query": function() {
				var item_group = frappe.query_report.get_filter_value("item_group");
				// var timber_prod_group = frappe.query_report.get_filter_value("timber_prod_group");
				
				// if(timber_prod_group)
				// {
				// 	return {"doctype": "Timber Species"}
				// }
				if(!item_group || item_group != "Timber Products") {
					return {
						filters: {
							docstatus: 1,
						}
					};
					// return {"doctype": "Timber Species", "filters": {"docstatus": 5}}
				}
				// else {
				// 	return {"doctype": "Timber Species"}
				// }
			}
		},
		{
			"fieldname": "timber_class",
			"label": ("Timber Class"),
			"fieldtype": "Link",
 			"options": "Timber Class",
			"get_query": function() {
				var item_group = frappe.query_report.get_filter_value("item_group");
				// var timber_prod_group = frappe.query_report.get_filter_value("timber_prod_group");			
				// if(timber_prod_group)
				// {
				// 	return {"doctype": "Timber Class"}
				// }
				// else if (!item_group || item_group != "Timber Products") {
				// 	return {"doctype": "Timber Class", "filters": {"docstatus": 5}}
				// }
				// else {
				// 	return {"doctype": "Timber Class"}
				// }
				if(!item_group || item_group != "Timber Products") {
					return {
						filters: {
							docstatus: 1,
						}
					};
					// return {"doctype": "Timber Species", "filters": {"docstatus": 5}}
				}
			}
		},
		{
			"fieldname": "production_type",
			"label":("Production Type"),
			"fieldtype" : "Select",
			"width" :"80",
			"options": ["All", "Planned","Adhoc"],
			"default": "All",
			"reqd" : 1
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname": "warehouse",
			"label": ("Warehouse"),
			"fieldtype": "Link",
 			"options": "Warehouse",
			 get_query: () => {
				var branch = frappe.query_report.get_filter_value("branch");
				branch = branch.replace(' - NRDCL','');
				if(branch)
				{
					return {
						filters: {
							disabled: 0,
							branch: branch,
						}
					};
				}
				
			},
			// "get_query": function() {
			// 	var branch = frappe.query_report.filters_by_name.branch.get_value();
			// 	branch = branch.replace(' - NRDCL','')
			// 	if (!branch) {
			// 		return
			// 	}
			// 	return {"doctype": "Warehouse", "filters": {"branch": branch, "disabled": 0}}
			// }
		},
		{
			"fieldname": "timber_type",
			"label":("Timber Type"),
			"fieldtype" : "Select",
			"width" :"80",
			"options": ["All", "Conifer","Broadleaf"],
			"default": "All",
			"reqd" : 1
		},
		{
			"fieldname": "show_aggregate",
			"label": ("Show Aggregate Data"),
			"fieldtype": "Check",
 			"default": 1,
		},
		{
			"fieldname": "production_area",
			"label":("Production Area"),
			"fieldtype" : "Select",
			"width" :"80",
			"options": ["All","Normal","Road Alignment","Fire Burnt Area","Transmission Line","Sanitation Work Area","Scientific Thinning Area"],
			"default": "All",
			"reqd" : 1
		},
		{
			"fieldname": "challan_no",
			"label": ("Challan No"),
			"fieldtype": "Select",
			"width": "80",
			"options": [],
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname": "uom",
			"label": ("UOM"),
			"fieldtype": "Link",
 			"options": "UOM"
		},
		{
			"fieldname": "supplier",
			"label": ("Contractor"),
			"fieldtype": "Link",
 			"options": "Supplier"
		},
		{
			"fieldname": "machine_name",
			"label": ("Machine Name"),
			"fieldtype": "Link",
 			"options": "Equipment",
			"get_query": function() {
				var branch = frappe.query_report.get_filter_value("branch");
				var cost_center = frappe.query_report.get_filter_value("cost_center");
				if(branch != "" && branch != null && branch != undefined){
					branch = branch.replace(' - NRDCL','')
					return {
						filters: {
							is_disabled: 0,
							branch: branch,
						}
					};
					// return {"doctype": "Equipment", "filters": {"branch": branch, "is_disabled": 0}}
				}
				else if(cost_center != "" && cost_center != null && cost_center != undefined){
					frappe.call({
						method:"erpnext.production.report.production_report.production_report.get_cost_center_based_equipments",
						args:{"cost_center":cost_center},
						callback: function(r){
							console.log(r.message)
							if(r.message)
							{
								options = []
								for (i = 0; i < r.message.length; i++) { 
									options[i]= r.message[i].name
								}
								return {
									filters: {
										name: options,
									}
								};
								// return {"doctype": "Equipment", "filters": {"name":options}}
							}
							// 	console.log(options)
							// 	frappe.query_reports["Production Report"].filters[13].options = options
							// 	frappe.query_report.filters_by_name.tp_sub_group.refresh();
							// 	frappe.query_report.refresh();
							// 	// **I have set options dynamically to the below select fieldtype but I need to refresh that field to show that new options.**
							// 	// console.log(frappe.query_reports["Stock Balance Report"].filters[4].options)
							// }
						}
					})
				}
				else{
					return {
						filters: {
							disabled: 0,
						}
					};
					// return {"doctype": "Equipment", "filters":{"is_disabled":0}}
				}
			}		
		}
	]
}
