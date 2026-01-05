// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Daily Sales", {
	refresh(frm) {

	},
    get_daily_sales_record(frm) {
        frappe.call({
            method: "get_daily_sales_record",
            doc: frm.doc,
            callback: function(r){
                frm.refresh_field("daily_sales_record");
            }
        })
    }
});
