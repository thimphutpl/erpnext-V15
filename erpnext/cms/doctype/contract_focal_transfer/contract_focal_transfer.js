// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract Focal Transfer", {
	onload(frm) {
		// default posting_date for new docs only
		if (frm.is_new() && !frm.doc.posting_date) {
			frm.set_value("posting_date", frappe.datetime.get_today());
		}
	},

	contract(frm) {
		// only fetch old focal in draft
		if (frm.doc.docstatus !== 0) return;

		if (!frm.doc.contract) {
			frm.set_value("focal_person", null);
			frm.set_value("focal_person_name", null);
			return;
		}

		frappe.db.get_value(
			"Contract Details",
			frm.doc.contract,
			["focal_person", "focal_person_name"]
		).then(r => {
			if (!r.message) return;
			frm.set_value("focal_person", r.message.focal_person);
			frm.set_value("focal_person_name", r.message.focal_person_name);
		});
	}
});
