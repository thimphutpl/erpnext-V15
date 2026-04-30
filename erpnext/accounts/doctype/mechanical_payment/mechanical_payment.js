// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// cur_frm.add_fetch("branch", "revenue_bank_account", "income_account")

frappe.ui.form.on('Mechanical Payment', {
    onload: function(frm) {
        create_custom_buttons(frm);
    },
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Accounting Ledger'), function() {
                frappe.route_options = {
                    voucher_no: frm.doc.name,
                    from_date: frm.doc.posting_date,
                    to_date: frm.doc.posting_date,
                    company: frm.doc.company,
                    group_by_voucher: false
                };
                frappe.set_route("query-report", "General Ledger");
            }, __("View"));
        }
        create_custom_buttons(frm);
    },

    "tds_amount": function(frm) {
        calculate_totals(frm);
        frm.toggle_reqd("tds_account", frm.doc.tds_amount);
    },

    get_series: function(frm) {
        frappe.call({
            method: "get_series",
            doc: frm.doc,
            callback: function(r) {
                frm.reload_doc();
            }
        });
    },

    get_transactions: function(frm) {
        frappe.call({
            method: "get_transactions",
            doc: frm.doc,
            callback: function(r) {
                frm.refresh_field("items");
                frm.refresh_fields();
            },
            freeze: true,
            freeze_message: "Fetching Transactions... Please Wait"
        });
    },

    tax_withholding_category: function(frm) {
        frappe.call({
            method: "get_tax_rate",
            doc: frm.doc,
            callback: function(r) {
                frm.refresh_field("items");
                frm.refresh_fields();
            },
            freeze: true,
            freeze_message: "Fetching Transactions... Please Wait"
        });
    },

    "receivable_amount": function(frm) {
        if (frm.doc.receivable_amount > frm.doc.actual_amount) {
            frm.set_value("receivable_amount", frm.doc.actual_amount);
            frappe.msgprint("Receivable Amount cannot be greater than the Total Payable Amount");
        } else {
            calculate_totals(frm);
            let total = frm.doc.receivable_amount;
            frm.doc.items.forEach(function(d) {
                let allocated = 0;
                if (total > 0 && total >= d.outstanding_amount) {
                    allocated = d.outstanding_amount;
                } else if (total > 0 && total < d.outstanding_amount) {
                    allocated = total;
                } else {
                    allocated = 0;
                }
                d.allocated_amount = allocated;
                total -= allocated;
            });
            frm.refresh_field("items");
        }
    },

    "items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
        let row = frm.open_grid_row();
        row.grid_form.fields_dict.reference_type.set_value(frm.doc.payment_for);
        row.grid_form.fields_dict.reference_type.refresh();
    },
    get_delivery_note: function(frm) {
		get_delivery_notes(frm);
	},
    
});

function calculate_totals(frm) {
    if (frm.doc.receivable_amount) {
        frm.set_value("net_amount", flt(frm.doc.receivable_amount) - flt(frm.doc.tds_amount));
        frm.refresh_field("net_amount");
    }
}

function get_delivery_notes(frm){
    if (frm.doc.transporter || frm.doc.vehicle){
            return frappe.call({
                    method: "get_delivery_note_list",
                    doc: frm.doc,
                    callback: function(r, rt){
                //             if(r.message){
                // console.log(r.message);
                //                     var total_amount = 0;
                //                     console.log(r.message);
                //                     frm.clear_table("transporter_payment_item");
                //                     r.message.forEach(function(rec) {
                //                             var row = frappe.model.add_child(frm.doc, "Transporter Payment Item", "transporter_payment_item");
                //                             row.delivery_note = rec['delivery_note'];
                //                             row.vehicle = rec['vehicle'];
                //                             row.amount = rec['amount'];
                //                             total_amount += rec['amount'];
                //                     });
                //                     frm.set_value("receivable_amount", total_amount);
                //             }else{
                //                   frm.clear_table("transporter_payment_item");
                //                   frappe.msgprint("No Delivery Note for the above selected vehicle or transporter");
                //             }
                //             frm.refresh();
                //     },
                
                    frm.refresh_field("transporter_payment_item");
                    frm.refresh_fields();
                },
                freeze: true,
                freeze_message: "Fetching Delivery Note... Please Wait"
            });
    }else{
            frappe.msgprint("To retrieve Delivery Note, Please Provide Transporter or Vehicle no");
    }
}

frappe.ui.form.on("Transporter Payment Item", {
    "delivery_note": function(frm, cdt, cdn){
        var items = frm.doc.transporter_payment_item;
        var total = 0;
        for(var i = 0; i < items.length ; i++){
                   total += parseFloat(items[i].amount);
              }
        frm.set_value('receivable_amount', total);
        calculate_totals(frm);
    }
})

frappe.ui.form.on("Mechanical Payment Item", {
    "reference_name": function(frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        let rec_amount = flt(frm.doc.receivable_amount);
        let act_amount = flt(frm.doc.actual_amount);
        if (item.reference_name) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: item.reference_type,
                    fieldname: ["outstanding_amount"],
                    filters: {
                        name: item.reference_name
                    }
                },
                callback: function(r) {
                    frappe.model.set_value(cdt, cdn, "outstanding_amount", r.message.outstanding_amount);
                    frappe.model.set_value(cdt, cdn, "allocated_amount", r.message.outstanding_amount);
                    frm.refresh_field("outstanding_amount");
                    frm.refresh_field("allocated_amount");

                    frm.set_value("actual_amount", act_amount + flt(r.message.outstanding_amount));
                    frm.refresh_field("actual_amount");
                    frm.set_value("receivable_amount", rec_amount + flt(r.message.outstanding_amount));
                    frm.refresh_field("receivable_amount");
                }
            });
        }
    },

    "before_items_remove": function(frm, cdt, cdn) {
        let doc = locals[cdt][cdn];
        let amount = flt(frm.doc.receivable_amount);
        let ac_amount = flt(frm.doc.actual_amount) - flt(doc.outstanding_amount);
        frm.set_value("actual_amount", ac_amount);
        frm.refresh_field("actual_amount");
        frm.trigger("receivable_amount");
    }
});


/* ePayment Begins */
var create_custom_buttons = function(frm){
	if(frm.doc.docstatus == 1 && (frm.doc.voucher_type == "Bank Entry" || frm.doc.voucher_type == "Contra Entry") && frm.doc.mode_of_payment == "Bank Payment" && frm.doc.payment_status != "Payment Successful"){
		if(!frm.doc.bank_payment || frm.doc.payment_status == 'Failed' || frm.doc.payment_status == 'Payment Failed'){
			frm.page.set_primary_action(__('Process Payment'), () => {
				frappe.model.open_mapped_doc({
					method: "erpnext.accounts.doctype.journal_entry.journal_entry.make_bank_payment",
					frm: cur_frm
				});
			});
		}
	}
}
/* ePayment Ends */