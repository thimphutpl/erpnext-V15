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

frappe.ui.form.on('Customer Quotation Details', {
    // rate: function(frm, cdt, cdn) {
    //     calculate_amount(frm, cdt, cdn);
    // },
    // quantity: function(frm, cdt, cdn) { // Note: 'qty' is the standard field name, not 'quantity'
    //     calculate_amount(frm, cdt, cdn);
    // }
    amount: function(frm, cdt, cdn) {
        update_item_amount(frm, cdt, cdn);
        calculate_payable_amount(frm);
    },
    discount_amount: function(frm, cdt, cdn) {
        update_item_amount(frm, cdt, cdn);
        calculate_payable_amount(frm);
    },
    items_add: function(frm, cdt, cdn) {
        calculate_payable_amount(frm);
    },
    items_remove: function(frm, cdt, cdn) {
        calculate_payable_amount(frm);
    }
});

function update_item_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.amount && row.discount_amount) {
        row.net_price = flt(row.amount) - flt(row.discount_amount);
        refresh_field('net_price', cdn, 'items');
    }
}
