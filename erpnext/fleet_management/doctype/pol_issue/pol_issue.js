// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('POL Issue', {
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},

	// tanker: function (frm) {
    //     if (frm.doc.tanker) {
    //         frappe.call({
    //             method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_data",
    //             args: {
    //                 tanker: frm.doc.tanker,
    //                 branch: frm.doc.branch,
    //                 all_equipment: frm.doc.all_equipment || 0,
    //                 to_date: frm.doc.to_date || frappe.datetime.now_date()
    //             },
    //             callback: function (response) {
    //                 if (response.message) {
    //                     // Process the data and update fields in the form
    //                     let data = response.message;
    //                     console.log(data); // Debugging the fetched data
    //                     frappe.msgprint(__("Data fetched successfully for the selected tanker."));
    //                     // Additional logic to handle or display data in the form
    //                 } else {
    //                     frappe.msgprint(__("No data found for the selected tanker."));
    //                 }
    //             }
    //         });
    //     }
    // },

	refresh: function(frm) {
		if(frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company
				};
				frappe.set_route("query-report", "Stock Ledger Report");
			}, __("View"));

			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}

		// cur_frm.set_query("pol_type", function () {
        //     return {
        //         filters: {
        //             disabled: 0,
        //             is_pol_item: 1
        //         }
        //     };
        // });

        // cur_frm.set_query("tanker", function () {
        //     if (!frm.doc.branch) {
        //         frappe.msgprint(__('Please select a branch first.'));
        //         return null;
        //     }
        //     return {
        //         query: "erpnext.fleet_management.doctype.pol_issue.pol_issue.equipment_query",
        //         filters: { branch: frm.doc.branch }
        //     };
        // });
	},
	// "tanker": function (frm) {
	// 	if (frm.doc.tanker) {
    //         frappe.call({
    //             method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_data", // Update with the correct path
    //             args: {
    //                 equipment_name: frm.doc.equipment,
    //                 to_date: frm.doc.to_date,
    //                 all_equipment: frm.doc.all_equipment || 1,
    //                 branch: frm.doc.branch
    //             },
    //             callback: function(response) {
    //                 if (response.message) {
    //                     let data = response.message;

    //                     // Process and display the fetched data
    //                     frappe.msgprint({
    //                         title: __('Fetched Equipment Data'),
    //                         message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
    //                         indicator: 'green'
    //                     });

    //                     // Optional: You can set a field value with specific data
    //                     if (data.length > 0) {
    //                         frm.set_value('tank_balance', data[0].balance);
    //                     }
    //                 } else {
    //                     frappe.msgprint(__('No data found for the selected equipment.'));
    //                 }
    //             }
    //         });
    //     } else {
    //         // Clear related fields if no equipment is selected
    //         frm.set_value('tank_balance', '');
    //     }
	// },
	tanker: function (frm) {
        if (frm.doc.tanker) {
            frappe.call({
                method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_data",
                args: {
                    tanker: frm.doc.tanker,
                    branch: frm.doc.branch,
                    all_equipment: frm.doc.all_equipment || 0,
                    to_date: frm.doc.to_date || frappe.datetime.now_date()
                },
                callback: function (response) {
                    if (response.message) {
                        // Process the data and update fields in the form
                        let data = response.message;
                        console.log(data); // Debugging the fetched data
                        frappe.msgprint(__("Data fetched successfully for the selected tanker."));
                        // Additional logic to handle or display data in the form
                    } else {
                        frappe.msgprint(__("No data found for the selected tanker."));
                    }
                }
            });
        }
    },

	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
		var row = cur_frm.open_grid_row();
		/*if(!row.grid_form.fields_dict.pol_type.value) {
			//row.grid_form.fields_dict.pol_type.set_value(frm.doc.pol_type)
                	row.grid_form.fields_dict.pol_type.refresh()
		}*/
	},

	"branch": function(frm) {
		return frappe.call({
			method: "erpnext.custom_utils.get_cc_warehouse",
			args: {
				"branch": frm.doc.branch
			},
			callback: function(r) {
				cur_frm.set_value("cost_center", r.message.cc)
				cur_frm.set_value("warehouse", r.message.wh)
				cur_frm.refresh_fields()
			}
		})
	}
});

cur_frm.add_fetch("equipment", "registration_number", "equipment")

frappe.ui.form.on("POL Issue", "refresh", function(frm) {
    	cur_frm.set_query("pol_type", function() {
		return {
		    "filters": {
			"disabled": 0,
			"is_pol_item": 1
		    }
		};
	    });
	
	cur_frm.set_query("tanker", function() {
		return {
			// "query": "erpnext.fleet_management.doctype.pol_issue.pol_issue.equipment_query",
			"query": "erpnext.fleet_management.doctype.pol_issue.pol_issue.equipment_query",
			
			filters: {'branch': frm.doc.branch}
		}
	})
	
	cur_frm.set_query("warehouse", function() {
                return {
                        query: "erpnext.controllers.queries.filter_branch_wh",
                        filters: {'branch': frm.doc.branch}
                }
            });

        frm.fields_dict['items'].grid.get_field('equipment_warehouse').get_query = function(doc, cdt, cdn) {
                item = locals[cdt][cdn]
                return {
                        "query": "erpnext.controllers.queries.filter_branch_wh",
                        filters: {'branch': item.equipment_branch}
                }
        }

        frm.fields_dict['items'].grid.get_field('hiring_warehouse').get_query = function(doc, cdt, cdn) {
                item = locals[cdt][cdn]
                return {
                        "query": "erpnext.controllers.queries.filter_branch_wh",
                        filters: {'branch': item.hiring_branch}
                }
        }

	frm.fields_dict['items'].grid.get_field('equipment').get_query = function(doc, cdt, cdn) {
		doc = locals[cdt][cdn]
                if(frm.doc.purpose == "Transfer") {
                        return {
				"query": "erpnext.fleet_management.doctype.pol_issue.pol_issue.equipment_query",
				filters: {'branch': '%'}
                        }
                }
                else {
                        return {
                                filters: {
                                        "is_disabled": 0,
					"equipment_type": ["not in", ['Skid Tank', 'Barrel']]
                                }
                        }
                }
	}
})

frappe.ui.form.on("POL Issue Items", "equipment", function(doc, cdt, cdn) {
	doc = locals[cdt][cdn]
	if(doc.equipment_branch) {
		return frappe.call({
			method: "erpnext.custom_utils.get_cc_warehouse",
			args: {
				"branch": doc.equipment_branch
			},
			callback: function(r) {
				frappe.model.set_value(cdt, cdn, "equipment_cost_center", r.message.cc)
				frappe.model.set_value(cdt, cdn, "equipment_warehouse", r.message.wh)
				cur_frm.refresh_fields()
			}
		})
	}
})

