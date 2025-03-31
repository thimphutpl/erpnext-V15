// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Imprest Advance', {
	setup: function(frm) {
        // Set query for party (employee) field
        frm.set_query("party", erpnext.queries.employee);  // Changed to employee query
        
        // Set query for approver field
        frm.set_query("approver", function() {
            if (!frm.doc.party) {
                frappe.msgprint(__("Please select an employee first"));
                return;
            }
            
            return {
                query: "erpnext.accounts.doctype.imprest_recoup.imprest_recoup.get_approvers",
                filters: {
                    party: frm.doc.party  // Changed from 'employee' to 'party' to match Python
                }
            };
        });
    },
    
    party: function(frm) {
        // Clear approver when employee changes
        frm.set_value("approver", null);
        
        // Fetch new approver if employee is selected
        if (frm.doc.party) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Employee",
                    fieldname: "expense_approver",
                    filters: {name: frm.doc.party}
                },
                callback: function(r) {
                    if (r.message && r.message.expense_approver) {
                        frm.set_value("approver", r.message.expense_approver);
                    }
                }
            });
        }
    },


	refresh: function(frm) {
		frm.set_query("project", function() {
			return {
				"filters": {
					"branch": frm.doc.branch
				}
			}
		 });
	},

	// party: (frm) => {
	// 	frappe.call({
	// 		method: 'set_advance_amount',
	// 		doc: frm.doc,
	// 		callback: (r) =>{
	// 			frm.set_value("advance_amount", r.message)
	// 			frm.refresh_fields()
	// 		}
	// 	})
	// },

	amount: function(frm){
		if (frm.doc.advance_amount > 0 ){
			frm.set_value("balance_amount", frm.doc.amount)
			frm.set_value("adjusted_amount",0)
		}
	},

	// opening_amount: function(frm){
	// 	if (frm.doc.opening_amount > 0 ){
	// 		frm.set_value("balance_amount", frm.doc.opening_amount)
	// 		frm.set_value("adjusted_amount",0)
	// 	}
	// },
});
