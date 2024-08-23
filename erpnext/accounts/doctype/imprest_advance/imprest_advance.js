// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Imprest Advance', {
	onload: function(frm) {
		frm.set_query("branch", function(doc) {
			return {
				filters: {
					'company': doc.company,
				}
			}
		})
	},

	refresh: function(frm) {
		// 
	},

	party: (frm) => {
		frappe.call({
			method: 'set_advance_amount',
			doc: frm.doc,
			callback: (r) =>{
				frm.set_value("advance_amount", r.message)
				frm.refresh_fields()
			}
		})
	},

	advance_amount: function(frm){
		if (frm.doc.advance_amount > 0 ){
			frm.set_value("balance_amount", frm.doc.advance_amount)
			frm.set_value("adjusted_amount",0)
		}
	},
	opening_amount: function(frm){
		if (frm.doc.opening_amount > 0 ){
			frm.set_value("balance_amount", frm.doc.opening_amount)
			frm.set_value("adjusted_amount",0)
		}
	},
});
