// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center");
cur_frm.add_fetch("utility_services", "expense_account", "expense_account");
cur_frm.add_fetch("utility_services", "bank_account", "bank_account");
cur_frm.add_fetch("utility_service_type", "party", "party");
cur_frm.add_fetch("utility_service_type", "expense_account", "debit_account");
frappe.ui.form.on('Utility Bill', {
    setup: function (frm) {



        frm.set_query("branch", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    disabled: 0
                }
            };
        });

    },

    onload: function (frm) {
        if (frm.doc.workflow_state != "Draft" && !cur_frm.doc.__islocal) {
            cur_frm.set_df_property("item", "disabled", 1);
            cur_frm.set_df_property("utility_services", "read_only", 1);
            cur_frm.set_df_property("posting_date", "read_only", 1);
            cur_frm.set_df_property("branch", "read_only", 1);
            cur_frm.set_df_property("tds_percent", "read_only", 1);
            cur_frm.set_df_property("get_details", "disabled", 1);
        }
        frappe.model.get_value('Bank Payment Settings', { 'name': 'BOBL' }, 'enable_one_to_one',
            function (d) {
                if (d.enable_one_to_one == 0) {
                    cur_frm.set_df_property("bank_balance", "hidden", 1);
                }
            });
    },
    refresh: function (frm) {
        cur_frm.set_query("utility_services", function () {
            return {
                "filters": {
                    "branch": frm.doc.branch,
                    "company": frm.doc.company
                }
            }
        });

        if (!frm.doc.journal_entry && frm.doc.docstatus === 1 && (frm.doc.payment_status === "Payment Successful" || frm.doc.payment_status === "Partial Payment")) {
            frm.add_custom_button("Create Journal Entry", function () {
                frappe.call({
                    "method": "make_journal_entry",
                    "doc": cur_frm.doc,
                    callback: function (r, rt) {
                        if (r.message) {
                            frm.refresh_fields();
                            frappe.set_route("Form", "Journal Entry", r.message);
                        }
                    }
                });
            }).addClass("btn-primary");
        }
    },
    "tds_percent": function (frm) {
        calculate_tds(frm);
    },
    "branch": function (frm) {
        cur_frm.set_value("utility_services", "");
    },
    "utility_services": function (frm) {
        if (frm.doc.utility_services)
            get_utility_services(frm);
    },
    "get_details": function (frm) {
        if (frm.doc.utility_services)
            get_utility_outstandings(frm);
    }
});

function get_utility_outstandings(frm) {
    return frappe.call({
        method: "get_utility_outstandings",
        doc: cur_frm.doc,
        callback: function (r, rt) {
            frm.refresh_field("item");
            frm.refresh_fields();
        },
        freeze: true,
        freeze_message: "Fetching Utility Outstanding Amount..... Please Wait"
    });
}

function get_utility_services(frm) {
    if (!frm.doc.utility_services || !frm.doc.branch) {
        frappe.msgprint(
            "To fetch Utility Outstanding Amount, provide Branch and Utility Services ID"
        );
        return;
    }

    frappe.call({
        method: "erpnext.epayment.doctype.utility_bill.utility_bill.get_utility_services",
        args: {
            docname: frm.doc.name,
            doctype: frm.doc.doctype,
            utility_services: frm.doc.utility_services,
        },
        callback: function (r) {
            if (!r.message) return;
            var total = r.message.total || 0;
            show_progress(frm, 0, total, "Starting...");
        },
        freeze: false,
    });
}

// ---- progress bar helpers ----

function show_progress(frm, done, total, current) {
    var pct = total ? Math.round((done / total) * 100) : 0;
    var text = done + " / " + total + (current ? "  (" + current + ")" : "");

    // Create or reuse the wrapper
    if (!window._ub_progress_wrapper) {
        var wrapper = $(
            '<div id="ub-progress-wrapper" style="margin:8px 0;padding:8px 12px;border:1px solid #e5e7eb;border-radius:6px;background:#f9fafb;">' +
                '<div style="font-size:13px;font-weight:600;color:#374151;margin-bottom:6px;">' +
                    'Fetching Utility Outstanding <span id="ub-progress-count" style="float:right;color:#2563eb;"></span>' +
                '</div>' +
                '<div style="height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden;">' +
                    '<div id="ub-progress-bar" style="height:100%;width:0%;background:#2563eb;transition:width .2s ease;"></div>' +
                '</div>' +
            '</div>'
        );
        frm.$wrapper.find(".form-layout").first().prepend(wrapper);
        window._ub_progress_wrapper = wrapper;
    }

    $("#ub-progress-count").text(text + "   " + pct + "%");
    $("#ub-progress-bar").css("width", pct + "%");
}

function hide_progress() {
    if (window._ub_progress_wrapper) {
        window._ub_progress_wrapper.remove();
        window._ub_progress_wrapper = null;
    }
}

// ---- realtime listeners ----

frappe.realtime.on("utility_services_progress", function (data) {
    if (
        cur_frm &&
        cur_frm.doc.name === data.docname &&
        cur_frm.doc.doctype === data.doctype
    ) {
        show_progress(cur_frm, data.done, data.total, data.current);
    }
});

frappe.realtime.on("utility_services_result", function (data) {
    if (
        cur_frm &&
        cur_frm.doc.name === data.docname &&
        cur_frm.doc.doctype === data.doctype
    ) {
        hide_progress();
        frm_clear_and_set_items(cur_frm, data.rows || []);
        frappe.show_alert({
            message: __("Utility services outstanding fetched!"),
            indicator: "green",
        });
    }
});

frappe.realtime.on("utility_services_completed", function (data) {
    if (
        cur_frm &&
        cur_frm.doc.name === data.docname &&
        cur_frm.doc.doctype === data.doctype
    ) {
        hide_progress();
        cur_frm.reload_doc();
        frappe.show_alert({
            message: __("Utility services outstanding fetched successfully!"),
            indicator: "green",
        });
        if (data.errors && data.errors.length) {
            frappe.msgprint({
                title: __("Some services failed"),
                indicator: "orange",
                message: data.errors.join("<br>"),
            });
        }
    }
});

function frm_clear_and_set_items(frm, rows) {
    frm.clear_table("item");
    rows.forEach(function (r) {
        var child = frm.add_child("item");
        Object.keys(r).forEach(function (k) {
            if (k !== "doctype") child[k] = r[k];
        });
    });
    frm.refresh_field("item");
    frm.refresh_fields();
}

// function get_utility_services(frm) {
//     if (frm.doc.utility_services && frm.doc.branch) {
//         return frappe.call({
//             method: "get_utility_services",
//             doc: cur_frm.doc,
//             callback: function (r, rt) {
//                 frm.refresh_field("item");
//                 frm.refresh_fields();
//             },
//             freeze: true,
//             freeze_message: "Fetching Utility Outstanding Amount..... Please Wait"
//         });
//     } else {
//         frappe.msgprint("To fetch Utility Outstanding Amount, provide Branch and Utility Services ID");
//     }
// }

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