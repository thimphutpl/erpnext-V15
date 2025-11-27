// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("C0 Status", {
	refresh(frm) {
        // if (!frm.doc.c1_status && frm.doc.docstatus == 1 && frm.doc.workflow_state == "Approved")  {
        if (!frm.doc.c1_status && frm.doc.docstatus == 1)  {
			frm.add_custom_button(__("C1 Status"), function () {
				frm.trigger("create_c1_status");
				},
				__("Create")
			);
		}
	},
    create_c1_status: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.c0_status.c0_status.make_c0_status",
			frm: cur_frm
		})
	},
});
