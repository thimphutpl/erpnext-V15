// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch", {
	onload: function (frm) {
		frm.set_query("expense_bank_account", function(doc){
			return {
				filters: {
					'company': doc.company,
				}
			}
		});
	},
	refresh: function (frm) {
		frm.set_query("cost_center", function(doc) {
			return {
				filters: {
					'is_group': 0,
					'disabled': 0,
					'company': doc.company,
				}
			}
		});
	},
});
