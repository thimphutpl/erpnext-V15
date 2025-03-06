// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Received Entries", {
	refresh(frm) {

	},
    is_existing_asset(frm){
        frm.set_value("ref_doc", null);
        frm.set_value("existing_pr_reference", null);
        frm.refresh_fields();
    }
});
