// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Other Deposit Claim", {
	setup:function(frm){
        frm.set_query("branch",function(){
            return {
                filters: {
                    company: frm.doc.company
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
    },

    get_all_other_deposit: function(frm) {
        frappe.call({
            method: "erpnext.accounts.doctype.other_deposit_claim.other_deposit_claim.get_all_other_deposit",
            args: {
                company: frm.doc.company,
                account_deposit: frm.doc.account_deposit,
                party: frm.doc.party,
                party_type: frm.doc.party_type,
                posting_date:frm.doc.posting_date
            },
            callback: function(r) {
                if (r.message) {
                    

     
                    frm.clear_table("other_deposite_details");

     
                    r.message.forEach(function(d) {

                        let child = frm.add_child("other_deposite_details");
                        child.party_type = d.party_type;
                        child.assignment = d.assignment;
                        child.amount = d.amount;
                        child.account = d.account;
                        child.party = d.party;
                        child.voucher_type=d.voucher_type;
                        child.voucher_no=d.voucher_no
                       

                    });

                    frm.refresh_field("other_deposite_details");
                }
            }
        });
    }
});
