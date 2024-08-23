// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Resource Booking", {
	refresh: function(frm) {
        frm.fields_dict['resource'].get_query = function(doc) {
            return {
                filters: {
                    'status': 'Available'
                }
            };
        };
    },
    resource_type: function(frm) {
        if(frm.doc.resource_type) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Resource Directory",
                    filters: { "resource_type": frm.doc.resource_type },
                    fieldname: "resource_name"
                }
                
            });

            // Reapply the filter when the department is changed
            frm.set_query('resource', function() {
                return {
                    filters: {
                        'resource_type': frm.doc.resource_type
                    }
                };
            });
        }
    },
});
