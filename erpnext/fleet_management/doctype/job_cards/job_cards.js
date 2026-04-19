// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Cards', {
	refresh: function(frm) {
		frm.set_value("job_card_no", frm.doc.name);
		
		// Set query for job items
		frm.set_query("job", "items", function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			let filters = {};
			if (row.which === "Service") {
				filters.item_group = "Service";
			}
			return { filters: filters };
		});
		
		// Add Accounting Ledger button for submitted documents
		if(frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.finish_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
		
		// Add Bank Entries button
		if (frm.doc.jv && frappe.model.can_read("Journal Entry")) {
			frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": frm.doc.doctype,
					"Journal Entry Account.reference_name": frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
		
		// Add Receive Payment button
		if (frm.doc.outstanding_amount > 0 && frappe.model.can_write("Journal Entry")) {
			frm.add_custom_button("Receive Payment", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.fleet_management.doctype.job_cards.job_cards.make_payment_entry",
					frm: cur_frm
				})
			}, __("Receive"));
		} else {
			frm.toggle_display("receive_payment", 0);
		}
		
		frm.toggle_display("owned_by", 0);
		
		// Add Get Chassis No button for draft documents
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Get Chassis No'), function() {
				frm.trigger('get_chassis_no');
			}, __('Get Details From'));
		}
		
		// Calculate totals on form load
		calculate_all_totals(frm);
	},
	
	// Get Chassis No button handler
	get_chassis_no: function(frm) {
		if (frm.doc.docstatus !== 0) {
			frappe.msgprint(__("Cannot get chassis number for submitted document"));
			return;
		}
		
		let already_selected = [];
		if (frm.doc.vinchassis_no) {
			already_selected.push(frm.doc.vinchassis_no);
		}
		
		let msd = new frappe.ui.form.MultiSelectDialog({
			doctype: "Serial No",
			target: frm,
			setters: {
				status: "Active"
			},
			add_filters_group: 1,
			
			get_query() {
				return {
					filters: {
						status: "Active",
						name: ["not in", already_selected]
					}
				};
			},
			
			primary_action_label: "Select Chassis No",
			
			action(selections) {
				if (selections.length === 0) return;
				
				if (selections.length > 1) {
					frappe.msgprint(__("Please select only one Chassis No"));
					return;
				}
				
				let selected = selections[0];
				
				// Fetch all vehicle details from Serial No
				frappe.db.get_value("Serial No", selected, [
					"name", "engine_no", "tvo_number", "item_code",
					"item_name", "make", "model", "model_year",
					"color_code", "km_reading", "brand"
				]).then(r => {
					if (r && r.message) {
						// Set all vehicle details
						frm.set_value("vinchassis_no", selected);
						if (r.message.engine_no) frm.set_value("engine_no", r.message.engine_no);
						if (r.message.tvo_number) frm.set_value("registration_no", r.message.tvo_number);
						
						// Set Model Name/Year
						let model_nameyear = "";
						if (r.message.model) model_nameyear += r.message.model;
						if (r.message.model_year) model_nameyear += model_nameyear ? " " + r.message.model_year : r.message.model_year;
						frm.set_value("model_nameyear", model_nameyear || r.message.item_name);
						
						if (r.message.make) frm.set_value("model_code", r.message.make);
						if (r.message.color_code) frm.set_value("color_code", r.message.color_code);
						if (r.message.km_reading) frm.set_value("odometer_reading_km", r.message.km_reading);
						if (r.message.brand) frm.set_value("equipment_category", r.message.brand);
						
						frm.refresh_fields();
						msd.dialog.hide();
					}
				}).catch(err => {
					frappe.msgprint({
						title: __("Error"),
						message: __("Failed to fetch vehicle details: {0}", [err]),
						indicator: "red"
					});
				});
			}
		});
	},
	
	get_items: function(frm) {
		return frappe.call({
			method: "get_job_items",
			doc: frm.doc,
			callback: function() {
				calculate_all_totals(frm);
				frm.refresh_fields();
			}
		});
	},
	
	receive_payment: function(frm) {
		if(frm.doc.paid == 0) {
			return frappe.call({
				method: "erpnext.fleet_management.doctype.job_cards.job_cards.make_bank_entry",
				args: {
					"frm": frm.doc.name,
				},
				callback: function() {
					frm.reload_doc();
				}
			});
		}
		frm.refresh();
	}
});

// Job Card Item Details
frappe.ui.form.on("Job Cards Item", {
	which: function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "job_name", '');
		frappe.model.set_value(cdt, cdn, "job", '');
		frm.refresh_fields();
	},
	
	start_time: function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn);
	},
	
	end_time: function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn);
	},
	
	job: function(frm, cdt, cdn) {
		var item = locals[cdt][cdn];
		
		if(item.job) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Item",
					fieldname: ["item_name"],
					filters: { name: item.job }
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, "job_name", r.message.item_name);
					// Calculate total after setting job
					calculate_row_total(frm, cdt, cdn);
				}
			});
		}
	},
	
	amount: function(frm, cdt, cdn) {
		calculate_row_total(frm, cdt, cdn);
	},
	
	quantity: function(frm, cdt, cdn) {
		calculate_row_total(frm, cdt, cdn);
	}
});

// Job Card Mechanic Details
frappe.ui.form.on("Mechanic Assigned", {
	start_time: function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn);
	},
	
	end_time: function(frm, cdt, cdn) {
		calculate_time(frm, cdt, cdn);
	},
	
	mechanic: function(frm, cdt, cdn) {
		var item = locals[cdt][cdn];
		
		if (!item.mechanic) return;
		
		var doc_type = "Employee";
		if (item.employee_type == "GEP Employee") {
			doc_type = "GEP Employee";
		} else if (item.employee_type == "Muster Roll Employee") {
			doc_type = "Muster Roll Employee";
		}
		
		var name_field = doc_type === "Employee" ? "employee_name" : "person_name";
		
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: doc_type,
				fieldname: [name_field],
				filters: { name: item.mechanic }
			},
			callback: function(r) {
				if (r.message && r.message[name_field]) {
					frappe.model.set_value(cdt, cdn, "employee_name", r.message[name_field]);
					frm.refresh_fields();
				}
			}
		});
	}
});

// ========== HELPER FUNCTIONS ==========

// Calculate total for a single row and update parent total
function calculate_row_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let total = (row.amount || 0) * (row.quantity || 0);
	
	frappe.model.set_value(cdt, cdn, "total_amount", total);
	
	// Update parent total
	let parent_total = 0;
	(frm.doc.items || []).forEach(function(r) {
		parent_total += r.total_amount || 0;
	});
	
	frm.set_value("total_amount", parent_total);
}

// Calculate all totals for all rows
function calculate_all_totals(frm) {
	if (!frm.doc.items || frm.doc.items.length === 0) return;
	
	let parent_total = 0;
	frm.doc.items.forEach(function(row) {
		row.total_amount = (row.amount || 0) * (row.quantity || 0);
		parent_total += row.total_amount;
	});
	
	frm.set_value("total_amount", parent_total);
	frm.refresh_field("items");
}

// Calculate datetime difference
function calculate_datetime(frm, cdt, cdn) {
	var item = locals[cdt][cdn];
	if(item.start_time && item.end_time && item.end_time >= item.start_time) {
		frappe.model.set_value(cdt, cdn, "total_time", 
			frappe.datetime.get_hour_diff(item.end_time, item.start_time));
		frm.refresh_field("total_time");
	}
}

// Calculate time for mechanics
function calculate_time(frm, cdt, cdn) {
	var item = locals[cdt][cdn];
	if(item.start_time && item.end_time && item.end_time >= item.start_time) {
		frappe.model.set_value(cdt, cdn, "total_time", 
			frappe.datetime.get_hour_diff(item.end_time, item.start_time));
		frm.refresh_field("total_time");
	}
}

// Get entries from MIN (Standalone function)
function get_entries_from_min(form) {
	frappe.call({
		method: "erpnext.fleet_management.doctype.job_cards.job_cards.get_min_items",
		args: {
			"name": form,
		},
		callback: function(r) {
			if(r.message && r.message.length) {
				r.message.forEach(function(logbook) {
					var row = frappe.model.add_child(cur_frm.doc, "Job Card Item", "items");
					row.which = "Item";
					row.job = logbook['item_code'];
					row.job_name = logbook['item_name'];
					row.amount = logbook['amount'];
					row.quantity = 1;
					row.total_amount = (row.amount || 0) * (row.quantity || 0);
				});
				
				cur_frm.refresh_field("items");
				calculate_all_totals(cur_frm);
			}
		}
	});
}

// Legacy cscript function for compatibility
cur_frm.cscript.receive_payment = function() {
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.fleet_management.doctype.job_cards.job_cards.make_bank_entry",
		args: {
			"frm": cur_frm.doc.name,
		},
		callback: function() {
			cur_frm.reload_doc();
		},
		always: function() {
			frappe.ui.form.is_saving = false;
		}
	});
};