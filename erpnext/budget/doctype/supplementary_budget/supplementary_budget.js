// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplementary Budget', {
	onload: function(frm){
		frm.set_query("cost_center", function() {
			return {
				filters: {
					company: frm.doc.company,
					disabled: 0,
					use_budget_from_parent:1

				}
			}
		});
		frm.set_query("account", "items", function() {
		return {
			filters: {
				company: frm.doc.company,
				is_group: 0,
				account_type:["in",["Expense Account","Fixed Asset"]],
				budget_type:frm.doc.budget_type
			}
		};
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
		
		frm.set_query("account", "items", function() {
		return {
			filters: {
				company: frm.doc.company,
				is_group: 0,
				account_type:["in",["Expense Account","Fixed Asset"]],
				budget_type:frm.doc.budget_type
			}
		};
	});
	},
});
