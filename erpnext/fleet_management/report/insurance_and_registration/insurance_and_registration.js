// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
let i=1
frappe.query_reports["Insurance and Registration"] = {
	"filters": [
		{
			fieldname:"company", 
			label:__("Company"), 
			fieldtype:"Link", 
			options:"Company", 
			default: frappe.defaults.get_default("company"),
		},
		{
			fieldname:"equipment",
			label: __("Vehicle"),
			fieldtype:"Link", 
			options:"Equipment",
			get_query: () => {
				return {
					filters: {
						company:frappe.query_report.get_filter_value('company')
					}
				}
			}
		},
	],
	// formatter:function (value, row, column, data, default_formatter) {
		
		
	// 	value = default_formatter(value, row, column, data);
	// 	console.log(value)
	// 	return value
	// },
	get_datatable_options(options) {
		
		delete options['cellHeight']
		// change datatable options
		return Object.assign(options, {
			dynamicRowHeight: true,
			cellHeight: 70			
		});
	},
	


};
