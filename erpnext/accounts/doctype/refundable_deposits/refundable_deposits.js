// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Refundable Deposits", {
    refresh: function(frm) {
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
	setup:function(frm){
        frm.set_query("branch",function(){
            return {
                filters: {
                    company: frm.doc.company
                }
            }
        })
        frm.set_query("board_head",function(){
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 1
                }
            }
        })
        frm.set_query("account_deposit",function(){
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 0
                }
            }
        })
        frm.set_query("account",function(){
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 0,
                    parent_account:frm.doc.board_head
                }
            }
        })
        
    },
    // get_all_other_deposite:function(frm){
    //     frappe.call({
    //     method: "erpnext.accounts.doctype.mof_payment.mof_payment.get_all_other_deposit",
    //     args: {
    //         company: frm.doc.company,
    //         account_deposit: frm.doc.account_deposit

    //     },
    //     callback: function(r) {
    //       if (r.message) {
    //             frm.set_value("amount", r.message);
    //         }
    //     }
    // });

    // },

     get_all_other_deposite: function(frm) {
        frappe.call({
            method: "erpnext.accounts.doctype.refundable_deposits.refundable_deposits.get_all_other_deposit",
            args: {
                company: frm.doc.company,
                account_deposit: frm.doc.account_deposit,
                posting_date: frm.doc.posting_date
       
            },
            callback: function(r) {
                if (r.message) {
                    

     
                    frm.clear_table("other_deposits");

     
                    r.message.forEach(function(d) {

                        let child = frm.add_child("other_deposits");
                        child.party_type = d.party_type;
                        child.voucher_no = d.voucher_no;
                        child.voucher_type = d.voucher_type;
                        child.assignment = d.assignment;
                        child.amount = d.outstanding;
                        child.account = d.account;
                        child.party = d.party;
                       

                    });

                    frm.refresh_field("other_deposits");
                }
            }
        });
    }
  
});


