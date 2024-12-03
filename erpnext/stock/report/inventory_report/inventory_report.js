// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Inventory Report"] = {
    "filters": [
        {
            fieldname: "report_type",
            label: __("Select Report"),
            fieldtype: "Select",
            options: [
                "Inventory Report",
                "Inventory Summary",
                "Non Moving Branch Wise",
                "Consumption Report"
            ],
            default: "Inventory Report",
            reqd: 1,
            on_change: function(query_report) {
                query_report.refresh();
            }
        }
    ],

    onload: function(report) {
        frappe.query_report.refresh();
    },

    get_data: function(filters) {
        const selected_report = filters.report_type;

        switch (selected_report) {
            case "Inventory Report":
                // return this.get_inventory_report_data();
                return this.StockBalanceReport();
            case "Inventory Summary":
                return this.get_inventory_summary_data();
            case "Non Moving Branch Wise":
                return this.get_non_moving_branch_data();
            case "Report 4":
                return this.get_report_4_data();
            default:
                // return this.get_inventory_report_data(); // Default to Report 1
                return this.StockBalanceReport(); // Default to Report 1
        }
    },

    // get_inventory_report_data: function() {
    //     return frappe.call({
    //         method: "erpnext.stock.report.inventory_report.inventory_report.get_inventory_report_data",
    //         callback: function(r) {
    //             return r.message;
    //         }
    //     });
    // },

    StockBalanceReport: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.StockBalanceReport",
            callback: function(r) {
                return r.message;
            }
        });
    },

    get_inventory_summary_data: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.get_inventory_summary_data",
            callback: function(r) {
                return r.message;
            }
        });
    },

    get_non_moving_branch_data: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.get_non_moving_branch_data",
            callback: function(r) {
                return r.message;
            }
        });
    },

    get_report_4_data: function() {
        return frappe.call({
            method: "erpnext.stock.report.inventory_report.inventory_report.get_report_4_data",
            callback: function(r) {
                return r.message;
            }
        });
    }
};
