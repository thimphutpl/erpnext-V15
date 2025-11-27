// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("C1 Status", {
	refresh(frm) {
        if (!frm.doc.c2_status && frm.doc.docstatus == 1)  {
			frm.add_custom_button(__("C2 Status"), function () {
				frm.trigger("create_c2_status");
				},
				__("Create")
			);
		}
	},
    create_c2_status: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.c1_status.c1_status.make_c1_status",
			frm: cur_frm
		})
	},
});
