// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("C2 Status", {
	refresh(frm) {
        if (!frm.doc.sales_order && frm.doc.docstatus == 1)  {
			frm.add_custom_button(__("Sales Order"), function () {
				frm.trigger("create_sales_order");
				},
				__("Create")
			);
		}
	},
    create_sales_order: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.c2_status.c2_status.make_c2_status",
			frm: cur_frm
		})
	},
});
