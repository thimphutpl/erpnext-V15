// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Close Work Report"] = {
	"filters": [
		{
			fieldname: "broad_head",
			label: __("Broad Head"),
			fieldtype: "Link",
			options: "Account",
			get_query: function () {
				return {
					filters: {
						is_group: 1,
					}
				};
			}
		},
        {
            "fieldname": "account",
            "label": "Account",
            "fieldtype": "Link",
            "options": "Account"
        },
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        }

	]
};
