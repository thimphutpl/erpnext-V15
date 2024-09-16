// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advance Recoup", {
    onload: function(frm){
		// frm.set_query('expense_account', 'items', function() {
		// 	return {
		// 		"filters": {
		// 			"account_type": "Expense Account"
		// 		}
		// 	};
		// });

		frm.set_query('account', 'items', function() {
			return {
				filters: {
					"is_group": 0,
				}
			};
		});
	},

	refresh(frm) {

	},

    "get_advance":function(frm){
		get_advance(frm)
	},

	"get_items":function(frm){
		return frappe.call({
			doc: frm.doc,
			method: 'get_transactions_detail',
			callback: function(r) {
				if (r.message){
					
					frm.refresh_field("items");
				}
			},
			freeze: true,
			
		});
	},
});

frappe.ui.form.on("Advance Recoup Item", {
	amount: function(frm, cdt, cdn){
		get_advance(frm)
	},
	
	recoup_type: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (!frm.doc.company) {
			d.recoup_type = "";
			frappe.msgprint(__("Please set the Company"));
			this.frm.refresh_fields();
			return;
		}

		if(!d.recoup_type) {
			return;
		}
		return frappe.call({
			method: "erpnext.accounts.doctype.imprest_recoup.imprest_recoup.get_imprest_recoup_account",
			args: {
				"recoup_type": d.recoup_type,
				"company": frm.doc.company
			},
			callback: function(r) {
				if (r.message) {
					d.account = r.message.account;
				}
				frm.refresh_field("items")
				frm.refresh_fields();
			}
		});
	}
})


var get_advance = function(frm){
	frm.set_value('total_amount', 0);
	frappe.call({
		method: 'populate_advances',
		doc: frm.doc,
		callback:  () =>{
			frm.refresh_field('advances')
			frm.refresh_fields()
		}
	})
}
