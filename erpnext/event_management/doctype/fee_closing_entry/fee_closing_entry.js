// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fee Closing Entry", {
    setup(frm) {
        frm.set_query("location", function(){
			return {
				filters: {
					'disabled': 0,
					'is_recreational_park': 1,
				}
			}
		});
    },

	refresh(frm) {

	},

    cashier: function(frm){
        frm.trigger("get_reference_document");
    },

    get_reference_document: function(frm) {
		reset_values(frm);
        if (frm.doc.location) {
            return frappe.call({
                method: 'erpnext.event_management.doctype.fee_closing_entry.fee_closing_entry.get_reference_document',
                args: {
                    date: frm.doc.posting_date,
                    location: frm.doc.location,
                    cashier: frm.doc.cashier
                },
                callback: function(r) {
                    let docs = r.message;
                    set_form_data(docs, frm);
				    refresh_fields(frm);
                }
            })
            
        }
    },

});

function reset_values(frm) {
	frm.set_value("references", []);
	frm.set_value("payments", []);
	frm.set_value("grand_total", 0);
}

function set_form_data(data, frm) {
	data.forEach((d) => {
		add_reference_docs(d, frm);
		frm.doc.grand_total += flt(d.grand_total);
		refresh_payments(d, frm, true);
	});
}

function add_reference_docs(d, frm) {
	frm.add_child("references", {
		reference_name: d.name,
		posting_date: d.posting_date,
		grand_total: d.grand_total,
	});
}

function refresh_payments(d, frm, is_new) {
	d.transaction_details.forEach((p) => {
		const payment = frm.doc.payments.find(
			(pay) => pay.mode_of_payment === p.mode_of_payment
		);
		if (payment) {
			if (is_new) payment.amount += flt(p.amount);
		} else {
			frm.add_child("payments", {
				mode_of_payment: p.mode_of_payment,
				amount: p.amount,
			});
		}
	});
}

function refresh_fields(frm) {
	frm.refresh_field("references");
	frm.refresh_field("payments");
	frm.refresh_field("grand_total");
}