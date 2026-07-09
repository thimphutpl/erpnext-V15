// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advance", {
    setup: function(frm) {
        frm.set_query("branch", function() {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
        frm.set_query("budget_activity",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
         frm.set_query("budget_sub_activity",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
        frm.set_query("retention",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
         frm.set_query("tds",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
    },

 
    company:function(frm){
        if (!frm.doc.company){
            frm.set_value("branch","")
        }

    },
    apply_retention(frm) {
        toggle_retention(frm);
    },

    party_type: function (frm) {
        toggle_party_field(frm);
    },
    tds(frm){
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
            callback: function(r) {
                if (r.message) {
                    
                    frm.set_value("tds_account", r.message.account);
                    frm.set_value("tds_rate", r.message.tax_withholding_rate);
                }
            }
        });

    },
    // retention(frm){
    //     if (!frm.doc.retention) {
    //         // frm.set_value("retention_account", "");
    //         frm.set_value("retention_rate", "");
    //         return;
    //     }
    //     frappe.call({
    //         method: "erpnext.accounts.doctype.advance.advance.tax_account",
    //         args: {
    //             name: frm.doc.retention
    //         },
    //         callback: function(r) {
    //             if (r.message) {
    //                 // frm.set_value("retention_account", r.message[0].account_head);
    //                 frm.set_value("retention_rate", r.message[0].rate);
    //             }
    //         }
    //     });

    // },
    apply_tds(frm){
        toggle_tds(frm)
    },

    onload: function (frm) {
        toggle_party_field(frm);
        toggle_retention(frm);
        toggle_tds(frm)
    },

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


    
});

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
     frm.set_query("advance_type", function() {
            return {
                filters: {
                    "company": frm.doc.company,
                    "party_type": frm.doc.party_type
                }
            };
        });
}