// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.query_reports["Contract Detail Report"] = {
  filters: [
    {
      fieldname: "contract",
      label: __("Contract"),
      fieldtype: "Link",
      options: "Contract Details"
    },
    
    {
      fieldname: "status",
      label: __("Status"),
      fieldtype: "Select",
      options: "\nActive\nClosed\nTerminated"
    }
  ]
};
