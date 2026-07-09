// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Advance Type", {
	setup: function(frm) {
        frm.set_query("advance_account", function() {
            return {
                filters: {
                    "company": frm.doc.company
            
                }
            };
        });
        // frm.set_query("advance_type", function() {
        //     return {
        //         filters: {
        //             "party_type":frm.doc.party_type
        //         }
        //     };
        // });

        
    },
    
});
