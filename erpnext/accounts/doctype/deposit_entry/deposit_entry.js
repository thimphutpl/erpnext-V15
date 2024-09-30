// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Deposit Entry", {
	onload: function(frm) {
		frm.set_query("branch", function(doc){
			return {
				filters: {
					'company': doc.company,
				}
			}
		});

		frm.set_query("bank_account", function() {
			return {
				query: "erpnext.accounts.doctype.bank_payment.bank_payment.get_paid_from",
				filters: {
					branch: frm.doc.branch
				}
			};
		});

		frm.set_query("cash_account", function() {
			return {
				filters: {
					'account_type': 'Cash',
					'company': frm.doc.company
				}
			};
		});
	},

	refresh: function(frm) {
		if (frm.doc.docstatus != 1){
			frm.add_custom_button("Pull Trasaction",function(){
				frappe.call({
					method:'get_pos_closing',
					doc:frm.doc,
					callback:function(r){
						frm.refresh_fields('items')
						frm.set_value('total_amount',r.message)
						frm.refresh_fields('total_amount')
					},
					freeze: true,
					freeze_message: '<span style="color:white; background-color: red; padding: 10px 50px; border-radius: 5px;">Please Wait...</span>',
				})
			},__('Create'))
			cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
		}
	}
});
