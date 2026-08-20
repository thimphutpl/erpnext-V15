// // Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Advance", {
//     setup: function(frm) {
//         frm.set_query("branch", function() {
//             return {
//                 filters: {
//                     company: frm.doc.company
//                 }
//             };
//         });
//         frm.set_query("budget_activity",function(){
//             return{
//                  filters: {
//                     company: frm.doc.company
//                 }

//             }
//         })
//          frm.set_query("budget_sub_activity",function(){
//             return{
//                  filters: {
//                     company: frm.doc.company
//                 }

//             }
//         })
//         frm.set_query("retention",function(){
//             return{
//                  filters: {
//                     company: frm.doc.company
//                 }

//             }
//         })
//          frm.set_query("tds",function(){
//             return{
//                  filters: {
//                     company: frm.doc.company
//                 }

//             }
//         })
//     },

 
//     company:function(frm){
//         if (!frm.doc.company){
//             frm.set_value("branch","")
//         }

//     },
//     apply_retention(frm) {
//         toggle_retention(frm);
//     },

//     party_type: function (frm) {
//         toggle_party_field(frm);
//     },
//     tds(frm){
//         if (!frm.doc.tds) {
//             frm.set_value("tds_account", "");
//             frm.set_value("tds_rate", "");
//             return;
//         }
//         frappe.call({
//             method: "erpnext.accounts.doctype.advance.advance.tax_account",
//             args: {
//                 name: frm.doc.tds,
//                 company: frm.doc.company
//             },
//             callback: function(r) {
//                 if (r.message) {
                    
//                     frm.set_value("tds_account", r.message.account);
//                     frm.set_value("tds_rate", r.message.tax_withholding_rate);
//                 }
//             }
//         });

//     },
//     // retention(frm){
//     //     if (!frm.doc.retention) {
//     //         // frm.set_value("retention_account", "");
//     //         frm.set_value("retention_rate", "");
//     //         return;
//     //     }
//     //     frappe.call({
//     //         method: "erpnext.accounts.doctype.advance.advance.tax_account",
//     //         args: {
//     //             name: frm.doc.retention
//     //         },
//     //         callback: function(r) {
//     //             if (r.message) {
//     //                 // frm.set_value("retention_account", r.message[0].account_head);
//     //                 frm.set_value("retention_rate", r.message[0].rate);
//     //             }
//     //         }
//     //     });

//     // },
//     apply_tds(frm){
//         toggle_tds(frm)
//     },

//     onload: function (frm) {
//         toggle_party_field(frm);
//         toggle_retention(frm);
//         toggle_tds(frm)
//     },

//     refresh(frm) {

//          frm.add_custom_button('Start Tour', () => {
//             const tour_name = 'Advance';

//             frm.tour.init({ tour_name }).then(() => {
//                 frm.tour.start();
//             });
//         });
//         if (frm.doc.docstatus == 1) {
//             cur_frm.add_custom_button(__('Accounting Ledger'), function () {
//                 frappe.route_options = {
//                     voucher_no: frm.doc.name,
//                     from_date: frm.doc.posting_date,
//                     to_date: frm.doc.posting_date,
//                     company: frm.doc.company,
//                     group_by_voucher: false
//                 };
//                 frappe.set_route("query-report", "General Ledger");
//             }, __("View"));
//         }
//     },


    
// });

// function toggle_retention(frm) {
//     if (frm.doc.apply_retention) {
//         frm.set_df_property("retention", "hidden", 0);
//         frm.set_df_property("retention_amount", "hidden", 0);
//         frm.set_df_property("retention_amount", "hidden", 0);
//         frm.set_df_property("retention", "reqd", 1);
//     } else {
//         frm.set_df_property("retention", "hidden", 1);
//         frm.set_df_property("retention_amount", "hidden", 1);
//         frm.set_df_property("retention", "reqd", 0);
//         frm.set_df_property("retention_amount", "hidden", 1);
//         frm.set_value("retention", "");
//         frm.set_value("retention_amount", 0);
//     }

//     frm.refresh_field("retention");
//     frm.refresh_field("retention_amount");
// }

// function toggle_tds(frm) {
//     if (frm.doc.apply_tds) {
//         frm.set_df_property("tds", "hidden", 0);
//         frm.set_df_property("tds_amount", "hidden", 0);
//         frm.set_df_property("tds_rate", "hidden", 0);
//         frm.set_df_property("tds", "reqd", 1);
//     } else {
//         frm.set_df_property("tds", "hidden", 1);
//         frm.set_df_property("tds_amount", "hidden", 1);
//            frm.set_df_property("tds_rate", "hidden", 1);
//         frm.set_df_property("tds", "reqd", 0);
//         frm.set_value("tds", "");
//         frm.set_value("tds_amount", 0);
//     }

//     frm.refresh_field("tds");
//     frm.refresh_field("tds_amount");
// }
// function toggle_party_field(frm) {
//     if (!frm.doc.party_type) {
//         frm.set_df_property("customer", "hidden", 1);
//         frm.set_df_property("advance_type", "hidden", 1);
//         frm.set_df_property("advance_type", "reqd", 0);
//         frm.set_df_property("customer", "reqd", 0);
//         frm.set_value("customer", "");
//     } else {
//         frm.set_df_property("customer", "hidden", 0);
//         frm.set_df_property("advance_type", "hidden", 0);
//         frm.set_df_property("customer", "reqd", 1);
//         frm.set_df_property("advance_type", "reqd", 1);
//     }
//      frm.set_query("advance_type", function() {
//             return {
//                 filters: {
//                     "company": frm.doc.company,
//                     "party_type": frm.doc.party_type
//                 }
//             };
//         });
// }

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
        frm.set_query("budget_activity","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
         frm.set_query("budget_sub_activity","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
        frm.set_query("retention","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
         frm.set_query("tds","advance_details",function(){
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
    
    party_type: function (frm) {
        toggle_party_field(frm);
    },
    


    
});


frappe.ui.form.on("Advance Item", {

    apply_tds: function(frm, cdt, cdn) {
        toggle_tds(frm, cdt, cdn);
    },
    apply_retention: function(frm, cdt, cdn) {
        toggle_retention(frm, cdt, cdn);
    },

    opening_balance: function(frm, cdt, cdn) {
        calculate_tds(frm, cdt, cdn);
    },
    tds_rate: function(frm, cdt, cdn) {
        calculate_tds(frm, cdt, cdn);
    },

    retention_rate: function(frm, cdt, cdn) {
        calculate_retention(frm, cdt, cdn);
    },
    retention: function(frm, cdt, cdn) {
        calculate_retention(frm, cdt, cdn);
    },
    tds_amount: function(frm, cdt, cdn) {
        calculate_net_amount(frm, cdt, cdn);
    },
    retention_amount: function(frm, cdt, cdn) {
          calculate_net_amount(frm, cdt, cdn);
    },

    tds: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.tds) {
            frappe.model.set_value(cdt, cdn, "tds_account", "");
            frappe.model.set_value(cdt, cdn, "tds_rate", 0);
            frappe.model.set_value(cdt, cdn, "tds_amount", 0);
            return;
        }

        frappe.call({
            method: "erpnext.accounts.doctype.advance.advance.tax_account",
            args: {
                name: row.tds,
                company: frm.doc.company
            },
            callback: function(r) {
                if (r.message) {
                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "tds_account",
                        r.message.account
                    );

                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "tds_rate",
                        r.message.tax_withholding_rate
                    );
                }
            }
        });
        calculate_tds(frm, cdt, cdn);
    },

    form_render: function(frm, cdt, cdn) {
        toggle_tds(frm, cdt, cdn);
        toggle_retention(frm, cdt, cdn);
    }
});



function toggle_tds(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let grid_row = frm.fields_dict.advance_details.grid.grid_rows_by_docname[cdn];

    if (!grid_row) {
        return;
    }

    if (row.apply_tds) {
        grid_row.toggle_reqd("tds_account", true);
        grid_row.toggle_reqd("tds", true);
        grid_row.toggle_reqd("tds_rate", true);
        grid_row.toggle_reqd("tds_amount", true);
    
        grid_row.toggle_display("tds_account",true)
        grid_row.toggle_display("tds", true);
        grid_row.toggle_display("tds_rate", true);
        grid_row.toggle_display("tds_amount", true);

    } else {

        grid_row.toggle_reqd("tds_account", false);
        grid_row.toggle_reqd("tds", false);
        grid_row.toggle_reqd("tds_rate", false);
        grid_row.toggle_reqd("tds_amount", false);

        grid_row.toggle_display("tds_account",false)
        grid_row.toggle_display("tds", false);
        grid_row.toggle_display("tds_rate", false);
        grid_row.toggle_display("tds_amount", false);

        frappe.model.set_value(cdt, cdn, "tds", "");
        frappe.model.set_value(cdt, cdn, "tds_rate", 0);
        frappe.model.set_value(cdt, cdn, "tds_amount", 0);
          frappe.model.set_value(cdt, cdn, "tds_account","");
    }
}


function toggle_retention(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let grid_row = frm.fields_dict.advance_details.grid.grid_rows_by_docname[cdn];

    if (!grid_row) {
        return;
    }

    if (row.apply_retention) {

        grid_row.toggle_reqd("retention",true)
        grid_row.toggle_reqd("retention_account", true);
        grid_row.toggle_reqd("retention_rate", true);
        grid_row.toggle_reqd("retention_amount", true);
        grid_row.toggle_display("retention",true)
        grid_row.toggle_display("retention_account", true);
        grid_row.toggle_display("retention_rate", true);
        grid_row.toggle_display("retention_amount", true);

    } else {


        grid_row.toggle_reqd("retention",false)
        grid_row.toggle_reqd("retention_account", false);
        grid_row.toggle_reqd("retention_rate", false);
        grid_row.toggle_reqd("retention_amount", false);
        grid_row.toggle_display("retention", false);
        grid_row.toggle_display("retention_account", false);
        grid_row.toggle_display("retention_rate", false);
        grid_row.toggle_display("retention_amount", false);

        frappe.model.set_value(cdt, cdn, "retention", "");
        frappe.model.set_value(cdt, cdn, "retention_rate", 0);
        frappe.model.set_value(cdt, cdn, "retention_account", 0);
        frappe.model.set_value(cdt, cdn, "retention_account", "");
    }
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
                company: frm.doc.company,
                party_type: frm.doc.party_type
            }
        };
    });
}

function calculate_tds(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.apply_tds || !row.opening_balance || !row.tds_rate) {
        frappe.model.set_value(cdt, cdn, "tds_amount", 0);
        return;
    }

    let opening_balance = flt(row.opening_balance);
    let tds_rate = flt(row.tds_rate);

    let tds_amount = opening_balance * tds_rate / 100;

    frappe.model.set_value(
        cdt,
        cdn,
        "tds_amount",
        tds_amount
    );
}

function calculate_retention(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.apply_tds || !row.opening_balance || !row.retention_rate) {
        frappe.model.set_value(cdt, cdn, "retention_amount", 0);
        return;
    }

    let opening_balance = flt(row.opening_balance);
    let retention_rate = flt(row.retention_rate);

    let retention_amount = opening_balance * retention_rate / 100;

    frappe.model.set_value(
        cdt,
        cdn,
        "retention_amount",
        retention_amount
    );
}

function calculate_net_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let net_amount =
        flt(row.opening_balance) -
        flt(row.tds_amount) -
        flt(row.retention_amount);

    frappe.model.set_value(
        cdt,
        cdn,
        "total_amount",
        net_amount
    );
}