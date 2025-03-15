// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("pol_type", "item_name", "item_name")

frappe.ui.form.on('Equipment POL Transfer', {
	onload: function(frm) {
		// if(!frm.doc.posting_date) {
		// 	frm.set_value("posting_date", get_today())
		// }
        if(!frm.doc.posting_date) {
			// frm.set_value("posting_date", get_today())
            frm.set_value('posting_date', frappe.datetime.now_date());
            frm.set_value('posting_time', frappe.datetime.now_time());
		}
	},

	refresh: function(frm) {
		// if(frm.doc.docstatus == 1) {
        //     cur_frm.add_custom_button(__("Stock Ledger"), function() {
		// 		frappe.route_options = {
		// 			voucher_no: frm.doc.name,
		// 			from_date: frm.doc.posting_date,
		// 			to_date: frm.doc.posting_date,
		// 			company: frm.doc.company
		// 		};
		// 		frappe.set_route("query-report", "Stock Ledger Report");
		// 	}, __("View"));

		// 	cur_frm.add_custom_button(__('Accounting Ledger'), function() {
		// 		frappe.route_options = {
		// 			voucher_no: frm.doc.name,
		// 			from_date: frm.doc.posting_date,
		// 			to_date: frm.doc.posting_date,
		// 			company: frm.doc.company,
		// 			group_by_voucher: false
		// 		};
		// 		frappe.set_route("query-report", "General Ledger");
		// 	}, __("View"));
		// }
	},
  
	from_equipment: function (frm) {
		if (frm.doc.from_equipment && frm.doc.own_tank_transfer) {
            // Fetch Equipment Data
            // frappe.throw("hello")
            frappe.call({
                method: "erpnext.fleet_management.doctype.equipment_pol_transfer.equipment_pol_transfer.get_tank_datas",
                args: {
                    equipment: frm.doc.from_equipment,
                    all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch,
                },
                callback: function (response) {
                    if (response.message) {
                        let data = response.message;

                        // Optional: Display fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });
                        if (data.length > 0) {
                            frm.set_value('equipment_balance', data[0].balance);
                        }

                        // Set the balance in the current row
                        frappe.model.set_value(cdt, cdn, "equipment_balance", data[0]?.balance || 0);
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                        frappe.model.set_value(cdt, cdn, "equipment_balance", 0);
                    }
                }
            });
        }
        if (frm.doc.from_equipment && frm.doc.own_tank_transfer != 1) {
            // Fetch Equipment Data
            frappe.call({
                method: "erpnext.fleet_management.doctype.equipment_pol_transfer.equipment_pol_transfer.get_tank_data",
                args: {
                    equipment: frm.doc.from_equipment,
                    all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch
                },
                callback: function (response) {
                    if (response.message) {
                        let data = response.message;

                        // Optional: Display fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });
                        if (data.length > 0) {
                            frm.set_value('tank_balance', data[0].balance);
                        }
                        // Set the balance in the current row
                        frappe.model.set_value(cdt, cdn, "tank_balance", data[0]?.balance || 0);
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                        frappe.model.set_value(cdt, cdn, "tank_balance", 0);
                    }
                }
            });
        } else {
            // Clear the field if no equipment is selected
            frappe.model.set_value(cdt, cdn, "tank_balance", 0);
        }

        // Refresh fields to update UI
        cur_frm.refresh_fields();
    },

    to_equipment: function (frm) {
        if (frm.doc.to_equipment && frm.doc.own_tank_transfer) {
            // Fetch Equipment Data
            // frappe.throw("hello")
            frappe.call({
                method: "erpnext.fleet_management.doctype.equipment_pol_transfer.equipment_pol_transfer.to_get_equipment_data",
                args: {
                    equipment: frm.doc.to_equipment,
                    all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch
                },
                callback: function (response) {
                    if (response.message) {
                        let data = response.message;

                        // Optional: Display fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });
                        if (data.length > 0) {
                            frm.set_value('to_equipment_balance', data[0].balance);
                        }

                        // Set the balance in the current row
                        frappe.model.set_value(cdt, cdn, "to_equipment_balance", data[0]?.balance || 0);
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                        frappe.model.set_value(cdt, cdn, "to_equipment_balance", 0);
                    }
                }
            });
        }
        if (frm.doc.to_equipment && frm.doc.own_tank_transfer != 1) {
            // Fetch Equipment Data
            frappe.call({
                method: "erpnext.fleet_management.doctype.equipment_pol_transfer.equipment_pol_transfer.to_get_tank_data",
                args: {
                    equipment: frm.doc.to_equipment,
                    all_equipment: frm.doc.all_equipment || 1,
                    branch: frm.doc.branch
                },
                callback: function (response) {
                    if (response.message) {
                        let data = response.message;

                        // Optional: Display fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });
                        if (data.length > 0) {
                            frm.set_value('to_tank_balance', data[0].balance);
                        }
                        // Set the balance in the current row
                        frappe.model.set_value(cdt, cdn, "to_tank_balance", data[0]?.balance || 0);
                    } else {
                        frappe.msgprint(__('No data found for the selected equipment.'));
                        frappe.model.set_value(cdt, cdn, "to_tank_balance", 0);
                    }
                }
            });
        } else {
            // Clear the field if no equipment is selected
            frappe.model.set_value(cdt, cdn, "tank_balance", 0);
        }

        // Refresh fields to update UI
        cur_frm.refresh_fields();
    },
});

frappe.ui.form.on("Equipment POL Transfer", "refresh", function(frm) {
    	cur_frm.set_query("pol_type", function() {
		return {
		    "filters": {
			"disabled": 0,
			"is_hsd_item": 1
		    }
		};
	    });

    	cur_frm.set_query("from_equipment", function() {
		return {
		    "filters": {
			"is_disabled": 0,
			"branch": frm.doc.branch
		    }
		};
	    });
})


