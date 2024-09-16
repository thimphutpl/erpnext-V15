// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Gift Register Report"] = {
	filters: [
		{
			fieldname: "name",
			label: __("Name"),
			fieldtype:'Data',
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Select",
			options: ['','2022', '2023', '2024'],
			
		}
	],
	"onload": function (report){
		report.page.fields_dict['fiscal_year'].$input.on('change', function () {
			report.refresh();
        });
        report.page.fields_dict['to_date'].$input.on('change', function () {
			
            report.refresh();
        });
        report.page.fields_dict['from_date'].$input.on('change', function () {
			
            report.refresh();
        });
		report.page.fields_dict['name'].$input.on('change', function () {
			
            report.refresh();
        });
    }
  
	
};
