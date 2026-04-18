// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Cards', {
	refresh: function(frm) {
		frm.set_value("job_card_no", frm.doc.name);
		frm.set_query("job", "items", function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];
		
			let filters = {};
			if (row.which === "Service") {
				filters.item_group = "Service";
			}
		
			return { filters: filters };
		});
		
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
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
		
		if (frm.doc.jv && frappe.model.can_read("Journal Entry")) {
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
	
		if (frm.doc.outstanding_amount > 0 && frappe.model.can_write("Journal Entry")) {
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
		
		// Add Get Chassis No button for draft documents
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Get Chassis No'), function() {
				frm.trigger('get_chassis_no');
			}, __('Get Details From'));
		}
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
					"name",                    // Serial No / Chassis No
					"engine_no",               // Engine number
					"tvo_number",              // TVO number (could be registration)
					"item_code",               // Item code
					"item_name",               // Item name
					"make",                    // Vehicle make
					"model",                   // Vehicle model
					"model_year",              // Model year
					"color_code",              // Vehicle color
					"km_reading",              // KM reading
					"brand"                    // Brand
				]).then(r => {
					if (r && r.message) {
						// Set Chassis/VIN number
						frm.set_value("vinchassis_no", selected);
						
						// Set Engine number
						if (r.message.engine_no) {
							frm.set_value("engine_no", r.message.engine_no);
						}
						
						// Set Registration number (using tvo_number or create from make+model)
						if (r.message.tvo_number) {
							frm.set_value("registration_no", r.message.tvo_number);
						}
						
						// Set Model Name/Year (combine model and year)
						let model_nameyear = "";
						if (r.message.model) {
							model_nameyear += r.message.model;
						}
						if (r.message.model_year) {
							model_nameyear += model_nameyear ? " " + r.message.model_year : r.message.model_year;
						}
						if (model_nameyear) {
							frm.set_value("model_nameyear", model_nameyear);
						} else if (r.message.item_name) {
							frm.set_value("model_nameyear", r.message.item_name);
						}
						
						// Set Model Code
						if (r.message.make) {
							frm.set_value("model_code", r.message.make);
						}
						
						// Set Color Code
						if (r.message.color_code) {
							frm.set_value("color_code", r.message.color_code);
						}
						
						// Set Odometer Reading
						if (r.message.km_reading) {
							frm.set_value("odometer_reading_km", r.message.km_reading);
						}
						
						// Optionally set Equipment Category from brand or item
						if (r.message.brand) {
							frm.set_value("equipment_category", r.message.brand);
						}
						
						frm.refresh_field("vinchassis_no");
						frm.refresh_field("engine_no");
						frm.refresh_field("registration_no");
						frm.refresh_field("model_nameyear");
						frm.refresh_field("model_code");
						frm.refresh_field("color_code");
						frm.refresh_field("odometer_reading_km");
						frm.refresh_field("equipment_category");
						
						
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
	
	"get_items": function(frm) {
		return frappe.call({
			method: "get_job_items",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
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

//Job Card Item Details
frappe.ui.form.on("Job Cards Item", {
	"which": function(frm,cdt,cdn) {
		var item = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "job_name", '')
		frappe.model.set_value(cdt, cdn, "job", '')
		frm.refresh_field("job_name")
		frm.refresh_field("job")
	},
	"start_time": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"end_time": function(frm, cdt, cdn) {
		calculate_datetime(frm, cdt, cdn)
	},
	"job": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		var fields = ["item_name"]
		
		if(item.job) {
			var filters = {
				'name': item.job
			}
			
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Item",
					fieldname: fields,
					filters: {
						name: item.job
					}
				},
				callback: function(r) {
					frappe.model.set_value(cdt, cdn, "job_name", r.message.item_name)
					// frappe.model.set_value(cdt, cdn, "amount", r.message.cost ?? 0.0)
					cur_frm.refresh_field("job_name")
					// cur_frm.refresh_field("amount")
				}
			})
		}
	},
	amount(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},
	quantity(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	}
})

function calculate_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let total = (row.amount || 0) * (row.quantity || 0);
	
	frappe.model.set_value(cdt, cdn, "total_amount", total);
	
	let parent_total = 0;
	frm.doc.items.forEach(function(r) {
		parent_total += r.total_amount || 0;
	});
	
	frm.set_value("total_amount", parent_total);
}

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