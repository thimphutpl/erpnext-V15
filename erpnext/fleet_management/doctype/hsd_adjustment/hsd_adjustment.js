// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('HSD Adjustment', {
	setup: function(frm) {
                frm.get_docfield("items").allow_bulk_edit = 1;
        },	
	get_equipments: function(frm) {
		return frappe.call({
			method: "get_equipments",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			},
                        freeze: true,
                        freeze_message: "Loading Equipment Data.... Please Wait!"
		});
	},	
});

cur_frm.fields_dict['items'].grid.get_field('equipment').get_query = function(frm, cdt, cdn) {
	return {
		"filters": {
			"branch": frm.branch
		    } 
	}
}

frappe.ui.form.on("HSD Adjustment Item", {
	equipment: function (frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn); // Get the specific row in the child table
		if (row.equipment) {
			// Fetch Equipment Data
			frappe.call({
				method: "erpnext.fleet_management.doctype.hsd_adjustment.hsd_adjustment.get_tank_data",
				args: {
					equipment: row.equipment,
					branch: frm.doc.branch,
					tanker_adjustment: frm.doc.tanker_adjustment ? 1 : 0
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
						// if (data.length > 0) {
						// 	frm.set_value('system_balance', data[0].balance);
						// }
						// Set the balance in the current row
						frappe.model.set_value(cdt, cdn, "system_balance", data[0]?.balance || 0);
					} else {
						frappe.msgprint(__('No data found for the selected equipment.'));
						frappe.model.set_value(cdt, cdn, "system_balance", 0);
					}
				}
			});
		} else {
			// Clear the field if no equipment is selected
			frappe.model.set_value(cdt, cdn, "system_balance", 0);
		}

		// Refresh fields to update UI
		cur_frm.refresh_fields();
	},
});