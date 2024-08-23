// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Resouce Sharing Report"] = {
	"filters": [
		
		{
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Datetime",
			default:'',
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Datetime",
			default: ''
		},
		{
			fieldname:"resource_type",
			label: __("Resource Type"),
			fieldtype: "Link",
			options:"Resource Type",
			
			default: "",
		},
		{
            fieldname: "resource",
            label: __("Resource Name"),
            fieldtype: "Link",
            options: "Resource Directory",
            get_query: () => {
                let resource_type = frappe.query_report.get_filter_value('resource_type');
                if (resource_type) {
                    return {
                        filters: {
                            resource_type: resource_type
                        }
                    };
                }
            }
        }


	]
};
