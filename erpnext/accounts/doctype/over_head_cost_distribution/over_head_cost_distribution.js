// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Over Head Cost Distribution", {
    setup: function (frm){
        frm.set_query("account", function () {
			return {
				filters: {
					root_type: "Expense"
				},
			};
		});
    },
    get_over_head_cost: (frm) => {
        frappe.call({
            method: "get_over_head_cost",
            doc: frm.doc,
            callback: function(r) {
                if (r.message) {
                    frm.set_value("source_total_amount", r.message);
                } else {
                    frappe.msgprint(__("No Over Head Cost found for the selected period."));
                }
            }
        });
    },
    get_project: (frm) => {
        frappe.call({
            method: "get_project",
            doc: frm.doc,
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint(__("Project fetched successfully."));
                } else {
                    frappe.msgprint(__("No Project found for the selected criteria."));
                }
            }
        });
        frm.refresh_fields();
    },
});
