// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Track", {
	refresh(frm) {
        if (frm.doc.customer_status === "C0" && !frm.doc.c0_status) {
            frm.add_custom_button(__('C0 Status Document'),
                () => frm.events.make_c0_status(frm), __('Create'));
        }
        else if (frm.doc.customer_status === "C1" && !frm.doc.c1_status) {
            frm.add_custom_button(__('C1 Status Document'),
                () => frm.events.make_c1_status(frm), __('Create'));
        }
        else if (frm.doc.customer_status === "C2" && !frm.doc.c2_status) {
            frm.add_custom_button(__('C2 Status Document'),
                () => frm.events.make_c2_status(frm), __('Create'));
        }
        if (frm.doc.customer_status === "On Warranty" && !frm.doc.warranty) {
            frm.add_custom_button(__('Warranty Document'),
                () => frm.events.make_warranty(frm), __('Create'));
        }

        if (!frm.doc.c1_status && frm.doc.docstatus == 0)  {
			frm.add_custom_button(__("C0 Status"), function () {
				frm.trigger("create_c0_status");
				},
				__("Create")
			);
		}
	},
    create_c0_status: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.customer_track.customer_track.make_customer_track",
			frm: cur_frm
		})
	},
    make_c0_status: function (frm) {
        frappe.model.open_mapped_doc({
            method: "erpnext.crm.doctype.customer_track.customer_track.make_c0_status",
            frm: frm,
            run_link_triggers: true
        });
    },
    make_c1_status: function (frm) {
        frappe.model.open_mapped_doc({
            method: "erpnext.crm.doctype.customer_track.customer_track.make_c1_status",
            frm: frm,
            run_link_triggers: true
        });
    },
    make_c2_status: function (frm) {
        frappe.model.open_mapped_doc({
            method: "erpnext.crm.doctype.customer_track.customer_track.make_c2_status",
            frm: frm,
            run_link_triggers: true
        });
    },
    make_warranty: function (frm) {
        frappe.model.open_mapped_doc({
            method: "erpnext.crm.doctype.customer_track.customer_track.make_warranty",
            frm: frm,
            run_link_triggers: true
        });
    },
});
