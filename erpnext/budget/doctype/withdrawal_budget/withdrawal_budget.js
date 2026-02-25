// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Withdrawal Budget", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Withdrawal Budget', {
	onload: function(frm){
		apply_account_filter(frm)
		frm.set_query("cost_center", function() {
			return {
				filters: {
					company: frm.doc.company,
					disabled: 0,
					is_group: 0
				}
			}
		});
		cur_frm.set_query("project", function() {
			return {
				"filters": [
					["Project", "status", "=", "Opened"]
				]
			}
		});
	},
	refresh: function(frm) {
		apply_account_filter(frm)
	},
});

var apply_account_filter = function(frm){
	console.log()
	frm.set_query("account", "items", function() {
		return {
			filters: {
				company: frm.doc.company,
				is_group: 0,
				// account_type:["in",["Expense Account","Fixed Asset"]],
				budget_type:frm.doc.budget_type
			}
		};
	});
}