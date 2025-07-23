// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Request', {
	refresh: function (frm) {
        if (frm.doc.docstatus == 1 ){
            open_extension(frm)
        }
    },

    from_date: function(frm){
        get_date(frm);
    },
    to_date: function(frm){
        check_date(frm);
    },

    vehicle: function(frm) {
        get_previous_km(frm)
        if (frm.doc.vehicle) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Equipment",
                    name: frm.doc.vehicle
                },
                callback: function(r) {
                    if (r.message) {
                        let equipment = r.message;
                        
                        // Ensure the Operators child table exists
                        if (equipment.operators && equipment.operators.length > 0) {
                            let operator_details = equipment.operators[0];  // Fetch the first operator

                            frm.set_value("driver", operator_details.operator);
                            frm.set_value("driver_name", operator_details.operator_name);
                            frm.set_value("contact_number", operator_details.contact_number);
                        } else {
                            frappe.msgprint(__("No operators found for this vehicle."));
                            frm.set_value("driver", "");
                            frm.set_value("driver_name", "");
                            frm.set_value("contact_number", "");
                        }
                    }
                }
            });
        }
    },
    
	onload:function(frm){
		frm.set_query('vehicle', () => {
			return {
				filters: {
					// equipment_type: frm.doc.vehicle_type,
                    // hired_equipment: 0,
                    branch: frm.doc.branch // Add branch filter
				}
			}
		})
	}
});

function open_extension(frm){
    frm.add_custom_button('Extend', () => {
        frappe.model.open_mapped_doc({
            method: "erpnext.fleet_management.doctype.vehicle_request.vehicle_request.create_vr_extension",	
            frm: cur_frm
        });
    })
}

function get_date(frm){
    var get_date = cur_frm.doc.from_date;
    frappe.model.set_value("time_of_departure", get_date);

}

function check_date(frm){
    frappe.call({
        method:"erpnext.fleet_management.doctype.vehicle_request.vehicle_request.check_form_date_and_to_date",
        args: {
            'from_date': frm.doc.from_date,
            'to_date': frm.doc.to_date
        },
    });
}

function get_previous_km(frm){
    frappe.call({
        method: "erpnext.fleet_management.doctype.vehicle_request.vehicle_request.get_previous_km",
        args: {
        'vehicle': frm.doc.vehicle,
        'vehicle_number': frm.doc.vehicle_number,
    },
    callback: function(r){
            console.log(r.message)
            cur_frm.set_value("previous_km", r.message[0].km)
        }
    });
}