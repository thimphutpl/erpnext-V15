// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Compact Setup", {
	refresh: function(frm) {
		// Check if the user has the PMS Compact Approver role
		if (frappe.user.has_role("Head of OPM")) {
			frm.add_custom_button("Create Compact Review", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.compact_agreement.doctype.compact_setup.compact_setup.make_compact_review",
					frm: frm
				});
			});
			
			// // Add button for Compact Evaluation if needed
			// frm.add_custom_button("Create Compact Evaluation", function() {
			// 	frappe.model.open_mapped_doc({
			// 		method: "erpnext.compact_agreement.doctype.compact_setup.compact_setup.make_compact_evaluation",
			// 		frm: frm
			// 	});
			// });
		}
	},
});

// frappe.ui.form.on("Compact Setup", {
// 	refresh: function(frm) {
// 		if ( 1 ) {
// 			frm.add_custom_button("Create Compact Review", function() {
// 				frappe.model.open_mapped_doc({
// 					method: "erpnext.compact_agreement.doctype.compact_setup.compact_setup.make_compact_review",
// 					frm: frm
// 				});
// 			});
// 		}

// 	},
// });


