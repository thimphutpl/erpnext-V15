cur_frm.add_fetch("branch", "cost_center", "cost_center");
frappe.ui.form.on('Expense Invoice', {
    refresh(frm) {
        // child table field hide
        frm.fields_dict["item"].grid.update_docfield_property(
            "consumer_code",
            "hidden",
            1
        );

        frm.refresh_field("item");
        let allowed_roles = ['Account Manager', 'System Manager'];
        let user_roles = frappe.user_roles;

        if (!user_roles.some(r => allowed_roles.includes(r))) {
            frm.set_df_property('direct_payment', 'hidden', true);
        } else {
            frm.set_df_property('direct_payment', 'hidden', false);
        }
    },
    "tds_percent": function (frm) {
        calculate_tds(frm);
    },


});

function calculate_tds(frm) {
    frappe.call({
        method: "erpnext.accounts.doctype.direct_payment.direct_payment.get_tds_account",
        args: {
            percent: frm.doc.tds_percent,
            payment_type: "Payment"
        },
        callback: function (r) {
            if (r.message) {
                frm.set_value("tds_account", r.message);
                cur_frm.refresh_field("tds_account");
            }
        }
    })
}

frappe.ui.form.on('Utility Bill Item', {
    invoice_amount: function (frm, cdt, cdn) {
        calculate_net_amount(frm, cdt, cdn);
    },
    tds_applicable: function (frm, cdt, cdn) {
        calculate_net_amount(frm, cdt, cdn);
    },
});


function calculate_net_amount(frm, cdt, cdn) {
    var item = frappe.get_doc(cdt, cdn);
    var net_amount = 0.00; var tds_amount = 0.00; var total_inv_amount = 0.00; var total_tds_amount = 0.00; var total_net_amount = 0.00;
    if (item.invoice_amount > 0) {
        if (frm.doc.tds_percent > 0 && item.tds_applicable) {
            tds_amount = parseFloat(item.invoice_amount) * parseFloat(frm.doc.tds_percent / 100);
        } else {
            frappe.model.set_value(cdt, cdn, "tds_amount", 0.00);
        }

        net_amount = parseFloat(item.invoice_amount) - parseFloat(tds_amount);

        frappe.model.set_value(cdt, cdn, "net_amount", net_amount);
        frappe.model.set_value(cdt, cdn, "tds_amount", tds_amount);
    }
    frm.doc.item.forEach(function (d) {
        total_inv_amount += parseFloat(d.invoice_amount);
        total_net_amount += parseFloat(d.net_amount);
        total_tds_amount += parseFloat(d.tds_amount);
    });
    frm.set_value("total_bill_amount", total_inv_amount);
    frm.set_value("total_tds_amount", total_tds_amount);
    frm.set_value("net_payable_amount", total_net_amount);
}
