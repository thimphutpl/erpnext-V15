// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Compact Evaluation", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Compact Evaluation', {
    refresh: function (frm) {
        // Calculate and display totals when the form is loaded
        calculate_totals(frm);
    },
    table_qwvz: {
        // Trigger recalculation when the child table is modified
        weighted: calculate_totals,
        achieved: calculate_totals
    }
});

function calculate_totals(frm) {
    let total_weighted = 0;
    let total_achieved = 0;

    // Loop through the child table
    frm.doc.table_qwvz.forEach((row) => {
        total_weighted += flt(row.weighted || 0);
        total_achieved += flt(row.achieved || 0);
    });

    // Update the fields
    frm.set_value("total_weighted_percent", total_weighted);
    frm.set_value("total_achieved_percent", total_achieved);

    frm.refresh_field("total_weighted_percent");
    frm.refresh_field("total_achieved_percent");
}

