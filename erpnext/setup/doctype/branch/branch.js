// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Branch", {
	refresh: function (frm) {},
	setup:function(frm){
		const getBankAccountFilter = () => {
            if (!frm.doc.company) {
                alert("Company is required.")
            }
            
            return {
                filters: {
                    company: frm.doc.company,
                    is_group: 0,
                    disabled: 0
                }
            };
        };
	    frm.set_query("expense_bank_account", getBankAccountFilter);
        frm.set_query("revenue_bank_account", getBankAccountFilter);

	},

	// expense_bank_account:function(frm){
	// 	frappe.call({
	// 		method:"erpnext.setup.doctype.branch.branch.company_base_account",
	// 		args:{
	// 			company:frm.doc.company,
	// 			is_group:0
	// 		}
	// 	})
	// }
});