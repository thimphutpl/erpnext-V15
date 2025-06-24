// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// cur_frm.add_fetch("branch", "revenue_bank_account", "income_account")

frappe.ui.form.on('Mechanical Payment', {
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
    }
});

function calculate_totals(frm) {
    if (frm.doc.receivable_amount) {
        frm.set_value("net_amount", flt(frm.doc.receivable_amount) - flt(frm.doc.tds_amount));
        frm.refresh_field("net_amount");
    }
}

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

frappe.ui.form.on('Mechanical Payment', {
    refresh: function(frm) {
        // Add custom logic if required
    }
});

// frm.fields_dict['items'].grid.get_field('reference_name').get_query = function(frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//     return {
//         filters: {
//             "docstatus": 1,
//             "branch": frm.branch,
//             "customer": frm.customer,
//             "outstanding_amount": [">", 0]
//         }
//     };
// };
