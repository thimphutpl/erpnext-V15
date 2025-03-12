// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Pass Registry", {
	refresh(frm) {
		frm.set_query("location", function(){
			return {
				filters: {
					'disabled': 0,
					'is_recreational_park': 1,
				}
			}
		});
	},
});

frappe.ui.form.on("Visitor Pass Registry Item", {
    qty: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

	ticket_price: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

	calculate: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
		let csr_qty = flt(row.no_of_visitors) - flt(row.qty)
		
        frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.ticket_price));
        frappe.model.set_value(cdt, cdn, "csr_amount", flt(csr_qty) * flt(row.ticket_price));
    },
});
