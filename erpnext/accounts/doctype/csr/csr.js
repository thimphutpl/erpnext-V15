// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("CSR", {
	refresh(frm) {
        frm.add_custom_button(__('Accounting Ledger'), function() {
            frappe.route_options = {
                voucher_no: frm.doc.stock_entrys,// Change to relevant field in CSR
            };
            frappe.set_route("query-report", "General Ledger");
        }, __("View"));

        // Button to view Stock Ledger
        frm.add_custom_button(__('Stock Ledger'), function() {
            frappe.route_options = {
                voucher_no: frm.doc.stock_entrys, // Change to relevant field in CSR
                 // Change to relevant field in CSR
            };
            frappe.set_route("query-report", "Stock Ledger");
        }, __("View"));
    
	},
});
