// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Cards', {
	// setup: function(frm){
	// 	frm.get_field('assigned_to').grid.editable_fields = [
	// 		{fieldname: 'mechanic', columns: 3},
	// 		{fieldname: 'start_time', columns: 3},
	// 		{fieldname: 'end_time', columns: 3},
	// 		{fieldname: 'total_time', columns: 1},
	// 	];		
	// },
	refresh: function(frm) {
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.finish_date,
					to_date: frm.doc.finish_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
		if (frm.doc.jv && frappe.model.can_read("Journal Entry")) {
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
	
		if (frm.doc.outstanding_amount > 0 && frm.doc.owned_by == "Others" && frappe.model.can_write("Journal Entry")) {
			//cur_frm.toggle_display("receive_payment", 1)
			/*cur_frm.add_custom_button(__('Payment'), function() {
				cur_frm.cscript.receive_payment()
			}, __("Receive"));*/
			frm.add_custom_button("Receive Payment", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.fleet_management.doctype.job_cards.job_cards.make_payment_entry",
					frm: cur_frm
				})
			}, __("Receive"));
		}
		else {
			cur_frm.toggle_display("receive_payment", 0)
		}
		
		cur_frm.toggle_display("owned_by", 0)

	},
	"receive_payment": function(frm) {
		if(frm.doc.paid == 0) {
			return frappe.call({
				method: "erpnext.fleet_management.doctype.job_cards.job_cards.make_bank_entry",
				args: {
					"frm": cur_frm.doc.name,
				},
				callback: function(r) {
				}
			});
		}
		cur_frm.refresh_field("paid")
		cur_frm.refresh_field("receive_payment")
		cur_frm.refresh()
	},
	"get_items": function(frm) {
		//get_entries_from_min(frm.doc.stock_entry)
		//load_accounts(frm.doc.company)
		return frappe.call({
			method: "get_job_items",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
	},
	"items_on_form_rendered": function(frm, grid_row, cdt, cdn) {
                var row = cur_frm.open_grid_row();
                var df = frappe.meta.get_docfield("Job Card Item", "quantity", cur_frm.doc.name)
                if(!row.grid_form.fields_dict.stock_entry.value) {
                        df.read_only = 0
                        row.grid_form.fields_dict.quantity.refresh()
                }
                else {
                        df.read_only = 1
                        row.grid_form.fields_dict.quantity.refresh()
                }
        }
});

//Job Card Item  Details
frappe.ui.form.on("Job Card Item", {
	"start_time": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"end_time": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"job": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		
		if(item.job) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: item.which,
					fieldname: ["item_name", "cost"],
					filters: {
						name: item.job
					}
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, "job_name", r.message.item_name)
					frappe.model.set_value(cdt, cdn, "amount", r.message.cost)
					cur_frm.refresh_field("job_name")
					cur_frm.refresh_field("amount")
				}
			})
		}
	}
})

function calculate_datetime(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.start_time && item.end_time && item.end_time >= item.start_time) {
		frappe.model.set_value(cdt, cdn,"total_time", frappe.datetime.get_hour_diff(item.end_time, item.start_time))
	}
	cur_frm.refresh_field("total_time")
}

//Job Card Mechanic Details
frappe.ui.form.on("Mechanic Assigned", {
	"start_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"end_time": function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn)
	},
	"mechanic": function(frm, cdt, cdn) {
                var item = locals[cdt][cdn]
                if(item.employee_type == "Employee") {
                        frappe.call({
                                method: "frappe.client.get_value",
                                args: {
                                        doctype: "Employee",
                                        fieldname: "employee_name",
                                        filters: {name: item.mechanic}
                                },
                                callback: function(r) {
                                        if(r.message.employee_name) {
                                                frappe.model.set_value(cdt, cdn, "employee_name", r.message.employee_name)
                                                cur_frm.refresh_fields()
                                        }
                                }
                        })
                }
                else {
			var doc_type = "Muster Roll Employee"
			if(item.employee_type == "GEP Employee") {
				doc_type = "GEP Employee"
			}
                        frappe.call({
                                method: "frappe.client.get_value",
                                args: {
                                        doctype: doc_type,
                                        fieldname: "person_name",
                                        filters: {name: item.mechanic}
                                },
                                callback: function(r) {
                                        if(r.message.person_name) {
                                                frappe.model.set_value(cdt, cdn, "employee_name", r.message.person_name)
                                                cur_frm.refresh_fields()
                                        }
                                }
                        })
                }
        }
})

function calculate_time(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if(item.start_time && item.end_time && item.end_time >= item.start_time) {
		frappe.model.set_value(cdt, cdn,"total_time", frappe.datetime.get_hour_diff(item.end_time, item.start_time))
	}
	cur_frm.refresh_field("total_time")
}

// cur_frm.fields_dict['assigned_to'].grid.get_field('mechanic').get_query = function(frm, cdt, cdn) {
// 	var d = locals[cdt][cdn];
//         if(d.employee_type == "Employee") {
//                 return {
//                         filters: [
//                         ['Employee', 'is_job_card_employee', '=', 1],
//                         ['Employee', 'branch', '=', frm.branch],
//                         ['Employee', 'status', '=', 'Active']
//                         ]
//                 }
//         }
// 	else if(d.employee_type == "GEP Employee") {
//                 return {
//                         filters: [
//                         ['GEP Employee', 'list_in_job_card', '=', 1],
//                         ['GEP Employee', 'branch', '=', frm.branch],
//                         ['GEP Employee', 'status', '=', 'Active']
//                         ]
//                 }
// 	}
//         else {
//                 return {
//                         filters: [
//                         ['Muster Roll Employee', 'list_in_job_card', '=', 1],
//                         ['Muster Roll Employee', 'branch', '=', frm.branch],
//                         ['Muster Roll Employee', 'status', '=', 'Active']
//                         ]
//                 }
//         }
// }

function get_entries_from_min(form) {
	frappe.call({
		method: "erpnext.fleet_management.doctype.job_cards.job_cards.get_min_items",
		async: false,
		args: {
			"name": form,
		},
		callback: function(r) {
			if(r.message) {
				var total_amount = 0;
				r.message.forEach(function(logbook) {
				        var row = frappe.model.add_child(cur_frm.doc, "Job Card Item", "items");
					row.which = "Item"
					row.job = logbook['item_code']
					row.job_name = logbook['item_name']
					row.amount = logbook['amount']
				})
				cur_frm.refresh_field("items")
			}
		}
	})
}

cur_frm.cscript.receive_payment = function(){
	var doc = cur_frm.doc;
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.fleet_management.doctype.job_cards.job_cards.make_bank_entry",
		args: {
			"frm": cur_frm.doc.name,
		},
		callback: function(r){
			cur_frm.reload_doc();
		},
		always: function() {
			frappe.ui.form.is_saving = false;
		}
	});
}


