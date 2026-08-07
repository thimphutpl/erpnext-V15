// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Group", {
    setup: function (frm) {
        frm.set_query("grade", "employee_grade", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        })

    }
});
