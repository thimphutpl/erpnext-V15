// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.query_reports["Quotation Comparative Statement"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Quotation Comparative Statement"] = {
    filters: [
        {
            fieldname: "request_for_quotation",
            label: __("Request for Quotation"),
            fieldtype: "Link",
            options: "Request for Quotation",
            reqd: 1,
            get_query: function() {
                return {
                    filters: {
                        docstatus: 1 // Only fetch RFQs that are submitted
                    }
                };
            }
        }
    ]
};

