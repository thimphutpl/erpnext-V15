// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Soelra", {
	refresh(frm) {
        filter(frm)
	},

    company: function(frm) { 
        filter(frm)

    }
});


function filter(frm){
    frm.set_query('branch', function() {
        return {
            filters: {
                'company': frm.doc.company  // Filter based on selected company
            }
        };
    });

    frm.set_query("warehouse", "items", function(doc, cdt, cdn) {
        var child = locals[cdt][cdn];
        return {
            filters: {
                'company': frm.doc.company  // Filter based on selected company
            }
        };
    });
}