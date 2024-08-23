// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Resource Status"] = {
	"filters": [
		{
			fieldname:"from_date_time",
			label: __("From Date Time"),
			fieldtype: "Datetime",
			default:'',
		},
		{
			fieldname:"to_date_time",
			label: __("To Date Time"),
			fieldtype: "Datetime",
			default: ''
		},
		{
			fieldname:"agency",
			label: __("Agency"),
			fieldtype: "Link",
			options:"Cost Center",
			default: "",
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
        },
		{
			fieldname:"hall_item",
			label: __("Hall Item"),
			fieldtype: "MultiSelectList",
			options: "Hall Items",
			get_data: function () {
				return frappe.db.get_link_options("Hall Items");
			},
			default: "",
			
		}
		

	]
};
