// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["COP Report"] = {
	"filters": [
		{
			fieldname: "price_list",
			label: __("Price Liist"),
			fieldtype: "Link",
			width: "80",
			options: "Price List",
			
		},
		{
			fieldname: "item_code",
			label: __("Item Code"),
			fieldtype: "Link",
			width: "80",
			options: "Item",
			
		},
		{
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Int",
            default: new Date().getFullYear(),
            onchange: function () {
                frappe.query_report.refresh();
            }
        },
	],
	
	onload: function (report) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Item Price",
                fields: ["item_code", "price_list", "valid_from", "valid_upto", "price_list_rate"],
            },
            callback: function (r) {
                if (r.message) {
                    console.log("Loaded data:", r.message);
                }
            }
        });
    },

    get_data: function (filters) {
        const { item_code, year } = filters;
        if (!item_code) {
            frappe.throw(__("Item Code is required to filter the data."));
        }

        frappe.call({
            method: "your_app.your_module.your_python_method",
            args: { filters },
            callback: function (response) {
                if (response.message) {
                    const filteredData = response.message;
                    console.log("Filtered data:", filteredData);
                    // Render or process data as needed
                }
            }
        });
    }
};
