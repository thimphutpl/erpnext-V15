// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advance Settlement", {
    refresh(frm) {
        if (frm.doc.docstatus == 1) {
            cur_frm.add_custom_button(__('Accounting Ledger'), function () {
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
    "get_advance": function (frm) {
        get_advance(frm)
    },

    get_advance: function (frm) {
        // alert(frm.doc.is_running_bill)
        frappe.call({
            method: "erpnext.accounts.doctype.advance_entry.advance_entry.get_advance",
            args: {
                customer: frm.doc.customer,
                branch: frm.doc.branch

            },
            callback: function (response) {
                frm.clear_table('advance_list');
                if (response.message) {
                    if (typeof response.message === "string") {
                        // Show server message
                        frappe.msgprint(response.message);


                    } else {
                        response.message.forEach(function (advance) {
                            let row = frm.add_child('advance_list');
                            row.reference = advance.reference;
                            row.account = advance.account;
                            row.advance_type = advance.advance_type;
                            row.advance_amount = advance.advance_amount;
                            row.total_amount = advance.total_amount;
                            row.balance_amount = advance.balance_amount;
                            row.posting_date = advance.posting_date;
                            // Add any other fields you have in child table
                        });

                    }
                    // Add each advance to child table


                    // Refresh child table
                    frm.refresh_field('advance_list');
                }

            }
        });

    },
    setup: function (frm) {
        frm.set_query("branch", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        })
        frm.set_query("budget_activity", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        })
        frm.set_query("broad_head", "expense_details", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 1
                }
            };
        });
        frm.set_query("account", "expense_details", function () {
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 0
                }
            };
        });
        frm.set_query("retention", function () {
            return {
                filters: {
                    company: frm.doc.company
                }

            }
        })
        frm.set_query("tds", function () {
            return {
                filters: {
                    company: frm.doc.company
                }

            }
        })

    },
    company: function (frm) {
        if (!frm.doc.company) {
            frm.set_value("branch", "")
        }
    },
    party_type: function (frm) {
        toggle_party_field(frm);
    },

    onload: function (frm) {
        toggle_party_field(frm);
        toggle_tds(frm);
        toggle_retention(frm)
    },
    apply_tds: function (frm) {
        toggle_tds(frm)
    },
    apply_retention: function (frm) {
        toggle_retention(frm)
    },

    tds: function (frm) {
        if (!frm.doc.tds) {
            frm.set_value("tds_account", "");
            frm.set_value("tds_rate", "");
            return;
        }
        frappe.call({
            method: "erpnext.accounts.doctype.advance.advance.tax_account",
            args: {
                name: frm.doc.tds,
                company: frm.doc.company
            },
            callback: function (r) {
                if (r.message) {

                    frm.set_value("tds_account", r.message.account);
                    frm.set_value("tds_rate", r.message.tax_withholding_rate);
                }
            }
        });

    },


});

function toggle_party_field(frm) {
    if (!frm.doc.party_type) {
        frm.set_df_property("customer", "hidden", 1);
        frm.set_df_property("advance_type", "hidden", 1);
        frm.set_df_property("advance_type", "reqd", 0);
        frm.set_df_property("customer", "reqd", 0);
        frm.set_value("customer", "");
    } else {
        frm.set_df_property("customer", "hidden", 0);
        frm.set_df_property("advance_type", "hidden", 0);
        frm.set_df_property("customer", "reqd", 1);
        frm.set_df_property("advance_type", "reqd", 1);
    }
}


function toggle_retention(frm) {
    if (frm.doc.apply_retention) {
        frm.set_df_property("retention", "hidden", 0);
        frm.set_df_property("retention_amount", "hidden", 0);
        frm.set_df_property("retention_amount", "hidden", 0);
        frm.set_df_property("retention", "reqd", 1);
    } else {
        frm.set_df_property("retention", "hidden", 1);
        frm.set_df_property("retention_amount", "hidden", 1);
        frm.set_df_property("retention", "reqd", 0);
        frm.set_df_property("retention_amount", "hidden", 1);
        frm.set_value("retention", "");
        frm.set_value("retention_amount", 0);
    }

    frm.refresh_field("retention");
    frm.refresh_field("retention_amount");
}

function toggle_tds(frm) {
    if (frm.doc.apply_tds) {
        frm.set_df_property("tds", "hidden", 0);
        frm.set_df_property("tds_amount", "hidden", 0);
        frm.set_df_property("tds_rate", "hidden", 0);
        frm.set_df_property("tds", "reqd", 1);
    } else {
        frm.set_df_property("tds", "hidden", 1);
        frm.set_df_property("tds_amount", "hidden", 1);
        frm.set_df_property("tds_rate", "hidden", 1);
        frm.set_df_property("tds", "reqd", 0);
        frm.set_value("tds", "");
        frm.set_value("tds_amount", 0);
    }

    frm.refresh_field("tds");
    frm.refresh_field("tds_amount");
}