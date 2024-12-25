// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Compact Review", {
	refresh(frm) {
        if ( 1 ) {
			frm.add_custom_button("Create Compact Evaluation", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.compact_agreement.doctype.compact_review.compact_review.make_compact_evaluation",
					frm: frm
				});
			});
		}
	},
});
