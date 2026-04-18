// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.stock");

cur_frm.cscript.tax_table = "Purchase Taxes and Charges";

erpnext.accounts.taxes.setup_tax_filters("Purchase Taxes and Charges");
erpnext.accounts.taxes.setup_tax_validations("Purchase Receipt");
erpnext.buying.setup_buying_controller();

frappe.ui.form.on("Purchase Receipt", {
	setup: (frm) => {
		frm.make_methods = {
			"Landed Cost Voucher": () => {
				let lcv = frappe.model.get_new_doc("Landed Cost Voucher");
				lcv.company = frm.doc.company;

				let lcv_receipt = frappe.model.get_new_doc("Landed Cost Purchase Receipt");
				lcv_receipt.receipt_document_type = "Purchase Receipt";
				lcv_receipt.receipt_document = frm.doc.name;
				lcv_receipt.supplier = frm.doc.supplier;
				lcv_receipt.grand_total = frm.doc.grand_total;
				lcv.purchase_receipts = [lcv_receipt];

				frappe.set_route("Form", lcv.doctype, lcv.name);
			},
		};

		frm.custom_make_buttons = {
			"Stock Entry": "Return",
			"Purchase Invoice": "Purchase Invoice",
		};

		frm.set_query("expense_account", "items", function () {
			return {
				query: "erpnext.controllers.queries.get_expense_account",
				filters: { company: frm.doc.company },
			};
		});

		frm.set_query("wip_composite_asset", "items", function () {
			return {
				filters: { is_composite_asset: 1, docstatus: 0 },
			};
		});

		frm.set_query("taxes_and_charges", function () {
			return {
				filters: { company: frm.doc.company },
			};
		});

		frm.set_query("subcontracting_receipt", function () {
			return {
				filters: {
					docstatus: 1,
					supplier: frm.doc.supplier,
				},
			};
		});

		frm.set_query("branch", function (doc) {
			return {
				filters: { company: doc.company },
			};
		});
	},
	onload: function (frm) {
		erpnext.queries.setup_queries(frm, "Warehouse", function () {
			return erpnext.queries.warehouse(frm.doc);
		});
		frm.set_value("disable_rounded_total", 1);
	},

	refresh: function (frm) {

		if (frm.doc.company) {
			frm.trigger("toggle_display_account_head");
		}

		if (frm.doc.docstatus === 1 && frm.doc.is_return === 1 && frm.doc.per_billed !== 100) {
			frm.add_custom_button(
				__("Debit Note"),
				function () {
					frappe.model.open_mapped_doc({
						method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
						frm: cur_frm,
					});
				},
				__("Create")
			);
			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}

		if (frm.doc.docstatus === 1 && frm.doc.is_internal_supplier && !frm.doc.inter_company_reference) {
			frm.add_custom_button(
				__("Delivery Note"),
				function () {
					frappe.model.open_mapped_doc({
						method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_inter_company_delivery_note",
						frm: cur_frm,
					});
				},
				__("Create")
			);
		}

		if (frm.doc.docstatus === 0) {
			if (!frm.doc.is_return) {
				frappe.db.get_single_value("Buying Settings", "maintain_same_rate").then((value) => {
					if (value) {
						frm.doc.items.forEach((item) => {
							frm.fields_dict.items.grid.update_docfield_property(
								"rate",
								"read_only",
								item.purchase_order && item.purchase_order_item
							);
						});
					}
				});
			}
		}

		frm.events.add_custom_buttons(frm);
	},

	add_custom_buttons: function (frm) {
		if (frm.doc.docstatus == 0) {
			frm.add_custom_button(
				__("Purchase Invoice"),
				function () {
					if (!frm.doc.supplier) {
						frappe.throw({
							title: __("Mandatory"),
							message: __("Please Select a Supplier"),
						});
					}
					erpnext.utils.map_current_doc({
						method: "erpnext.accounts.doctype.purchase_invoice.purchase_invoice.make_purchase_receipt",
						source_doctype: "Purchase Invoice",
						target: frm,
						setters: {
							supplier: frm.doc.supplier,
						},
						get_query_filters: {
							docstatus: 1,
							per_received: ["<", 100],
							company: frm.doc.company,
						},
					});
				},
				__("Get Items From")
			);
		}
	},

	company: function (frm) {
		frm.trigger("toggle_display_account_head");
		erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
	},
	rate_per_kl: function(frm){
		frm.doc.set_value("cost_per_l", flt(rate_per_kl/1000, 2))
		frm.refresh_field("cost_per_l");
	},
	cost_per_l: function(frm){
        frm.doc.dip_details.forEach(row => {
            calculate_total_and_variance(frm, row.doctype, row.name);
        });
	},
	ug_qty: function(frm){
        frm.doc.dip_details.forEach(row => {
            calculate_total_and_variance(frm, row.doctype, row.name);
        });
	},
	subcontracting_receipt: (frm) => {
		if (
			frm.doc.is_subcontracted === 1 &&
			frm.doc.is_old_subcontracting_flow === 0 &&
			frm.doc.subcontracting_receipt
		) {
			frm.set_value("items", null);

			erpnext.utils.map_current_doc({
				method: "erpnext.subcontracting.doctype.subcontracting_receipt.subcontracting_receipt.make_purchase_receipt",
				source_name: frm.doc.subcontracting_receipt,
				target_doc: frm,
				freeze: true,
				freeze_message: __("Mapping Purchase Receipt ..."),
			});
		}
	},

	toggle_display_account_head: function (frm) {
		var enabled = erpnext.is_perpetual_inventory_enabled(frm.doc.company);
		frm.fields_dict["items"].grid.set_column_disp(["cost_center"], enabled);
	},

	freight_insurance_charges: function(frm) {
		calculate_discount(frm)
	},

	discount: function(frm) {
		calculate_discount(frm)
	},

	other_charges: function(frm) {
		calculate_discount(frm)
	},

	tax: function(frm) {
		calculate_discount(frm)
	},
});

function calculate_discount(frm) {
	console.log(frm.doc.freight_insurance_charges + frm.doc.other_charges - frm.doc.discount);
	frm.set_value("total_add_ded", flt(frm.doc.freight_insurance_charges + frm.doc.other_charges + frm.doc.tax - frm.doc.discount)??0);
	frm.set_value("discount_amount", flt(-frm.doc.freight_insurance_charges - frm.doc.other_charges - frm.doc.tax + frm.doc.discount)??0);
	frm.refresh_field("discount_amount");
	frm.refresh_field("total_add_ded");
}

erpnext.stock.PurchaseReceiptController = class PurchaseReceiptController extends (
	erpnext.buying.BuyingController
) {
	setup(doc) {
		this.setup_posting_date_time_check();
		super.setup(doc);
	}

	refresh() {
		var me = this;
		super.refresh();

		erpnext.accounts.ledger_preview.show_accounting_ledger_preview(this.frm);
		erpnext.accounts.ledger_preview.show_stock_ledger_preview(this.frm);

		if (this.frm.doc.docstatus > 0) {
			this.show_stock_ledger();
			//removed for temporary
			this.show_general_ledger();

			// this.frm.add_custom_button(
			// 	__("Asset"),
			// 	function () {
			// 		frappe.route_options = {
			// 			purchase_receipt: me.frm.doc.name,
			// 		};
			// 		frappe.set_route("List", "Asset");
			// 	},
			// 	__("View")
			// );

			// this.frm.add_custom_button(
			// 	__("Asset Movement"),
			// 	function () {
			// 		frappe.route_options = {
			// 			reference_name: me.frm.doc.name,
			// 		};
			// 		frappe.set_route("List", "Asset Movement");
			// 	},
			// 	__("View")
			// );
		}

		if (!this.frm.doc.is_return && this.frm.doc.status != "Closed") {
			if (this.frm.doc.docstatus == 0) {
				this.frm.add_custom_button(
					__("Purchase Order"),
					function () {
						if (!me.frm.doc.supplier) {
							frappe.throw({
								title: __("Mandatory"),
								message: __("Please Select a Supplier"),
							});
						}
						erpnext.utils.map_current_doc({
							method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
							source_doctype: "Purchase Order",
							target: me.frm,
							setters: {
								supplier: me.frm.doc.supplier,
								schedule_date: undefined,
							},
							get_query_filters: {
								docstatus: 1,
								status: ["not in", ["Closed", "On Hold"]],
								per_received: ["<", 99.99],
								company: me.frm.doc.company,
							},
						});
					},
					__("Get Items From")
				);
			}

			if (this.frm.doc.docstatus == 1 && this.frm.doc.status != "Closed") {
				if (this.frm.has_perm("submit")) {
					cur_frm.add_custom_button(__("Close"), this.close_purchase_receipt, __("Status"));
				}

				cur_frm.add_custom_button(__("Purchase Return"), this.make_purchase_return, __("Create"));

				// cur_frm.add_custom_button(
				// 	__("Make Stock Entry"),
				// 	cur_frm.cscript["Make Stock Entry"],
				// 	__("Create")
				// );

				if (flt(this.frm.doc.per_billed) < 100) {
					cur_frm.add_custom_button(
						__("Purchase Invoice"),
						this.make_purchase_invoice,
						__("Create")
					);
				}
				// cur_frm.add_custom_button(
				// 	__("Retention Stock Entry"),
				// 	this.make_retention_stock_entry,
				// 	__("Create")
				// );

				cur_frm.add_custom_button(__('Asset Issue Entry'), this.make_asset_issue_entry, __('Create'));
				cur_frm.page.set_inner_btn_group_as_primary(__("Create"));
			}
		}

		if (this.frm.doc.docstatus == 1 && this.frm.doc.status === "Closed" && this.frm.has_perm("submit")) {
			cur_frm.add_custom_button(__("Reopen"), this.reopen_purchase_receipt, __("Status"));
		}

		this.frm.toggle_reqd("supplier_warehouse", this.frm.doc.is_old_subcontracting_flow);
	}

	make_purchase_invoice() {
		frappe.model.open_mapped_doc({
			method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
			frm: cur_frm,
		});
	}

	make_purchase_return() {
		let me = this;

		let has_rejected_items = cur_frm.doc.items.filter((item) => {
			if (item.rejected_qty > 0) {
				return true;
			}
		});

		if (has_rejected_items && has_rejected_items.length > 0) {
			frappe.prompt(
				[
					{
						label: __("Return Qty from Rejected Warehouse"),
						fieldtype: "Check",
						fieldname: "return_for_rejected_warehouse",
						default: 1,
					},
				],
				function (values) {
					if (values.return_for_rejected_warehouse) {
						frappe.call({
							method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return_against_rejected_warehouse",
							args: {
								source_name: cur_frm.doc.name,
							},
							callback: function (r) {
								if (r.message) {
									frappe.model.sync(r.message);
									frappe.set_route("Form", r.message.doctype, r.message.name);
								}
							},
						});
					} else {
						cur_frm.cscript._make_purchase_return();
					}
				},
				__("Return Qty"),
				__("Make Return Entry")
			);
		} else {
			cur_frm.cscript._make_purchase_return();
		}
	}

	close_purchase_receipt() {
		cur_frm.cscript.update_status("Closed");
	}

	reopen_purchase_receipt() {
		cur_frm.cscript.update_status("Submitted");
	}

	make_retention_stock_entry() {
		frappe.call({
			method: "erpnext.stock.doctype.stock_entry.stock_entry.move_sample_to_retention_warehouse",
			args: {
				company: cur_frm.doc.company,
				items: cur_frm.doc.items,
			},
			callback: function (r) {
				if (r.message) {
					var doc = frappe.model.sync(r.message)[0];
					frappe.set_route("Form", doc.doctype, doc.name);
				} else {
					frappe.msgprint(
						__("Purchase Receipt doesn't have any Item for which Retain Sample is enabled.")
					);
				}
			},
		});
	}

	make_asset_issue_entry() {
		var doc = cur_frm.doc;
		var dialog = new frappe.ui.Dialog({
			title: __("For Issuing Asset"),
			fields: [
				{	"fieldtype": "Select",
					"label": __("Material Name"),
					"fieldname": "item_name",
					"options": doc.items
						.filter(d => d.is_fixed_asset === 1)
						.map(d => d.idx+' '+d.item_name),
					"reqd": 1 
				},
				{	"fieldtype": "Button", "label": __('Issue Asset'),
					"fieldname": "make_asset_issue_entry", "cssClass": "btn-primary"
				},
			]
		});
		
		dialog.fields_dict.make_asset_issue_entry.$input.click(function() {
			var args = dialog.get_values();
			var item = args.item_name;
			var itemIdx = item.substr(0, item.indexOf(" "));
			var itemName = item.substr(item.indexOf(" "), item.length - 1);

			frappe.call({
				method:'frappe.client.get_value',
				args:{
					'doctype':'Item',
					fieldname:"is_fixed_asset",
					filters: {
						"item_name": itemName.trim(),
						"is_fixed_asset":1
					}
				},
				callback:(r)=>{
					if(r.message){
						if ( !r.message.is_fixed_asset){
							frappe.msgprint('Item selected is not a fixed asset')
							dialog.hide();
							return;
						}
	
						if(!args) return;
						dialog.hide();
	
						let business_activity = ''
						let item_code = ''
						let asset_rate = ''
						cur_frm.doc.items.map(d => {
							if (d.idx == itemIdx){
								business_activity = d.business_activity;
								item_code = d.item_code;
								asset_rate = d.valuation_rate;
							}
	
						})
	
						var new_doc = frappe.model.get_new_doc('Asset Issue Details');
						new_doc.branch = cur_frm.doc.branch;
						new_doc.business_activity = business_activity;
						new_doc.entry_date = new Date().toJSON().slice(0,10).replace(/-/g,'-');
						new_doc.item_code = item_code;
						new_doc.purchase_receipt = cur_frm.docname;
						new_doc.asset_rate = asset_rate
						new_doc.purchase_date = cur_frm.doc.posting_date
						new_doc.company = cur_frm.doc.company
						new_doc.qty = 1;
						new_doc.amount = asset_rate * new_doc.qty
						frappe.set_route('Form', 'Asset Issue Details', new_doc.name);
					} else{
						frappe.msgprint('There no such item')
						dialog.hide();
						return;
					}
				}
			})
		});
		dialog.show()
	}
	
	apply_putaway_rule() {
		if (this.frm.doc.apply_putaway_rule) erpnext.apply_putaway_rule(this.frm);
	}
};

// for backward compatibility: combine new and previous states
extend_cscript(cur_frm.cscript, new erpnext.stock.PurchaseReceiptController({ frm: cur_frm }));

cur_frm.cscript.update_status = function (status) {
	frappe.ui.form.is_saving = true;
	frappe.call({
		method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.update_purchase_receipt_status",
		args: { docname: cur_frm.doc.name, status: status },
		callback: function (r) {
			if (!r.exc) cur_frm.reload_doc();
		},
		always: function () {
			frappe.ui.form.is_saving = false;
		},
	});
};

cur_frm.fields_dict["items"].grid.get_field("project").get_query = function (doc, cdt, cdn) {
	return {
		filters: [["Project", "status", "not in", "Completed, Cancelled"]],
	};
};

cur_frm.fields_dict["select_print_heading"].get_query = function (doc, cdt, cdn) {
	return {
		filters: [["Print Heading", "docstatus", "!=", "2"]],
	};
};

cur_frm.fields_dict["items"].grid.get_field("bom").get_query = function (doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		filters: [
			["BOM", "item", "=", d.item_code],
			["BOM", "is_active", "=", "1"],
			["BOM", "docstatus", "=", "1"],
		],
	};
};

frappe.provide("erpnext.buying");

frappe.ui.form.on("Purchase Receipt", "is_subcontracted", function (frm) {
	if (frm.doc.is_old_subcontracting_flow) {
		erpnext.buying.get_default_bom(frm);
	}

	frm.toggle_reqd("supplier_warehouse", frm.doc.is_old_subcontracting_flow);
});

frappe.ui.form.on("Purchase Receipt Item", {
	refresh: function(frm, cdt, cdn){
		var i = locals[cdt][cdn];
		frappe.call({
			method:'frappe.client.get_value',
			args:{
				'doctype':'Item',
				fieldname:"is_fixed_asset",
				filters: {
					"name": i.name
				}
			},
			callback:(r)=>{
				if(r.message.is_fixed_asset){
					frm.toggle_display(['brand', 'model'], r.message.is_fixed_asset);
				}
				else{
					frm.toggle_display(['brand', 'model'], 0);
					
				}
			}
		})
		frm.refresh_fields();
	},
	item_code: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.db.get_value("Item", { name: d.item_code }, "sample_quantity", (r) => {
			frappe.model.set_value(cdt, cdn, "sample_quantity", r.sample_quantity);
			validate_sample_quantity(frm, cdt, cdn);
		});
		frappe.call({
			method:'frappe.client.get_value',
			args:{
				'doctype':'Item',
				fieldname:"is_fixed_asset",
				filters: {
					"name": d.name
				}
			},
			callback:(r)=>{
				if(r.message.is_fixed_asset){
					frm.toggle_display(['brand', 'model'], r.message.is_fixed_asset);
				}
				else{
					frm.toggle_display(['brand', 'model'], 0);
					
				}
			}
		})
		frm.refresh_fields();
	},
	qty: function (frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
	sample_quantity: function (frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
	batch_no: function (frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
});

cur_frm.cscript._make_purchase_return = function () {
	frappe.model.open_mapped_doc({
		method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return",
		frm: cur_frm,
	});
};

cur_frm.cscript["Make Stock Entry"] = function () {
	frappe.model.open_mapped_doc({
		method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_stock_entry",
		frm: cur_frm,
	});
};

var validate_sample_quantity = function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.sample_quantity && d.qty) {
		frappe.call({
			method: "erpnext.stock.doctype.stock_entry.stock_entry.validate_sample_quantity",
			args: {
				batch_no: d.batch_no,
				item_code: d.item_code,
				sample_quantity: d.sample_quantity,
				qty: d.qty,
			},
			callback: (r) => {
				frappe.model.set_value(cdt, cdn, "sample_quantity", r.message);
			},
		});
	}
};

frappe.ui.form.on("Dip Details", {
	c_i: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_i, item.c_i_qty, item.a_i, "a_i_qty", "I")
		calculate_total_and_variance(frm, cdt, cdn);

	},
	c_ii: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_ii, item.c_ii_qty, item.a_ii, "a_ii_qty", "II")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_iii: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_iii, item.c_iii_qty, item.a_iii, "a_iii_qty", "III")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_iv: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, c_iv, c_iv_qty, a_iv, "a_iv_qty", "IV")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_v: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_v, item.c_v_qty, item.a_v, "a_v_qty", "V")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_vi: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_vi, item.c_vi_qty, item.a_vi, "a_vi_qty", "VI")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_i_qty: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_i, item.c_i_qty, item.a_i, "a_i_qty", "I")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_ii_qty: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_ii, item.c_ii_qty, item.a_ii, "a_ii_qty", "II")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_iii_qty: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_iii, item.c_iii_qty, item.a_iii, "a_iii_qty", "III")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_iv_qty: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, c_iv, c_iv_qty, a_iv, "a_iv_qty", "IV")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_v_qty: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_v, item.c_v_qty, item.a_v, "a_v_qty", "V")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	c_vi_qty: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_vi, item.c_vi_qty, item.a_vi, "a_vi_qty", "VI")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	a_i: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_i, item.c_i_qty, item.a_i, "a_i_qty", "I")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	a_ii: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_ii, item.c_ii_qty, item.a_ii, "a_ii_qty", "II")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	a_iii: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_iii, item.c_iii_qty, item.a_iii, "a_iii_qty", "III")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	a_iv: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, c_iv, c_iv_qty, a_iv, "a_iv_qty", "IV")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	a_v: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_v, item.c_v_qty, item.a_v, "a_v_qty", "V")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	a_vi: function(frm, cdt, cdn){
		var item = locals[cdt][cdn];
		calculate_actual_dip_qty(frm, cdt, cdn, item.c_vi, item.c_vi_qty, item.a_vi, "a_vi_qty", "VI")
		calculate_total_and_variance(frm, cdt, cdn);
	},
	item_code: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.db.get_value("Item", { name: d.item_code }, "sample_quantity", (r) => {
			frappe.model.set_value(cdt, cdn, "sample_quantity", r.sample_quantity);
			validate_sample_quantity(frm, cdt, cdn);
		});
		frappe.call({
			method:'frappe.client.get_value',
			args:{
				'doctype':'Item',
				fieldname:"is_fixed_asset",
				filters: {
					"name": d.name
				}
			},
			callback:(r)=>{
				if(r.message.is_fixed_asset){
					frm.toggle_display(['brand', 'model'], r.message.is_fixed_asset);
				}
				else{
					frm.toggle_display(['brand', 'model'], 0);
					
				}
			}
		})
		frm.refresh_fields();
	},
	qty: function (frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
	sample_quantity: function (frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
	batch_no: function (frm, cdt, cdn) {
		validate_sample_quantity(frm, cdt, cdn);
	},
});

var calculate_actual_dip_qty = function(frm, cdt, cdn, calibrated_dip, calibrated_qty, actual_dip, actual_qty_fn, actual_dip_fn){
	if(flt(actual_dip,2) > flt(calibrated_dip,2)){
		frappe.throw("Actual Dip cannot be more than Calibrated Dip for Actual Dip "+actual_dip_fn)
	}
	var unit_dip = flt(flt(calibrated_qty)/flt(calibrated_dip),2)
	var actual_dip = flt(unit_dip*flt(actual_dip), 2)
	frappe.model.set_value(cdt, cdn, actual_qty_fn, actual_dip)
}

var calculate_total_and_variance = function(frm, cdt, cdn){
	var item = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "c_total", flt(flt(item.c_i)+flt(item.c_ii)+flt(item.c_iii)+flt(item.c_iv)+flt(item.c_v)+flt(item.c_vi),2))
	frappe.model.set_value(cdt, cdn, "c_total_qty", flt(flt(item.c_i_qty)+flt(item.c_ii_qty)+flt(item.c_iii_qty)+flt(item.c_iv_qty)+flt(item.c_v_qty)+flt(item.c_vi_qty),2))
	frappe.model.set_value(cdt, cdn, "a_total", flt(flt(item.a_i)+flt(item.a_ii)+flt(item.a_iii)+flt(item.a_iv)+flt(item.a_v)+flt(item.a_vi),2))
	frappe.model.set_value(cdt, cdn, "a_total_qty", flt(flt(item.a_i_qty)+flt(item.a_ii_qty)+flt(item.a_iii_qty)+flt(item.a_iv_qty)+flt(item.a_v_qty)+flt(item.a_vi_qty),2))
	frappe.model.set_value(cdt, cdn, "variance_in_dip", flt(item.c_total - item.a_total,2))
	frappe.model.set_value(cdt, cdn, "variance_in_litres", flt(item.c_total_qty - item.a_total_qty,2))
	frappe.model.set_value(cdt, cdn, "variance_in_amount", flt(item.variance_in_litres * frm.doc.cost_per_l,2))
	if(flt(item.idx) == flt(frm.doc.items.length)){
		frm.set_value("dispatch_qty", item.c_total_qty);
		frm.set_value("receipt_qty", item.a_total_qty);
		frm.set_value("shrinkage_qty", item.variance_in_litres);
		frm.set_value("shrinkage_amt", item.variance_in_amount);
	}
	frm.set_value("ug_loss_ltrs", flt(frm.doc.receipt_qty-frm.doc.ug_qty,2))
	frm.set_value("ug_loss_amt", flt(frm.doc.ug_loss_ltrs*frm.doc.cost_per_l,2))
	frm.refresh_field("receipt_qty");
	frm.refresh_field("shrinkage_qty");
	frm.refresh_field("shrinkage_amt");
	frm.refresh_field("ug_loss_ltrs");
	frm.refresh_field("ug_loss_amt");
	frm.refresh_field("dip_details");
}

cur_frm.cscript._make_purchase_return = function () {
	frappe.model.open_mapped_doc({
		method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return",
		frm: cur_frm,
	});
};

cur_frm.cscript["Make Stock Entry"] = function () {
	frappe.model.open_mapped_doc({
		method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_stock_entry",
		frm: cur_frm,
	});
};

var validate_sample_quantity = function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.sample_quantity && d.qty) {
		frappe.call({
			method: "erpnext.stock.doctype.stock_entry.stock_entry.validate_sample_quantity",
			args: {
				batch_no: d.batch_no,
				item_code: d.item_code,
				sample_quantity: d.sample_quantity,
				qty: d.qty,
			},
			callback: (r) => {
				frappe.model.set_value(cdt, cdn, "sample_quantity", r.message);
			},
		});
	}
};





// // previous stcbl code

// // Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// // License: GNU General Public License v3. See license.txt

// {% include 'erpnext/public/js/controllers/buying.js' %};

// frappe.provide("erpnext.stock");

// frappe.ui.form.on("Purchase Receipt", {
// 	setup: (frm) => {
// 		frm.make_methods = {
// 			'Landed Cost Voucher': () => {
// 				let lcv = frappe.model.get_new_doc('Landed Cost Voucher');
// 				lcv.company = frm.doc.company;
// 				let lcv_receipt = frappe.model.get_new_doc('Landed Cost Purchase Receipt');
// 				lcv_receipt.receipt_document_type = 'Purchase Receipt';
// 				lcv_receipt.receipt_document = frm.doc.name;
// 				lcv_receipt.supplier = frm.doc.supplier;
// 				lcv_receipt.grand_total = frm.doc.grand_total;
// 				lcv.purchase_receipts = [lcv_receipt];

// 				frappe.set_route("Form", lcv.doctype, lcv.name);
// 			},
// 		}

// 		frm.custom_make_buttons = {
// 			'Stock Entry': 'Return',
// 			'Purchase Invoice': 'Purchase Invoice'
// 		};

// 		frm.set_query("expense_account", "items", function() {
// 			return {
// 				query: "erpnext.controllers.queries.get_expense_account",
// 				filters: {'company': frm.doc.company }
// 			}
// 		});

// 		frm.set_query("taxes_and_charges", function() {
// 			return {
// 				filters: {'company': frm.doc.company }
// 			}
// 		});

// 	},
// 	onload: function(frm) {
// 		erpnext.queries.setup_queries(frm, "Warehouse", function() {
// 			return erpnext.queries.warehouse(frm.doc);
// 		});
// 	},

// 	refresh: function(frm) {
// 		if(frm.doc.company) {
// 			frm.trigger("toggle_display_account_head");
// 		}

// 		var other_vendor_payment = false;

// 		for (var i in frm.doc.taxes) {
// 			var tax = frm.doc.taxes[i];
// 			if (tax.payable_to_different_vendor === 1 && !tax.reference_no){
// 				other_vendor_payment = true;
// 			}
// 		}

// 		if (frm.doc.docstatus === 1 && frm.doc.is_return === 1 && frm.doc.per_billed !== 100) {
// 			frm.add_custom_button(__('Debit Note'), function() {
// 				frappe.model.open_mapped_doc({
// 					method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
// 					frm: cur_frm,
// 				})
// 			}, __('Create'));
// 			frm.page.set_inner_btn_group_as_primary(__('Create'));
// 		}

// 		if (frm.doc.docstatus === 1 && frm.doc.is_internal_supplier && !frm.doc.inter_company_reference) {
// 			frm.add_custom_button(__('Delivery Note'), function() {
// 				frappe.model.open_mapped_doc({
// 					method: 'erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_inter_company_delivery_note',
// 					frm: cur_frm,
// 				})
// 			}, __('Create'));
// 		}

// 		if (frm.doc.docstatus == 1 && other_vendor_payment) {
// 			frm.add_custom_button( __('Payment for Charges'), () => {
// 				frappe.model.open_mapped_doc({
// 					method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_charges_advance_payment",
// 					frm: cur_frm
// 				});
// 				}, __('Create'));	
// 		}

// 		frm.events.add_custom_buttons(frm);
// 	},

// 	add_custom_buttons: function(frm) {
// 		if (frm.doc.docstatus == 0) {
// 			frm.add_custom_button(__('Purchase Invoice'), function () {
// 				if (!frm.doc.supplier) {
// 					frappe.throw({
// 						title: __("Mandatory"),
// 						message: __("Please Select a Supplier")
// 					});
// 				}
// 				erpnext.utils.map_current_doc({
// 					method: "erpnext.accounts.doctype.purchase_invoice.purchase_invoice.make_purchase_receipt",
// 					source_doctype: "Purchase Invoice",
// 					target: frm,
// 					setters: {
// 						supplier: frm.doc.supplier,
// 					},
// 					get_query_filters: {
// 						docstatus: 1,
// 						per_received: ["<", 100],
// 						company: frm.doc.company
// 					}
// 				})
// 			}, __("Get Items From"));
// 		}
// 	},

// 	company: function(frm) {
// 		frm.trigger("toggle_display_account_head");
// 		erpnext.accounts.dimensions.update_dimension(frm, frm.doctype);
// 	},

// 	toggle_display_account_head: function(frm) {
// 		var enabled = erpnext.is_perpetual_inventory_enabled(frm.doc.company)
// 		frm.fields_dict["items"].grid.set_column_disp(["cost_center"], enabled);
// 	},
// });

// erpnext.stock.PurchaseReceiptController = class PurchaseReceiptController extends erpnext.buying.BuyingController {
// 	setup(doc) {
// 		this.setup_posting_date_time_check();
// 		super.setup(doc);
// 	}

// 	refresh() {
// 		var me = this;
// 		super.refresh();
// 		if(this.frm.doc.docstatus > 0) {
// 			this.show_stock_ledger();
// 			//removed for temporary
// 			this.show_general_ledger();

// 			this.frm.add_custom_button(__('Asset'), function() {
// 				frappe.route_options = {
// 					purchase_receipt: me.frm.doc.name,
// 				};
// 				frappe.set_route("List", "Asset");
// 			}, __("View"));

// 			this.frm.add_custom_button(__('Asset Movement'), function() {
// 				frappe.route_options = {
// 					reference_name: me.frm.doc.name,
// 				};
// 				frappe.set_route("List", "Asset Movement");
// 			}, __("View"));
// 		}

// 		if(!this.frm.doc.is_return && this.frm.doc.status!="Closed") {
// 			if (this.frm.doc.docstatus == 0) {
// 				this.frm.add_custom_button(__('Purchase Order'),
// 					function () {
// 						if (!me.frm.doc.supplier) {
// 							frappe.throw({
// 								title: __("Mandatory"),
// 								message: __("Please Select a Supplier")
// 							});
// 						}
// 						erpnext.utils.map_current_doc({
// 							method: "erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt",
// 							source_doctype: "Purchase Order",
// 							target: me.frm,
// 							setters: {
// 								supplier: me.frm.doc.supplier,
// 								schedule_date: undefined
// 							},
// 							get_query_filters: {
// 								docstatus: 1,
// 								status: ["not in", ["Closed", "On Hold"]],
// 								per_received: ["<", 99.99],
// 								company: me.frm.doc.company
// 							}
// 						})
// 					}, __("Get Items From"));
// 			}

// 			if(this.frm.doc.docstatus == 1 && this.frm.doc.status!="Closed") {
// 				if (this.frm.has_perm("submit")) {
// 					cur_frm.add_custom_button(__("Close"), this.close_purchase_receipt, __("Status"))
// 				}

// 				cur_frm.add_custom_button(__('Purchase Return'), this.make_purchase_return, __('Create'));

// 				cur_frm.add_custom_button(__('Make Stock Entry'), cur_frm.cscript['Make Stock Entry'], __('Create'));

// 				if(flt(this.frm.doc.per_billed) < 100) {
// 					cur_frm.add_custom_button(__('Purchase Invoice'), this.make_purchase_invoice, __('Create'));
// 				}
// 				// cur_frm.add_custom_button(__('Retention Stock Entry'), this.make_retention_stock_entry, __('Create'));

// 				// if(!this.frm.doc.auto_repeat) {
// 				// 	cur_frm.add_custom_button(__('Subscription'), function() {
// 				// 		erpnext.utils.make_subscription(me.frm.doc.doctype, me.frm.doc.name)
// 				// 	}, __('Create'))
// 				// }
// 				cur_frm.add_custom_button(__('Asset Issue Entry'), this.make_asset_issue_entry, __('Create'));
// 				cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
// 			}
// 		}


// 		if(this.frm.doc.docstatus==1 && this.frm.doc.status === "Closed" && this.frm.has_perm("submit")) {
// 			cur_frm.add_custom_button(__('Reopen'), this.reopen_purchase_receipt, __("Status"))
// 		}

// 		this.frm.toggle_reqd("supplier_warehouse", this.frm.doc.is_old_subcontracting_flow);
// 	}

// 	make_purchase_invoice() {
// 		frappe.model.open_mapped_doc({
// 			method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_invoice",
// 			frm: cur_frm
// 		})
// 	}

// 	make_purchase_return() {
// 		frappe.model.open_mapped_doc({
// 			method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_purchase_return",
// 			frm: cur_frm
// 		})
// 	}

// 	close_purchase_receipt() {
// 		cur_frm.cscript.update_status("Closed");
// 	}

// 	reopen_purchase_receipt() {
// 		cur_frm.cscript.update_status("Submitted");
// 	}

// 	make_retention_stock_entry() {
// 		frappe.call({
// 			method: "erpnext.stock.doctype.stock_entry.stock_entry.move_sample_to_retention_warehouse",
// 			args:{
// 				"company": cur_frm.doc.company,
// 				"items": cur_frm.doc.items
// 			},
// 			callback: function (r) {
// 				if (r.message) {
// 					var doc = frappe.model.sync(r.message)[0];
// 					frappe.set_route("Form", doc.doctype, doc.name);
// 				}
// 				else {
// 					frappe.msgprint(__("Purchase Receipt doesn't have any Item for which Retain Sample is enabled."));
// 				}
// 			}
// 		});
// 	}

// 	make_asset_issue_entry() {
// 		var doc = cur_frm.doc;
// 		var dialog = new frappe.ui.Dialog({
// 			title: __("For Issuing Asset"),
// 			fields: [
// 				{	"fieldtype": "Select",
// 					"label": __("Material Name"),
// 					"fieldname": "item_name",
// 					"options": doc.items.map(d => d.item_name),
// 					"reqd": 1 
// 				},
// 				{	"fieldtype": "Button", "label": __('Issue Asset'),
// 					"fieldname": "make_asset_issue_entry", "cssClass": "btn-primary"
// 				},
// 			]
// 		});
		
// 		dialog.fields_dict.make_asset_issue_entry.$input.click(function() {
// 			var args = dialog.get_values();

// 			frappe.call({
// 				method:'frappe.client.get_value',
// 				args:{
// 					'doctype':'Item',
// 					fieldname:"is_fixed_asset",
// 					filters: {
// 						"item_name": args.item_name,
// 						"is_fixed_asset":1
// 					}
// 				},
// 				callback:(r)=>{
// 					if(r.message){
// 						if ( !r.message.is_fixed_asset){
// 							frappe.msgprint('Item selected is not a fixed asset')
// 							dialog.hide();
// 							return;
// 						}
	
// 						if(!args) return;
// 						dialog.hide();
	
// 						let business_activity = ''
// 						let item_code = ''
// 						let asset_rate = ''
// 						cur_frm.doc.items.map(d => {
// 							if (d.item_name == args.item_name){
// 								business_activity = d.business_activity;
// 								item_code = d.item_code;
// 								asset_rate = d.valuation_rate;
// 							}
	
// 						})
	
// 						var new_doc = frappe.model.get_new_doc('Asset Issue Details');
// 						new_doc.branch = cur_frm.doc.branch;
// 						new_doc.business_activity = business_activity;
// 						new_doc.entry_date = new Date().toJSON().slice(0,10).replace(/-/g,'-');
// 						new_doc.item_code = item_code;
// 						new_doc.purchase_receipt = cur_frm.docname;
// 						new_doc.asset_rate = asset_rate
// 						new_doc.qty = 1;
// 						new_doc.amount = asset_rate * new_doc.qty
// 						frappe.set_route('Form', 'Asset Issue Details', new_doc.name);
// 					} else{
// 						frappe.msgprint('There no such item')
// 						dialog.hide();
// 						return;
// 					}
// 				}
// 			})
// 		});
// 		dialog.show()
// 	}

// 	apply_putaway_rule() {
// 		if (this.frm.doc.apply_putaway_rule) erpnext.apply_putaway_rule(this.frm);
// 	}


// };

// // for backward compatibility: combine new and previous states
// extend_cscript(cur_frm.cscript, new erpnext.stock.PurchaseReceiptController({frm: cur_frm}));

// cur_frm.cscript.update_status = function(status) {
// 	frappe.ui.form.is_saving = true;
// 	frappe.call({
// 		method:"erpnext.stock.doctype.purchase_receipt.purchase_receipt.update_purchase_receipt_status",
// 		args: {docname: cur_frm.doc.name, status: status},
// 		callback: function(r){
// 			if(!r.exc)
// 				cur_frm.reload_doc();
// 		},
// 		always: function(){
// 			frappe.ui.form.is_saving = false;
// 		}
// 	})
// }

// cur_frm.fields_dict['items'].grid.get_field('project').get_query = function(doc, cdt, cdn) {
// 	return {
// 		filters: [
// 			['Project', 'status', 'not in', 'Completed, Cancelled']
// 		]
// 	}
// }

// cur_frm.fields_dict['select_print_heading'].get_query = function(doc, cdt, cdn) {
// 	return {
// 		filters: [
// 			['Print Heading', 'docstatus', '!=', '2']
// 		]
// 	}
// }

// cur_frm.fields_dict['items'].grid.get_field('bom').get_query = function(doc, cdt, cdn) {
// 	var d = locals[cdt][cdn]
// 	return {
// 		filters: [
// 			['BOM', 'item', '=', d.item_code],
// 			['BOM', 'is_active', '=', '1'],
// 			['BOM', 'docstatus', '=', '1']
// 		]
// 	}
// }

// frappe.provide("erpnext.buying");

// frappe.ui.form.on("Purchase Receipt", "is_subcontracted", function(frm) {
// 	if (frm.doc.is_old_subcontracting_flow) {
// 		erpnext.buying.get_default_bom(frm);
// 	}

// 	frm.toggle_reqd("supplier_warehouse", frm.doc.is_old_subcontracting_flow);
// });

// frappe.ui.form.on('Purchase Receipt Item', {
// 	item_code: function(frm, cdt, cdn) {
// 		var d = locals[cdt][cdn];
// 		frappe.db.get_value('Item', {name: d.item_code}, 'sample_quantity', (r) => {
// 			frappe.model.set_value(cdt, cdn, "sample_quantity", r.sample_quantity);
// 			validate_sample_quantity(frm, cdt, cdn);
// 		});
// 	},
// 	qty: function(frm, cdt, cdn) {
// 		validate_sample_quantity(frm, cdt, cdn);
// 	},
// 	sample_quantity: function(frm, cdt, cdn) {
// 		validate_sample_quantity(frm, cdt, cdn);
// 	},
// 	batch_no: function(frm, cdt, cdn) {
// 		validate_sample_quantity(frm, cdt, cdn);
// 	},
// });

// cur_frm.cscript['Make Stock Entry'] = function() {
// 	frappe.model.open_mapped_doc({
// 		method: "erpnext.stock.doctype.purchase_receipt.purchase_receipt.make_stock_entry",
// 		frm: cur_frm,
// 	})
// }

// var validate_sample_quantity = function(frm, cdt, cdn) {
// 	var d = locals[cdt][cdn];
// 	if (d.sample_quantity && d.qty) {
// 		frappe.call({
// 			method: 'erpnext.stock.doctype.stock_entry.stock_entry.validate_sample_quantity',
// 			args: {
// 				batch_no: d.batch_no,
// 				item_code: d.item_code,
// 				sample_quantity: d.sample_quantity,
// 				qty: d.qty
// 			},
// 			callback: (r) => {
// 				frappe.model.set_value(cdt, cdn, "sample_quantity", r.message);
// 			}
// 		});
// 	}
// };