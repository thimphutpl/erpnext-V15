// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Document Approver", {
	// refresh(frm) {
        
	// },
	setup: function (frm) {
        frm.set_query("cost_center", "items", function (doc) {
			return {
				filters: { is_group: 0 },
			};
		});
	},
});
