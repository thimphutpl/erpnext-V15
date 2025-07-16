// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Sub Category", {
    setup(frm){
        // Set query for asset_category based on company
        frm.set_query("asset_category", function() {
            return {
                filters: {
                    "company": frm.doc.company
                }
            };
        });
    },

	refresh(frm) {

	},
    company: function(frm) {
        // Clear asset_category when company changes
        frm.set_value("asset_category", "");
        frm.refresh_field("asset_category");
    }
});
