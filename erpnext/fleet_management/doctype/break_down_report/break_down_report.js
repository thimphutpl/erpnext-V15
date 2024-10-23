// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Break Down Report", {
    refresh: function(frm) {
        if (frm.doc.docstatus == 1 && !frm.doc.job_cards) {
            frm.add_custom_button("Create Job Card", function() {
                frappe.model.open_mapped_doc({
                    method: "erpnext.fleet_management.doctype.break_down_report.break_down_report.make_job_cards",
                    frm: frm 
                });
            });
        }
    },

    onload: function(frm) {
        if (!frm.doc.date) {
            frm.set_value("date", frappe.datetime.get_today()); 
        }

        if(frm.doc.__islocal) {
			frappe.call({
				method: "erpnext.custom_utils.get_user_info",
				args: {"user": frappe.session.user},
				callback(r) {
					frm.set_value("cost_center", r.message.cost_center);
					frm.set_value("branch", r.message.branch);
					frm.set_value("customer", r.message.customer);
				}
			});
		}
    },
    owned_by: function(frm) {
        frm.set_value("customer", "");
        frm.set_value("equipment", "");
        frm.toggle_reqd("customer_cost_center", frm.doc.owned_by == 'CDCL')
        frm.toggle_reqd("customer_branch", frm.doc.owned_by == 'CDCL')
    }, 


    cost_center: function(frm) {
        if (frm.doc.cost_center) {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Branch",
                    filters: { cost_center: frm.doc.cost_center },
                    fields: ["name as branch"]
                },
                callback: function(r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value("branch", r.message[0].branch);
                    } else {
                        frm.set_value("branch", null);
                    }
                }
            });
        } else {
            frm.set_value("branch", null);
        }
    },
});

frappe.ui.form.on("Break Down Report", "refresh", function(frm) {
    frm.set_query("equipment", function(){
        if(frm.doc.owned_by == "Own"){
            return {
                "doctype": "Equipment",
                "filters": {
                    "branch": frm.doc.branch
                }
            };
        }
        else if (frm.doc.owned_by == "CDCL"){
            return {
                "filters": {
                    "branch": frm.doc.customer_branch,
                    // "customer": frm.doc.customer_cost_center
                }
            };
        }
    });
    
    frm.set_query("cost_center", function(){
        return {
            "filters": {
                "is_group": 0,
            }
        };
    });
    
    frm.set_query("customer", function(){
        filters = {};
        if (frm.doc.owned_by == "Own"){
            filters = {
                "disabled": 0,
                "cost_center": frm.doc.cost_center,
                "branch": frm.doc.branch
            };
        }
        // if(frm.doc.owned_by == "CDCL") {
        //     filters = {
        //         "disabled": 0,
        //         "customer_group": "Internal",
        //         "branch": ["!=", frm.doc.branch]
        //     };
        // }
        // return {
        //     "filters": filters
        // };
    });
});

