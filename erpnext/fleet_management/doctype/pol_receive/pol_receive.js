// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("equipment", "registration_number", "registration_number")
cur_frm.add_fetch("branch", "branch", "cost_center")
cur_frm.add_fetch("cost_center", "warehouse", "warehouse")
cur_frm.add_fetch("fuelbook", "branch", "fuelbook_branch")
cur_frm.add_fetch("equipment", "fuelbook", "own_fb")
cur_frm.add_fetch("pol_type", "item_name", "item_name")
cur_frm.add_fetch("pol_type", "stock_uom", "stock_uom")

frappe.ui.form.on('POL Receive', {
	onload: function (frm) {
		// if(!frm.doc.posting_date) {
		// 	frm.set_value("posting_date", get_today());
		// }
	},
	setup: function (frm) {
		frm.ignore_doctypes_on_cancel_all = ["Serial and Batch Bundle"];
		frm.set_query("fuelbook", function (doc) {
			var filterArgs
			if (!doc.book_type) return

			if (doc.book_type == "Own")
				filterArgs = [["equipment", "=", doc.equipment]]
			else if (doc.book_type == "Common") {
				filterArgs = [["branch", "=", doc.branch], ["type", "=", doc.book_type]]
			}

			return {
				filters: filterArgs
			}
		})
	},
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && frm.doc.book_type != "Barrel") {
			cur_frm.add_custom_button(__('Accounting Ledger'), function () {
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


	},
	book_type: function (frm) {
		// if(frm.doc.book_type == 'Own') {
		// 	frm.set_value("direct_consumption", 1)
		// }
		// if(frm.doc.book_type == 'Common') {
		// 	frm.set_value("direct_consumption", 0)
		// }
		// frm.refresh_fields("direct_consumption")
		update_balances(frm);
		if (frm.doc.book_type === 'Common') {
			frm.set_df_property('direct_consumption', 'hidden', 1);
			frm.set_df_property('direct_consumption', 'read_only', 1);
			frm.set_value('direct_consumption', 0);
		} else if (frm.doc.book_type === 'Own' || frm.doc.book_type === 'General Pol') {
			frm.set_df_property('direct_consumption', 'hidden', 0);
			frm.set_df_property('direct_consumption', 'read_only', 0);
			frm.set_value('direct_consumption', 1);
		} else {
			frm.set_df_property('direct_consumption', 'hidden', 0);
			frm.set_df_property('direct_consumption', 'read_only', 0);
		}
		// Check if book_type is 'Common'
		if (frm.doc.book_type === 'Common') {
			// frm.set_query('equipment', function() {
			//     return {
			//         filters: {
			//             equipment_type: ['in', ['Fuel Tanker', 'Barrel', 'Skid Tank', 'Skid Tank (HSD)', 'Trailer', 'Pick Up Truck', 'Excavator']],
			// 			branch: frm.doc.branch
			//         }
			//     };
			// });
			frm.set_query('equipment', function () {
				return {
					query: "erpnext.fleet_management.doctype.pol_receive.pol_receive.get_filtered_equipment",
					filters: {
						branch: frm.doc.branch
					}
				};
			});
		} else {
			// Clear filter for equipment if book_type is not 'Common'
			frm.set_query('equipment', function () {
				return {
					filters: {
						equipment_type: ['not in', ['Fuel Tanker', 'Barrel', 'Skid Tank']],
						branch: frm.doc.branch
					}
				};
			});
		}
	},
	// qty: function (frm) {
	// 	calculate_total(frm)
	// 	frm.events.reset_items()
	// 	frm.refresh_fields("items")
	// },
	direct_consumption: function (frm) {
		set_equipment_filter(frm)
	},
	// rate: function (frm) {
	// 	frm.events.reset_items()
	// 	frm.refresh_fields("items")
	// 	calculate_total(frm)
	// },
	get_pol_advance: function (frm) {
		populate_child_table(frm)

	},


	current_km: function (frm) {
		let previous_km = flt(frm.doc.previous_km) || 0;
		let current_km = flt(frm.doc.current_km) || 0;
		let qty = flt(frm.doc.total_qty);

		if (current_km < previous_km) {
			frappe.msgprint(__('Current KM cannot be less than Previous KM'), __('Validation Error'));
			frm.set_value('current_km', previous_km);
			current_km = previous_km;
		}

		let km_difference = current_km - previous_km;
		frm.set_value('km_difference', km_difference);

		let mileage = 0;
		if (qty > 0) {
			mileage = km_difference / qty;
		}

		frm.set_value('mileage', mileage);
	},
	branch: function (frm) {
		frm.set_query("equipment", function () {
			return {
				filters: {
					"branch": frm.doc.branch,
					// "enabled":1
					"is_disabled": 0,
				}
			}
		})
	},
	equipment: function (frm) {
		frm.set_query("fuelbook", function () {
			return {
				filters: {
					"equipment": frm.doc.equipment
				}
			}
		})
		if (frm.doc.book_type === 'Common') {
			update_balances(frm);
		} else if (frm.doc.book_type === 'Own') {
			if (frm.doc.equipment) {
				// frappe.throw("Tanker");
				frappe.call({
					method: "erpnext.fleet_management.doctype.pol_receive.pol_receive.get_equipment_data",
					args: {
						equipment: frm.doc.equipment,
						to_date: frm.doc.to_date,
						all_equipment: frm.doc.all_equipment || 0,
						branch: frm.doc.branch
					},
					callback: function (response) {
						if (response.message) {
							let data = response.message;

							// Process and display the fetched data
							// frappe.msgprint({
							// 	title: __('Fetched Equipment Data'),
							// 	message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
							// 	indicator: 'green'
							// });

							// Set tank_balance field with the fetched data
							if (data.length > 0) {
								frm.set_value('tank_balance', data[0].balance || 0);
							}
						} else {
							frappe.msgprint(__('No data found for the selected equipment.'));
						}
					}
				});
			} else {
				// Clear related fields if no equipment is selected
				frm.set_value('tank_balance', '');
			}
		}
	},
	use_common_fuelbook: function (frm) {
		frm.set_query("fuelbook", function () {
			return {
				filters: {
					"type": "Common",
					"branch": frm.doc.branch
				}
			}
		})
		if (frm.doc.use_common_fuelbook) {
			frm.set_query("equipment", function () {
				return {
					filters: {
						"branch": frm.doc.branch,
						// "enabled":1,
						"hired_equipment": 1
					}
				}
			})
		}
		else {
			frm.set_query("equipment", function () {
				return {
					filters: {
						"branch": frm.doc.branch,
						// "enabled":1
					}
				}
			})
		}
	},
	// reset_items: function (frm) {
	// 	cur_frm.clear_table("items");
	// },
});

// frappe.ui.form.on('POL Receive Item', {
// 	qty: function (frm, cdt, cdn) {
// 		calculate_amount(frm, cdt, cdn);
// 		calculate_total_amount(frm);
// 	},

// 	rate: function (frm, cdt, cdn) {
// 		calculate_amount(frm, cdt, cdn);
// 		calculate_total_amount(frm);
// 	},
// 	items_add: function (frm, cdt, cdn) {
// 		let child = locals[cdt][cdn];
// 		let stock_uom = frm.doc.stock_uom;
// 		frappe.model.set_value(child.doctype, child.name, 'uom', stock_uom);
// 		frm.refresh_field('items');
// 	}
// });

// var calculate_amount = function (frm, cdt, cdn) {
// 	let child = locals[cdt][cdn];
// 	let amount = child.qty * child.rate
// 	frappe.model.set_value(cdt, cdn, 'amount', parseFloat(amount));
// 	frm.refresh_field("amount", cdt, cdn)
// }

// var calculate_total_amount = function (frm) {
// 	var me = frm.doc.items || [];
// 	var total_amount = 0.00;
// 	var total_qty = 0.00;

// 	if (frm.doc.docstatus != 1) {
// 		for (var i = 0; i < me.length; i++) {
// 			if (me[i].amount) {
// 				total_amount += parseFloat(me[i].amount);
// 				total_qty += parseFloat(me[i].qty);
// 			}
// 		}

// 		cur_frm.set_value("total_amount", (total_amount));
// 		cur_frm.set_value("total_qty", (total_qty));
// 	}
// }
frappe.ui.form.on("POL Receive Item", {
	items_add: function (frm, cdt, cdn) {
		let child = locals[cdt][cdn];
		let stock_uom = frm.doc.stock_uom;
		frappe.model.set_value(child.doctype, child.name, 'uom', stock_uom);
		frm.refresh_field('items');
	},
	qty: function (frm, cdt, cdn) {
		calculate_all(frm);
	},
	rate: function (frm, cdt, cdn) {
		calculate_all(frm);
	},
	items_remove: function (frm) {
		calculate_all(frm);
	}
});

function calculate_all(frm) {
	let total_qty = 0;
	let total_amount = 0;

	frm.doc.items.forEach(function (row) {
		if (row.qty) {
			row.amount = row.qty * row.rate;
			total_qty += row.qty;
			total_amount += row.amount;
		}
	});

	frm.refresh_field("items");

	frm.set_value("total_qty", total_qty);
	frm.set_value("total_amount", total_amount);
	frm.set_value("tank_balance", total_qty);
}
cur_frm.set_query("pol_type", function () {
	return {
		"filters": {
			"disabled": 0,
			"is_pol_item": 1
		}
	};
});
var populate_child_table = (frm) => {

	if (frm.doc.fuelbook && frm.doc.total_amount) {
		frappe.call({
			method: 'populate_child_table',
			doc: frm.doc,
			callback: () => {
				cur_frm.refresh_fields()
				frm.dirty()
				get_previous_km_reading(frm);
			}
		})
	}
}
function calculate_total(frm) {
	if (frm.doc.qty && frm.doc.rate) {
		frm.set_value("total_amount", frm.doc.qty * frm.doc.rate)
		frm.set_value("outstanding_amount", frm.doc.qty * frm.doc.rate)
	}

	if (frm.doc.qty && frm.doc.rate && frm.doc.discount_amount) {
		frm.set_value("total_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
		frm.set_value("outstanding_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
	}
}

var set_equipment_filter = function (frm) {
	if (cint(frm.doc.direct_consumption) == 0) {
		frm.set_query("equipment", function () {
			return {
				query: "erpnext.fleet_management.fleet_utils.get_container_filtered",
				filters: {
					"branch": frm.doc.branch
				}
			};
		});
	}
}

var get_previous_km_reading = (frm) => {
	if (frm.doc.equipment && frm.doc.fuelbook && frm.doc.for_machineries !== 1) {
		frappe.call({
			method: 'get_previous_km_reading',
			doc: frm.doc,
			callback: (r) => {
				console.log(r.message);

				frm.set_value('previous_km', r.message);
				frm.refresh_field("previous_km");
				frm.refresh_fields()
			}
		})
	}
}



// Tanker Balance
function update_balances(frm) {
	if (frm.doc.book_type && (frm.doc.tanker || frm.doc.equipment)) {
		frappe.call({
			method: "erpnext.fleet_management.doctype.pol_receive.pol_receive.get_balance_details",
			args: {
				book_type: frm.doc.book_type,
				tanker: frm.doc.tanker,
				equipment: frm.doc.equipment,
				posting_date: frm.doc.posting_date,
				pol_type: frm.doc.pol_type
			},
			callback: function (response) {
				if (response.message) {
					frm.set_value('tanker_balance', response.message.tanker_balance);
					frm.set_value('tank_balance', response.message.tank_balance);
				}
			}
		});
	} else {
		frm.set_value('tanker_balance', 0);
		frm.set_value('tank_balance', 0);
	}
}





















