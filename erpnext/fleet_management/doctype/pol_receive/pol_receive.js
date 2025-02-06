// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("equipment", "registration_number", "equipment_number")
cur_frm.add_fetch("branch", "branch", "cost_center")
cur_frm.add_fetch("cost_center", "warehouse", "warehouse")
cur_frm.add_fetch("fuelbook", "branch", "fuelbook_branch")
cur_frm.add_fetch("equipment", "fuelbook", "own_fb")
cur_frm.add_fetch("pol_type", "item_name", "item_name")
cur_frm.add_fetch("pol_type", "stock_uom", "stock_uom")

frappe.ui.form.on('POL Receive', {
	onload: function(frm) {
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
				filterArgs = [["branch", "=", doc.branch],["type", "=", doc.book_type]]
			}

			return {
				filters: filterArgs
			}
		})
	},
	refresh: function(frm) {
		if(frm.doc.jv) {
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
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
	},
	book_type:function(frm) {
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
        } else if (frm.doc.book_type === 'Own') {
            frm.set_df_property('direct_consumption', 'hidden', 0);
            frm.set_df_property('direct_consumption', 'read_only', 0);
            frm.set_value('direct_consumption', 1);
        } else {
            frm.set_df_property('direct_consumption', 'hidden', 0);
            frm.set_df_property('direct_consumption', 'read_only', 0);
        }
		// Check if book_type is 'Common'
        if (frm.doc.book_type === 'Common') {
            frm.set_query('equipment', function() {
                return {
                    filters: {
                        equipment_type: ['in', ['Fuel Tanker', 'Barrel', 'Skid Tank', 'Skid Tank (HSD)', 'Trailer', 'Pick Up Truck', 'Excavator']],
						branch: frm.doc.branch
                    }
                };
            });
        } else {
            // Clear filter for equipment if book_type is not 'Common'
            frm.set_query('equipment', function() {
                return {
					filters: {
                        equipment_type: ['not in', ['Fuel Tanker', 'Barrel', 'Skid Tank']],
						branch: frm.doc.branch
                    }
				};
            });
        }
	},
	qty: function(frm) {
		calculate_total(frm)
		frm.events.reset_items()
		frm.refresh_fields("items")
	},
	direct_consumption:function(frm){
		set_equipment_filter(frm)
	},
	rate: function(frm) {
		frm.events.reset_items()
		frm.refresh_fields("items")
		calculate_total(frm)
	},
	get_pol_advance:function(frm){
		populate_child_table(frm)
	},
	branch:function(frm){
		frm.set_query("equipment",function(){
			return {
				filters:{
					"branch":frm.doc.branch,
					// "enabled":1
					"is_disabled": 0,
				}
			}
		})
	},
	equipment:function(frm){
		// frm.set_query("fuelbook",function(){
		// 	return {
		// 		filters:{
		// 			"equipment":frm.doc.equipment
		// 		}
		// 	}
		// })
		if (frm.doc.book_type === 'Common') {
			update_balances(frm);
		} else if (frm.doc.book_type === 'Own') {
			if (frm.doc.equipment) {
				// frappe.throw("Tanker");
				frappe.call({
					method: "erpnext.fleet_management.doctype.pol_receive.pol_receive.get_equipment_data",
					args: {
						equipment_name: frm.doc.equipment,
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
	use_common_fuelbook:function(frm){
		frm.set_query("fuelbook",function(){
			return {
				filters:{
					"type":"Common",
					"branch":frm.doc.branch
				}
			}
		})
		if(frm.doc.use_common_fuelbook){
			frm.set_query("equipment",function(){
				return {
					filters:{
						"branch":frm.doc.branch,
						// "enabled":1,
						"hired_equipment":1
					}
				}
			})
		}
		else{
			frm.set_query("equipment",function(){
				return {
					filters:{
						"branch":frm.doc.branch,
						// "enabled":1
					}
				}
			})
		}
	},
	reset_items:function(frm){
		cur_frm.clear_table("items");
	},
});

cur_frm.set_query("pol_type", function() {
	return {
		"filters": {
		"disabled": 0,
		"is_pol_item":1
		}
	};
});
var populate_child_table=(frm)=>{
	if (frm.doc.fuelbook && frm.doc.total_amount) {
		frappe.call({
			method: 'populate_child_table',
			doc: frm.doc,
			callback:  () =>{
				cur_frm.refresh_fields()
				frm.dirty()
			}
		})
	}
}
function calculate_total(frm) {
	if(frm.doc.qty && frm.doc.rate) {
		frm.set_value("total_amount", frm.doc.qty * frm.doc.rate)
		frm.set_value("outstanding_amount", frm.doc.qty * frm.doc.rate)
	}

	if(frm.doc.qty && frm.doc.rate && frm.doc.discount_amount) {
		frm.set_value("total_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
		frm.set_value("outstanding_amount", (frm.doc.qty * frm.doc.rate) - frm.doc.discount_amount)
	}
}	

var set_equipment_filter=function(frm){
	if ( cint(frm.doc.direct_consumption) == 0){
		frm.set_query("equipment", function() {
			return {
				query: "erpnext.fleet_management.fleet_utils.get_container_filtered",
				filters:{
					"branch":frm.doc.branch
				}
			};
		});
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
            callback: function(response) {
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





















