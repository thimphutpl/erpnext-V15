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
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today());
		}
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
		if(frm.doc.book_type == 'Own') {
			frm.set_value("direct_consumption", 1)
		}
		if(frm.doc.book_type == 'Common') {
			frm.set_value("direct_consumption", 0)
		}
		frm.refresh_fields("direct_consumption")
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
		frm.set_query("fuelbook",function(){
			return {
				filters:{
					"equipment":frm.doc.equipment
				}
			}
		})
		// if (frm.doc.equipment) {
        //     frappe.call({
        //         method: "erpnext.fleet_management.doctype.pol_receive.pol_receive.fetch_tank_balance",
        //         args: {
        //             equipment: frm.doc.equipment
        //         },
        //         callback: function(response) {
        //             if (response.message) {
        //                 frm.set_value('tank_balance', response.message);
        //             }
        //         }
        //     });
        // } else {
        //     frm.set_value('tank_balance', '');
        // }
		
		if (frm.doc.equipment) {
            frappe.call({
                method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_data", // Update with the correct path
                args: {
                    equipment_name: frm.doc.equipment,
                    to_date: frm.doc.to_date,
                    all_equipment: frm.doc.all_equipment || 0,
                    branch: frm.doc.branch
                },
                callback: function(response) {
                    if (response.message) {
                        let data = response.message;

                        // Process and display the fetched data
                        frappe.msgprint({
                            title: __('Fetched Equipment Data'),
                            message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
                            indicator: 'green'
                        });

                        // Optional: You can set a field value with specific data
                        if (data.length > 0) {
                            frm.set_value('tank_balance', data[0].balance);
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
