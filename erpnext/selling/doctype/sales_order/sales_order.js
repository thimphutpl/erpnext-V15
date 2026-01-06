// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.cscript.tax_table = "Sales Taxes and Charges";
erpnext.accounts.taxes.setup_tax_filters("Sales Taxes and Charges");
erpnext.accounts.taxes.setup_tax_validations("Sales Order");
erpnext.sales_common.setup_selling_controller();

frappe.ui.form.on("Sales Order", {
	setup: function (frm) {
		frm.custom_make_buttons = {
			"Delivery Note": "Delivery Note",
			"Pick List": "Pick List",
			"Sales Invoice": "Sales Invoice",
			"Material Request": "Material Request",
			"Purchase Order": "Purchase Order",
			Project: "Project",
			"Payment Entry": "Payment",
			"Work Order": "Work Order",
		};
		frm.add_fetch("customer", "tax_id", "tax_id");

		// formatter for material request item
		frm.set_indicator_formatter("item_code", function (doc) {
			let color;
			if (!doc.qty && frm.doc.has_unit_price_items) {
				color = "yellow";
			} else if (doc.stock_qty <= doc.delivered_qty) {
				color = "green";
			} else {
				color = "orange";
			}

			return color;
		});

		frm.set_query("bom_no", "items", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					item: row.item_code,
				},
			};
		});

		frm.set_df_property("packed_items", "cannot_add_rows", true);
		frm.set_df_property("packed_items", "cannot_delete_rows", true);
	},

	refresh: function (frm) {
		if (frm.doc.docstatus === 1) {
			if (
				frm.doc.status !== "Closed" &&
				flt(frm.doc.per_delivered) < 100 &&
				flt(frm.doc.per_billed) < 100 &&
				frm.has_perm("write")
			) {
				frm.add_custom_button(__("Update Items"), () => {
					erpnext.utils.update_child_items({
						frm: frm,
						child_docname: "items",
						child_doctype: "Sales Order Detail",
						cannot_add_row: false,
						has_reserved_stock: frm.doc.__onload && frm.doc.__onload.has_reserved_stock,
					});
				});

				// Stock Reservation > Reserve button should only be visible if the SO has unreserved stock and no Pick List is created against the SO.
				if (
					frm.doc.__onload &&
					frm.doc.__onload.has_unreserved_stock &&
					flt(frm.doc.per_picked) === 0
				) {
					frm.add_custom_button(
						__("Reserve"),
						() => frm.events.create_stock_reservation_entries(frm),
						__("Stock Reservation")
					);
				}
			}

			// Stock Reservation > Unreserve button will be only visible if the SO has un-delivered reserved stock.
			if (
				frm.doc.__onload &&
				frm.doc.__onload.has_reserved_stock &&
				frappe.model.can_cancel("Stock Reservation Entry")
			) {
				frm.add_custom_button(
					__("Unreserve"),
					() => frm.events.cancel_stock_reservation_entries(frm),
					__("Stock Reservation")
				);
			}

			frm.doc.items.forEach((item) => {
				if (flt(item.stock_reserved_qty) > 0 && frappe.model.can_read("Stock Reservation Entry")) {
					frm.add_custom_button(
						__("Reserved Stock"),
						() => frm.events.show_reserved_stock(frm),
						__("Stock Reservation")
					);
					return;
				}
			});
		}

		if (frm.doc.docstatus === 0) {
			erpnext.set_unit_price_items_note(frm);

			if (frm.doc.is_internal_customer) {
				frm.events.get_items_from_internal_purchase_order(frm);
			}

			if (frm.doc.docstatus === 0) {
				frappe.call({
					method: "erpnext.selling.doctype.sales_order.sales_order.get_stock_reservation_status",
					callback: function (r) {
						if (!r.message) {
							frm.set_value("reserve_stock", 0);
							frm.set_df_property("reserve_stock", "read_only", 1);
							frm.set_df_property("reserve_stock", "hidden", 1);
							frm.fields_dict.items.grid.update_docfield_property("reserve_stock", "hidden", 1);
							frm.fields_dict.items.grid.update_docfield_property(
								"reserve_stock",
								"default",
								0
							);
							frm.fields_dict.items.grid.update_docfield_property(
								"reserve_stock",
								"read_only",
								1
							);
						}
					},
				});
			}
		}

		// Hide `Reserve Stock` field description in submitted or cancelled Sales Order.
		if (frm.doc.docstatus > 0) {
			frm.set_df_property("reserve_stock", "description", null);
		}
	},

	get_items_from_internal_purchase_order(frm) {
		if (!frappe.model.can_read("Purchase Order")) {
			return;
		}

		frm.add_custom_button(
			__("Purchase Order"),
			() => {
				erpnext.utils.map_current_doc({
					method: "erpnext.buying.doctype.purchase_order.purchase_order.make_inter_company_sales_order",
					source_doctype: "Purchase Order",
					target: frm,
					setters: [
						{
							label: __("Supplier"),
							fieldname: "supplier",
							fieldtype: "Link",
							options: "Supplier",
						},
					],
					get_query_filters: {
						company: frm.doc.company,
						is_internal_supplier: 1,
						docstatus: 1,
						status: ["!=", "Completed"],
					},
				});
			},
			__("Get Items From")
		);
	},

	onload: function (frm) {
		if (!frm.doc.transaction_date) {
			frm.set_value("transaction_date", frappe.datetime.get_today());
		}
		erpnext.queries.setup_queries(frm, "Warehouse", function () {
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", 0],
				],
			};
		});

		frm.set_query("warehouse", "items", function (doc, cdt, cdn) {
			let row = locals[cdt][cdn];
			let query = {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse", "is_group", "=", 0],
				],
			};
			if (row.item_code) {
				query.query = "erpnext.controllers.queries.warehouse_query";
				query.filters.push(["Bin", "item_code", "=", row.item_code]);
			}
			return query;
		});

		// On cancel and amending a sales order with advance payment, reset advance paid amount
		if (frm.is_new()) {
			frm.set_value("advance_paid", 0);
		}

		frm.ignore_doctypes_on_cancel_all = [
			"Purchase Order",
			"Unreconcile Payment",
			"Unreconcile Payment Entries",
		];
	},

	delivery_date: function (frm) {
		$.each(frm.doc.items || [], function (i, d) {
			if (!d.delivery_date) d.delivery_date = frm.doc.delivery_date;
		});
		refresh_field("items");
	},

	create_stock_reservation_entries(frm) {
		const dialog = new frappe.ui.Dialog({
			title: __("Stock Reservation"),
			size: "extra-large",
			fields: [
				{
					fieldname: "set_warehouse",
					fieldtype: "Link",
					label: __("Set Warehouse"),
					options: "Warehouse",
					default: frm.doc.set_warehouse,
					get_query: () => {
						return {
							filters: [["Warehouse", "is_group", "!=", 1]],
						};
					},
					onchange: () => {
						if (dialog.get_value("set_warehouse")) {
							dialog.fields_dict.items.df.data.forEach((row) => {
								row.warehouse = dialog.get_value("set_warehouse");
							});
							dialog.fields_dict.items.grid.refresh();
						}
					},
				},
				{ fieldtype: "Column Break" },
				{
					fieldname: "add_item",
					fieldtype: "Link",
					label: __("Add Item"),
					options: "Sales Order Item",
					get_query: () => {
						return {
							query: "erpnext.controllers.queries.get_filtered_child_rows",
							filters: {
								parenttype: frm.doc.doctype,
								parent: frm.doc.name,
								reserve_stock: 1,
							},
						};
					},
					onchange: () => {
						let sales_order_item = dialog.get_value("add_item");

						if (sales_order_item) {
							frm.doc.items.forEach((item) => {
								if (item.name === sales_order_item) {
									let unreserved_qty =
										(flt(item.stock_qty) -
											(item.stock_reserved_qty
												? flt(item.stock_reserved_qty)
												: flt(item.delivered_qty) * flt(item.conversion_factor))) /
										flt(item.conversion_factor);

									if (unreserved_qty > 0) {
										dialog.fields_dict.items.df.data.forEach((row) => {
											if (row.sales_order_item === sales_order_item) {
												unreserved_qty -= row.qty_to_reserve;
											}
										});
									}

									dialog.fields_dict.items.df.data.push({
										sales_order_item: item.name,
										item_code: item.item_code,
										warehouse: dialog.get_value("set_warehouse") || item.warehouse,
										qty_to_reserve: Math.max(unreserved_qty, 0),
									});
									dialog.fields_dict.items.grid.refresh();
									dialog.set_value("add_item", undefined);
								}
							});
						}
					},
				},
				{ fieldtype: "Section Break" },
				{
					fieldname: "items",
					fieldtype: "Table",
					label: __("Items to Reserve"),
					allow_bulk_edit: false,
					cannot_add_rows: true,
					cannot_delete_rows: true,
					data: [],
					fields: [
						{
							fieldname: "sales_order_item",
							fieldtype: "Link",
							label: __("Sales Order Item"),
							options: "Sales Order Item",
							reqd: 1,
							in_list_view: 1,
							get_query: () => {
								return {
									query: "erpnext.controllers.queries.get_filtered_child_rows",
									filters: {
										parenttype: frm.doc.doctype,
										parent: frm.doc.name,
										reserve_stock: 1,
									},
								};
							},
							onchange: (event) => {
								if (event) {
									let name = $(event.currentTarget).closest(".grid-row").attr("data-name");
									let item_row =
										dialog.fields_dict.items.grid.grid_rows_by_docname[name].doc;

									frm.doc.items.forEach((item) => {
										if (item.name === item_row.sales_order_item) {
											item_row.item_code = item.item_code;
										}
									});
									dialog.fields_dict.items.grid.refresh();
								}
							},
						},
						{
							fieldname: "item_code",
							fieldtype: "Link",
							label: __("Item Code"),
							options: "Item",
							reqd: 1,
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldname: "warehouse",
							fieldtype: "Link",
							label: __("Warehouse"),
							options: "Warehouse",
							reqd: 1,
							in_list_view: 1,
							get_query: () => {
								return {
									filters: [["Warehouse", "is_group", "!=", 1]],
								};
							},
						},
						{
							fieldname: "qty_to_reserve",
							fieldtype: "Float",
							label: __("Qty"),
							reqd: 1,
							in_list_view: 1,
						},
					],
				},
			],
			primary_action_label: __("Reserve Stock"),
			primary_action: () => {
				var data = { items: dialog.fields_dict.items.grid.get_selected_children() };

				if (data.items && data.items.length > 0) {
					frappe.call({
						doc: frm.doc,
						method: "create_stock_reservation_entries",
						args: {
							items_details: data.items,
							notify: true,
						},
						freeze: true,
						freeze_message: __("Reserving Stock..."),
						callback: (r) => {
							frm.doc.__onload.has_unreserved_stock = false;
							frm.reload_doc();
						},
					});

					dialog.hide();
				} else {
					frappe.msgprint(__("Please select items to reserve."));
				}
			},
		});

		frm.doc.items.forEach((item) => {
			if (item.reserve_stock) {
				let unreserved_qty =
					(flt(item.stock_qty) -
						(item.stock_reserved_qty
							? flt(item.stock_reserved_qty)
							: flt(item.delivered_qty) * flt(item.conversion_factor))) /
					flt(item.conversion_factor);

				if (unreserved_qty > 0) {
					dialog.fields_dict.items.df.data.push({
						__checked: 1,
						sales_order_item: item.name,
						item_code: item.item_code,
						warehouse: item.warehouse,
						qty_to_reserve: unreserved_qty,
					});
				}
			}
		});

		dialog.fields_dict.items.grid.refresh();
		dialog.show();
	},

	cancel_stock_reservation_entries(frm) {
		const dialog = new frappe.ui.Dialog({
			title: __("Stock Unreservation"),
			size: "extra-large",
			fields: [
				{
					fieldname: "sr_entries",
					fieldtype: "Table",
					label: __("Reserved Stock"),
					allow_bulk_edit: false,
					cannot_add_rows: true,
					cannot_delete_rows: true,
					in_place_edit: true,
					data: [],
					fields: [
						{
							fieldname: "sre",
							fieldtype: "Link",
							label: __("Stock Reservation Entry"),
							options: "Stock Reservation Entry",
							reqd: 1,
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldname: "item_code",
							fieldtype: "Link",
							label: __("Item Code"),
							options: "Item",
							reqd: 1,
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldname: "warehouse",
							fieldtype: "Link",
							label: __("Warehouse"),
							options: "Warehouse",
							reqd: 1,
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldname: "qty",
							fieldtype: "Float",
							label: __("Qty"),
							reqd: 1,
							read_only: 1,
							in_list_view: 1,
						},
					],
				},
			],
			primary_action_label: __("Unreserve Stock"),
			primary_action: () => {
				var data = { sr_entries: dialog.fields_dict.sr_entries.grid.get_selected_children() };

				if (data.sr_entries && data.sr_entries.length > 0) {
					frappe.call({
						doc: frm.doc,
						method: "cancel_stock_reservation_entries",
						args: {
							sre_list: data.sr_entries.map((item) => item.sre),
						},
						freeze: true,
						freeze_message: __("Unreserving Stock..."),
						callback: (r) => {
							frm.doc.__onload.has_reserved_stock = false;
							frm.reload_doc();
						},
					});

					dialog.hide();
				} else {
					frappe.msgprint(__("Please select items to unreserve."));
				}
			},
		});

		frappe
			.call({
				method: "erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry.get_stock_reservation_entries_for_voucher",
				args: {
					voucher_type: frm.doctype,
					voucher_no: frm.docname,
				},
				callback: (r) => {
					if (!r.exc && r.message) {
						r.message.forEach((sre) => {
							if (flt(sre.reserved_qty) > flt(sre.delivered_qty)) {
								dialog.fields_dict.sr_entries.df.data.push({
									sre: sre.name,
									item_code: sre.item_code,
									warehouse: sre.warehouse,
									qty: flt(sre.reserved_qty) - flt(sre.delivered_qty),
								});
							}
						});
					}
				},
			})
			.then((r) => {
				dialog.fields_dict.sr_entries.grid.refresh();
				dialog.show();
			});
	},

	show_reserved_stock(frm) {
		// Get the latest modified date from the items table.
		var to_date = moment(new Date(Math.max(...frm.doc.items.map((e) => new Date(e.modified))))).format(
			"YYYY-MM-DD"
		);

		frappe.route_options = {
			company: frm.doc.company,
			from_date: frm.doc.transaction_date,
			to_date: to_date,
			voucher_type: frm.doc.doctype,
			voucher_no: frm.doc.name,
		};
		frappe.set_route("query-report", "Reserved Stock");
	},
	"discount_or_cost_amount": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},
	"is_credit": function(frm){
		frm.toggle_reqd("supply_order_ref",frm.doc.is_credit==1);
	},
	"transportation_charges": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"additional_cost": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
        },

	"challan_cost": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"loading_rate": function(frm) {
		var total_qty = 0;
		for (var i in cur_frm.doc.items) {
			var item = cur_frm.doc.items[i];
		        total_qty += item.qty;		
			}
		cur_frm.set_value("loading_cost", flt(total_qty) * flt(frm.doc.loading_rate));
	},

	"loading_cost": function(frm) {
		cur_frm.set_value("discount_amount", flt(frm.doc.discount_or_cost_amount) - flt(frm.doc.transportation_charges) - flt(frm.doc.additional_cost) - flt(frm.doc.loading_cost)-flt(frm.doc.challan_cost))
		cur_frm.refresh_field("discount_amount")
	},

	"transportation_rate": function(frm) {
		cur_frm.set_value("transportation_charges", flt(frm.doc.transportation_rate) * flt(frm.doc.total_distance) * flt(frm.doc.total_quantity))
		cur_frm.trigger("transportation_charges")
		cur_frm.refresh_field("transportation_charges")
	},

	"total_distance": function(frm) {
		cur_frm.set_value("transportation_charges", flt(frm.doc.transportation_rate) * flt(frm.doc.total_distance) * flt(frm.doc.total_quantity))
		cur_frm.trigger("transportation_charges")
		cur_frm.refresh_field("transportation_charges")
	},

	"total_quantity": function(frm) {
		cur_frm.set_value("transportation_charges", flt(frm.doc.transportation_rate) * flt(frm.doc.total_distance) * flt(frm.doc.total_quantity))
		cur_frm.trigger("transportation_charges")
		cur_frm.refresh_field("transportation_charges")
	},
});

// frappe.ui.form.on("Sales Order Item", {
// 	item_code: function (frm, cdt, cdn) {
// 		var row = locals[cdt][cdn];
// 		if (frm.doc.delivery_date) {
// 			row.delivery_date = frm.doc.delivery_date;
// 			refresh_field("delivery_date", cdn, "items");
// 		} else {
// 			frm.script_manager.copy_from_first_row("items", row, ["delivery_date"]);
// 		}
// 	},
// 	delivery_date: function (frm, cdt, cdn) {
// 		if (!frm.doc.delivery_date) {
// 			erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "items", "delivery_date");
// 		}
// 	},
// });

cur_frm.fields_dict['items'].grid.get_field('price_template').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if(d.sales_uom){
		uom = d.sales_uom
	}else{
		uom = ''
	}
	return {
			query: "erpnext.controllers.queries.price_template_list",
			filters: {'item_code': d.item_code, 'transaction_date': frm.transaction_date, 'branch': frm.branch, 'location': frm.location, 'selling_uom': uom}
	}
}

//auto list the price_templates based on branch, transaction_date, item_code, customer written by Thukten on 12 Dec, 2021
cur_frm.fields_dict['items'].grid.get_field('customer_price_list').get_query = function(frm, cdt, cdn) {
var d = locals[cdt][cdn];
return {
		query: "erpnext.controllers.queries.customer_price_template_list",
		filters: {'item_code': d.item_code, 'transaction_date': frm.transaction_date, 'branch': frm.branch, 'location': frm.location, 'customer': frm.customer}
}
}


frappe.ui.form.on("Sales Order Item", {
	qty: function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		if(frm.doc.naming_series == "Timber Products" && !frm.doc.is_kidu_sale) { 
			if(item.lot_number){
				get_balance(frm, cdt, cdn);
			} 
			if(item.conversion_req){
				frappe.model.set_value(cdt, cdn, "stock_qty", '')
				cur_frm.refresh_field("stock_qty")
			}
		}

		if(item.item_code && item.stock_uom){
			if(item.stock_uom != item.sales_uom && (typeof item.sales_uom != "undefined" && item.sales_uom != '')){
				frappe.model.set_value(cdt, cdn, "stock_qty", item.conversion_factor * item.qty)
				cur_frm.refresh_field("stock_qty")
			}
			else{
				frappe.model.set_value(cdt, cdn, "stock_qty", item.qty)
				cur_frm.refresh_field("stock_qty")
			}
		}
	},	

	sales_uom: function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "price_template", "") 

		var item = locals[cdt][cdn];
		
		if(item.item_code && item.sales_uom) {
			frappe.call({
				method: "erpnext.stock.get_item_details.get_conversion_factor",
				args: {
					item_code: item.item_code,
					uom: item.sales_uom
				},
				callback: function(r) {
					if(r.message.conversion_factor){
						frappe.model.set_value(cdt, cdn, "conversion_factor", r.message.conversion_factor)
						frappe.model.set_value(cdt, cdn, "stock_qty", r.message.conversion_factor * item.qty)
						cur_frm.refresh_field("conversion_factor")
						cur_frm.refresh_field("stock_qty")
					}
				}
			});
		}
	},

	conversion_req: function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "sales_uom", "") 
		frappe.model.set_value(cdt, cdn, "price_template", "")
		
		var row = locals[cdt][cdn]
		frm.fields_dict.items.grid.toggle_reqd("sales_uom", row.conversion_req?1:0)
		frm.refresh_field('sales_uom')

		if(frm.doc.naming_series == "Timber Products"){
			frm.fields_dict.items.grid.toggle_reqd("stock_qty", 1)
			frm.fields_dict.items.grid.toggle_enable("stock_qty", 1)
			frm.refresh_field('stock_qty')
		}

	},
	
	form_render: (frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		frm.fields_dict.items.grid.toggle_reqd("sales_uom", row.conversion_req?1:0)
		frm.refresh_field('sales_uom')
		if(frm.doc.naming_series == "Timber Products"){
			frm.fields_dict.items.grid.toggle_reqd("stock_qty", 1)
			frm.refresh_field('stock_qty')
		}
	},
	
	stock_qty: function(frm, cdt, cdn) {
		if(frm.doc.naming_series == "Timber Products"){
			var row = locals[cdt][cdn]
			if(row.qty != 0){
				frappe.model.set_value(cdt, cdn, "conversion_factor", row.stock_qty / row.qty)
				cur_frm.refresh_field("conversion_factor")
			}
		}
	},

	price_template: function(frm, cdt, cdn) {
		d = locals[cdt][cdn]
		if(cur_frm.doc.location){
			loc = cur_frm.doc.location;
		}else{
			loc = ''
		}

		if(d.sales_uom){
			uom = d.sales_uom
		}else{
			uom = ''
		}

		frappe.call({
			method: "erpnext.production.doctype.selling_price.selling_price.get_selling_rate",
			args: {
					"price_list": d.price_template,
					"branch": cur_frm.doc.branch,
					"item_code": d.item_code,
					"transaction_date": cur_frm.doc.transaction_date,
					"selling_uom": uom,
					"location": loc
				},
			callback: function(r) {
					frappe.model.set_value(cdt, cdn, "price_list_rate", r.message)
					frappe.model.set_value(cdt, cdn, "rate", r.message)
					cur_frm.refresh_field("price_list_rate")
					cur_frm.refresh_field("rate")
			}
		})
    },

	customer_price_list: function(frm, cdt, cdn) {
		d = locals[cdt][cdn]
		if(cur_frm.doc.location){
			loc = cur_frm.doc.location;
		}else{
			loc = "NA";
		}
		frappe.call({
			method: "erpnext.production.doctype.customer_selling_price.customer_selling_price.get_customer_selling_rate",
			args: {
				"price_list": d.customer_price_list,
				"branch": cur_frm.doc.branch,
				"item_code": d.item_code,
				"transaction_date": cur_frm.doc.transaction_date,
				"location": loc,
				"customer": cur_frm.doc.customer
			},
			callback: function(r) {
				frappe.model.set_value(cdt, cdn, "price_list_rate", r.message);
				frappe.model.set_value(cdt, cdn, "rate", r.message);
				cur_frm.refresh_field("price_list_rate");
				cur_frm.refresh_field("rate");
			}
		})
	},

	item_code: function(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "price_template", "") 
	},

	lot_number: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.item_code && d.lot_number) { get_balance(frm, cdt, cdn); }
	},

	sp_type: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.sp_type == "General Rate"){

		}else{

		}
	}
	
});

erpnext.selling.SalesOrderController = class SalesOrderController extends erpnext.selling.SellingController {
	onload(doc, dt, dn) {
		super.onload(doc, dt, dn);
	}

	refresh(doc, dt, dn) {
		var me = this;
		super.refresh();
		let allow_delivery = false;

		if (doc.docstatus == 1) {
			if (this.frm.has_perm("submit")) {
				if (doc.status === "On Hold") {
					// un-hold
					this.frm.add_custom_button(
						__("Resume"),
						function () {
							me.frm.cscript.update_status("Resume", "Draft");
						},
						__("Status")
					);

					if (flt(doc.per_delivered) < 100 || flt(doc.per_billed) < 100) {
						// close
						this.frm.add_custom_button(__("Close"), () => this.close_sales_order(), __("Status"));
					}
				} else if (doc.status === "Closed") {
					// un-close
					this.frm.add_custom_button(
						__("Re-open"),
						function () {
							me.frm.cscript.update_status("Re-open", "Draft");
						},
						__("Status")
					);
				}
			}
			if (doc.status !== "Closed") {
				if (doc.status !== "On Hold") {
					const items_are_deliverable = this.frm.doc.items.some(
						(item) => item.delivered_by_supplier === 0 && item.qty > flt(item.delivered_qty)
					);
					allow_delivery =
						(this.frm.doc.has_unit_price_items || items_are_deliverable) &&
						!this.frm.doc.skip_delivery_note;

					if (this.frm.has_perm("submit")) {
						if (flt(doc.per_delivered) < 100 || flt(doc.per_billed) < 100) {
							// hold
							this.frm.add_custom_button(
								__("Hold"),
								() => this.hold_sales_order(),
								__("Status")
							);
							// close
							this.frm.add_custom_button(
								__("Close"),
								() => this.close_sales_order(),
								__("Status")
							);
						}
					}

					if (
						(!doc.__onload || !doc.__onload.has_reserved_stock) &&
						flt(doc.per_picked) < 100 &&
						flt(doc.per_delivered) < 100 &&
						frappe.model.can_create("Pick List")
					) {
						this.frm.add_custom_button(
							__("Pick List"),
							() => this.create_pick_list(),
							__("Create")
						);
					}

					const order_is_a_sale = ["Sales", "Shopping Cart"].indexOf(doc.order_type) !== -1;
					const order_is_maintenance = ["Maintenance"].indexOf(doc.order_type) !== -1;
					// order type has been customised then show all the action buttons
					const order_is_a_custom_sale =
						["Sales", "Shopping Cart", "Maintenance"].indexOf(doc.order_type) === -1;

					// delivery note
					if (
						flt(doc.per_delivered) < 100 &&
						(order_is_a_sale || order_is_a_custom_sale) &&
						allow_delivery
					) {
						if (frappe.model.can_create("Delivery Note")) {
							this.frm.add_custom_button(
								__("Delivery Note"),
								() => this.make_delivery_note_based_on_delivery_date(true),
								__("Create")
							);
						}

						if (frappe.model.can_create("Work Order")) {
							this.frm.add_custom_button(
								__("Work Order"),
								() => this.make_work_order(),
								__("Create")
							);
						}
					}

					// sales invoice
					if (flt(doc.per_billed) < 100 && frappe.model.can_create("Sales Invoice")) {
						this.frm.add_custom_button(
							__("Sales Invoice"),
							() => me.make_sales_invoice(),
							__("Create")
						);
					}

					// material request
					if (
						(!doc.order_type ||
							((order_is_a_sale || order_is_a_custom_sale) && flt(doc.per_delivered) < 100)) &&
						frappe.model.can_create("Material Request")
					) {
						this.frm.add_custom_button(
							__("Material Request"),
							() => this.make_material_request(),
							__("Create")
						);
						this.frm.add_custom_button(
							__("Request for Raw Materials"),
							() => this.make_raw_material_request(),
							__("Create")
						);
					}

					// Make Purchase Order
					if (!this.frm.doc.is_internal_customer && frappe.model.can_create("Purchase Order")) {
						this.frm.add_custom_button(
							__("Purchase Order"),
							() => this.make_purchase_order(),
							__("Create")
						);
					}

					// maintenance
					if (flt(doc.per_delivered) < 100 && (order_is_maintenance || order_is_a_custom_sale)) {
						if (frappe.model.can_create("Maintenance Visit")) {
							this.frm.add_custom_button(
								__("Maintenance Visit"),
								() => this.make_maintenance_visit(),
								__("Create")
							);
						}
						if (frappe.model.can_create("Maintenance Schedule")) {
							this.frm.add_custom_button(
								__("Maintenance Schedule"),
								() => this.make_maintenance_schedule(),
								__("Create")
							);
						}
					}

					// project
					if (flt(doc.per_delivered) < 100 && frappe.model.can_create("Project")) {
						this.frm.add_custom_button(__("Project"), () => this.make_project(), __("Create"));
					}

					if (
						doc.docstatus === 1 &&
						!doc.inter_company_order_reference &&
						frappe.model.can_create("Purchase Order")
					) {
						let me = this;
						let internal = me.frm.doc.is_internal_customer;
						if (internal) {
							let button_label =
								me.frm.doc.company === me.frm.doc.represents_company
									? "Internal Purchase Order"
									: "Inter Company Purchase Order";

							me.frm.add_custom_button(
								button_label,
								function () {
									me.make_inter_company_order();
								},
								__("Create")
							);
						}
					}
				}
				// payment request
				if (flt(doc.per_billed) < 100 + frappe.boot.sysdefaults.over_billing_allowance) {
					this.frm.add_custom_button(
						__("Payment Request"),
						() => this.make_payment_request(),
						__("Create")
					);

					if (frappe.model.can_create("Payment Entry")) {
						this.frm.add_custom_button(
							__("Payment"),
							() => this.make_payment_entry(),
							__("Create")
						);
					}
				}
				this.frm.page.set_inner_btn_group_as_primary(__("Create"));
			}
		}

		if (this.frm.doc.docstatus === 0 && frappe.model.can_read("Quotation")) {
			this.frm.add_custom_button(
				__("Quotation"),
				function () {
					let d = erpnext.utils.map_current_doc({
						method: "erpnext.selling.doctype.quotation.quotation.make_sales_order",
						source_doctype: "Quotation",
						target: me.frm,
						setters: [
							{
								label: __("Customer"),
								fieldname: "party_name",
								fieldtype: "Link",
								options: "Customer",
								default: me.frm.doc.customer || undefined,
							},
						],
						get_query_filters: {
							company: me.frm.doc.company,
							docstatus: 1,
							status: ["!=", "Lost"],
						},
					});

					setTimeout(() => {
						d.$parent.append(`
							<span class='small text-muted'>
								${__("Note: Please create Sales Orders from individual Quotations to select from among Alternative Items.")}
							</span>
					`);
					}, 200);
				},
				__("Get Items From")
			);
		}
		
		if (this.frm.doc.docstatus === 0 && frappe.model.can_read("Product Requisition")) {
			let company = this.frm.doc.company;
			this.frm.add_custom_button(
				__("Product Requisition"),
				function () {
					let d = erpnext.utils.map_current_doc({
						method: "erpnext.selling.doctype.product_requisition.product_requisition.make_sales_order",
						source_doctype: "Product Requisition",
						target: me.frm,
						setters: [
							{
								label: __("Product Requisition"),
								fieldname: "product_requisition",
								fieldtype: "Link",
								options: "Product Requisition",
							},
						],
						get_query_filters: {
							docstatus: 1,
							company: company
						}
					});

					setTimeout(() => {
						d.$parent.append(`
							<span class='small text-muted'>
								${__("Note: Please create Sales Orders to select from among Alternative Items.")}
							</span>
					`);
					}, 200);
				},
				__("Get Items From")
			);
		}

		if (this.frm.doc.docstatus === 0 && frappe.model.can_read("Lot List")) {
			this.frm.add_custom_button(
				__("Lot List"),
				function () {
					custom_map_current_doc({
						method: "erpnext.production.doctype.lot_list.lot_list.make_sales_order",
						source_doctype: "Lot List",
						target: me.frm,
						setters: [
							{
								label: __("Lot List"),
								fieldname: "lot_list",
								fieldtype: "Link",
								options: "Lot List",
							},
						],
						get_query_filters: {
							query: "erpnext.production.doctype.lot_list.lot_list.get_lot_list",
							filters: {branch:cur_frm.doc.branch}
						}
					});
				},
				__("Get Items From")
			);
		}

		this.order_type(doc);
	}

	create_pick_list() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.create_pick_list",
			frm: this.frm,
		});
	}

	make_work_order() {
		var me = this;
		me.frm.call({
			method: "erpnext.selling.doctype.sales_order.sales_order.get_work_order_items",
			args: {
				sales_order: this.frm.docname,
			},
			freeze: true,
			callback: function (r) {
				if (!r.message) {
					frappe.msgprint({
						title: __("Work Order not created"),
						message: __("No Items with Bill of Materials to Manufacture"),
						indicator: "orange",
					});
					return;
				} else {
					const fields = [
						{
							label: __("Items"),
							fieldtype: "Table",
							fieldname: "items",
							description: __("Select BOM and Qty for Production"),
							fields: [
								{
									fieldtype: "Read Only",
									fieldname: "item_code",
									label: __("Item Code"),
									in_list_view: 1,
								},
								{
									fieldtype: "Link",
									fieldname: "bom",
									options: "BOM",
									reqd: 1,
									label: __("Select BOM"),
									in_list_view: 1,
									get_query: function (doc) {
										return { filters: { item: doc.item_code } };
									},
								},
								{
									fieldtype: "Float",
									fieldname: "pending_qty",
									reqd: 1,
									label: __("Qty"),
									in_list_view: 1,
								},
								{
									fieldtype: "Data",
									fieldname: "sales_order_item",
									reqd: 1,
									label: __("Sales Order Item"),
									hidden: 1,
								},
							],
							data: r.message,
							get_data: () => {
								return r.message;
							},
						},
					];
					var d = new frappe.ui.Dialog({
						title: __("Select Items to Manufacture"),
						fields: fields,
						primary_action: function () {
							var data = { items: d.fields_dict.items.grid.get_selected_children() };
							if (!data.items.length) {
								frappe.throw(__("Please select atleast one item to continue"));
							}
							me.frm.call({
								method: "make_work_orders",
								args: {
									items: data,
									company: me.frm.doc.company,
									sales_order: me.frm.docname,
									project: me.frm.project,
								},
								freeze: true,
								callback: function (r) {
									if (r.message) {
										frappe.msgprint({
											message: __("Work Orders Created: {0}", [
												r.message
													.map(function (d) {
														return repl(
															'<a href="/app/work-order/%(name)s">%(name)s</a>',
															{ name: d }
														);
													})
													.join(", "),
											]),
											indicator: "green",
										});
									}
									d.hide();
								},
							});
						},
						primary_action_label: __("Create"),
					});
					d.show();
				}
			},
		});
	}

	order_type() {
		this.toggle_delivery_date();
	}

	tc_name() {
		this.get_terms();
	}

	make_material_request() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_material_request",
			frm: this.frm,
		});
	}

	skip_delivery_note() {
		this.toggle_delivery_date();
	}

	toggle_delivery_date() {
		this.frm.fields_dict.items.grid.toggle_reqd(
			"delivery_date",
			this.frm.doc.order_type == "Sales" && !this.frm.doc.skip_delivery_note
		);
	}

	make_raw_material_request() {
		var me = this;
		this.frm.call({
			method: "erpnext.selling.doctype.sales_order.sales_order.get_work_order_items",
			args: {
				sales_order: this.frm.docname,
				for_raw_material_request: 1,
			},
			callback: function (r) {
				if (!r.message) {
					frappe.msgprint({
						message: __("No Items with Bill of Materials."),
						indicator: "orange",
					});
					return;
				} else {
					me.make_raw_material_request_dialog(r);
				}
			},
		});
	}

	make_raw_material_request_dialog(r) {
		var me = this;
		var fields = [
			{ fieldtype: "Check", fieldname: "include_exploded_items", label: __("Include Exploded Items") },
			{
				fieldtype: "Check",
				fieldname: "ignore_existing_ordered_qty",
				label: __("Ignore Existing Ordered Qty"),
			},
			{
				fieldtype: "Table",
				fieldname: "items",
				description: __("Select BOM, Qty and For Warehouse"),
				fields: [
					{
						fieldtype: "Read Only",
						fieldname: "item_code",
						label: __("Item Code"),
						in_list_view: 1,
					},
					{
						fieldtype: "Link",
						fieldname: "warehouse",
						options: "Warehouse",
						label: __("For Warehouse"),
						in_list_view: 1,
					},
					{
						fieldtype: "Link",
						fieldname: "bom",
						options: "BOM",
						reqd: 1,
						label: __("BOM"),
						in_list_view: 1,
						get_query: function (doc) {
							return { filters: { item: doc.item_code } };
						},
					},
					{
						fieldtype: "Float",
						fieldname: "required_qty",
						reqd: 1,
						label: __("Qty"),
						in_list_view: 1,
					},
				],
				data: r.message,
				get_data: function () {
					return r.message;
				},
			},
		];
		var d = new frappe.ui.Dialog({
			title: __("Items for Raw Material Request"),
			fields: fields,
			primary_action: function () {
				var data = d.get_values();
				me.frm.call({
					method: "erpnext.selling.doctype.sales_order.sales_order.make_raw_material_request",
					args: {
						items: data,
						company: me.frm.doc.company,
						sales_order: me.frm.docname,
						project: me.frm.doc.project,
					},
					freeze: true,
					callback: function (r) {
						if (r.message) {
							frappe.msgprint(
								__("Material Request {0} submitted.", [
									'<a href="/app/material-request/' +
										r.message.name +
										'">' +
										r.message.name +
										"</a>",
								])
							);
						}
						d.hide();
						me.frm.reload_doc();
					},
				});
			},
			primary_action_label: __("Create"),
		});
		d.show();
	}

	async make_delivery_note_based_on_delivery_date(for_reserved_stock = false) {
		var me = this;
		let all_submitted = await frappe.call({
			method: "erpnext.selling.doctype.sales_order.sales_order.get_payment_entries_for_sales_order",
			args: { sales_order: this.frm.doc.name }
		}).then(r => {
			if (r.message && r.message.length > 0) {
				return r.message.every(ref => ref.docstatus === 1);
			}
			return false;
		});

		if ((this.frm.doc.is_credit === 0 && this.frm.doc.is_export === 0) && !all_submitted) {
			frappe.msgprint(__("Cannot make Delivery Note without making Payment"));
			return false; 
		}
		var delivery_dates = this.frm.doc.items.map((i) => i.delivery_date);
		delivery_dates = [...new Set(delivery_dates)];

		var item_grid = this.frm.fields_dict["items"].grid;
		if (!item_grid.get_selected().length && delivery_dates.length > 1) {
			var dialog = new frappe.ui.Dialog({
				title: __("Select Items based on Delivery Date"),
				fields: [{ fieldtype: "HTML", fieldname: "dates_html" }],
			});

			var html = $(`
				<div style="border: 1px solid #d1d8dd">
					<div class="list-item list-item--head">
						<div class="list-item__content list-item__content--flex-2">
							${__("Delivery Date")}
						</div>
					</div>
					${delivery_dates
						.map(
							(date) => `
						<div class="list-item">
							<div class="list-item__content list-item__content--flex-2">
								<label>
								<input type="checkbox" data-date="${date}" checked="checked"/>
								${frappe.datetime.str_to_user(date)}
								</label>
							</div>
						</div>
					`
						)
						.join("")}
				</div>
			`);

			var wrapper = dialog.fields_dict.dates_html.$wrapper;
			wrapper.html(html);

			dialog.set_primary_action(__("Select"), function () {
				var dates = wrapper
					.find("input[type=checkbox]:checked")
					.map((i, el) => $(el).attr("data-date"))
					.toArray();

				if (!dates) return;

				me.make_delivery_note(dates, for_reserved_stock);
				dialog.hide();
			});
			dialog.show();
		} else {
			this.make_delivery_note([], for_reserved_stock);
		}
	}

	make_delivery_note(delivery_dates, for_reserved_stock = false) {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_delivery_note",
			frm: this.frm,
			args: {
				delivery_dates,
				for_reserved_stock: for_reserved_stock,
			},
			freeze: true,
			freeze_message: __("Creating Delivery Note ..."),
		});
	}

	make_sales_invoice() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice",
			frm: this.frm,
		});
	}

	make_maintenance_schedule() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_maintenance_schedule",
			frm: this.frm,
		});
	}

	make_project() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_project",
			frm: this.frm,
		});
	}

	make_inter_company_order() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_inter_company_purchase_order",
			frm: this.frm,
		});
	}

	make_maintenance_visit() {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.sales_order.sales_order.make_maintenance_visit",
			frm: this.frm,
		});
	}

	make_purchase_order() {
		let pending_items = this.frm.doc.items.some((item) => {
			let pending_qty = flt(item.stock_qty) - flt(item.ordered_qty);
			return pending_qty > 0;
		});
		if (!pending_items) {
			frappe.throw({
				message: __("Purchase Order already created for all Sales Order items"),
				title: __("Note"),
			});
		}

		var me = this;
		var dialog = new frappe.ui.Dialog({
			title: __("Select Items"),
			size: "large",
			fields: [
				{
					fieldtype: "Check",
					label: __("Against Default Supplier"),
					fieldname: "against_default_supplier",
					default: 0,
				},
				{
					fieldname: "items_for_po",
					fieldtype: "Table",
					label: __("Select Items"),
					fields: [
						{
							fieldtype: "Data",
							fieldname: "item_code",
							label: __("Item"),
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldtype: "Data",
							fieldname: "item_name",
							label: __("Item name"),
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldtype: "Float",
							fieldname: "pending_qty",
							label: __("Pending Qty"),
							read_only: 1,
							in_list_view: 1,
						},
						{
							fieldtype: "Link",
							read_only: 1,
							fieldname: "uom",
							label: __("UOM"),
							in_list_view: 1,
						},
						{
							fieldtype: "Data",
							fieldname: "supplier",
							label: __("Supplier"),
							read_only: 1,
							in_list_view: 1,
						},
					],
				},
			],
			primary_action_label: __("Create Purchase Order"),
			primary_action(args) {
				if (!args) return;

				let selected_items = dialog.fields_dict.items_for_po.grid.get_selected_children();
				if (selected_items.length == 0) {
					frappe.throw({
						message: "Please select Items from the Table",
						title: __("Items Required"),
						indicator: "blue",
					});
				}

				dialog.hide();

				var method = args.against_default_supplier
					? "make_purchase_order_for_default_supplier"
					: "make_purchase_order";
				return frappe.call({
					method: "erpnext.selling.doctype.sales_order.sales_order." + method,
					freeze_message: __("Creating Purchase Order ..."),
					args: {
						source_name: me.frm.doc.name,
						selected_items: selected_items,
					},
					freeze: true,
					callback: function (r) {
						if (!r.exc) {
							if (!args.against_default_supplier) {
								frappe.model.sync(r.message);
								frappe.set_route("Form", r.message.doctype, r.message.name);
							} else {
								frappe.route_options = {
									sales_order: me.frm.doc.name,
								};
								frappe.set_route("List", "Purchase Order");
							}
						}
					},
				});
			},
		});

		dialog.fields_dict["against_default_supplier"].df.onchange = () => set_po_items_data(dialog);

		function set_po_items_data(dialog) {
			var against_default_supplier = dialog.get_value("against_default_supplier");
			var items_for_po = dialog.get_value("items_for_po");

			if (against_default_supplier) {
				let items_with_supplier = items_for_po.filter((item) => item.supplier);

				dialog.fields_dict["items_for_po"].df.data = items_with_supplier;
				dialog.get_field("items_for_po").refresh();
			} else {
				let po_items = [];
				me.frm.doc.items.forEach((d) => {
					let ordered_qty = me.get_ordered_qty(d, me.frm.doc);
					let pending_qty = (flt(d.stock_qty) - ordered_qty) / flt(d.conversion_factor);
					if (pending_qty > 0) {
						po_items.push({
							doctype: "Sales Order Item",
							name: d.name,
							item_name: d.item_name,
							item_code: d.item_code,
							pending_qty: pending_qty,
							uom: d.uom,
							supplier: d.supplier,
						});
					}
				});

				dialog.fields_dict["items_for_po"].df.data = po_items;
				dialog.get_field("items_for_po").refresh();
			}
		}

		set_po_items_data(dialog);
		dialog.get_field("items_for_po").grid.only_sortable();
		dialog.get_field("items_for_po").refresh();
		dialog.wrapper.find(".grid-heading-row .grid-row-check").click();
		dialog.show();
	}

	get_ordered_qty(item, so) {
		let ordered_qty = item.ordered_qty;
		if (so.packed_items && so.packed_items.length) {
			// calculate ordered qty based on packed items in case of product bundle
			let packed_items = so.packed_items.filter((pi) => pi.parent_detail_docname == item.name);
			if (packed_items && packed_items.length) {
				ordered_qty = packed_items.reduce((sum, pi) => sum + flt(pi.ordered_qty), 0);
				ordered_qty = ordered_qty / packed_items.length;
			}
		}
		return ordered_qty;
	}

	hold_sales_order() {
		var me = this;
		var d = new frappe.ui.Dialog({
			title: __("Reason for Hold"),
			fields: [
				{
					fieldname: "reason_for_hold",
					fieldtype: "Text",
					reqd: 1,
				},
			],
			primary_action: function () {
				var data = d.get_values();
				frappe.call({
					method: "frappe.desk.form.utils.add_comment",
					args: {
						reference_doctype: me.frm.doctype,
						reference_name: me.frm.docname,
						content: __("Reason for hold:") + " " + data.reason_for_hold,
						comment_email: frappe.session.user,
						comment_by: frappe.session.user_fullname,
					},
					callback: function (r) {
						if (!r.exc) {
							me.update_status("Hold", "On Hold");
							d.hide();
						}
					},
				});
			},
		});
		d.show();
	}
	close_sales_order() {
		this.frm.cscript.update_status("Close", "Closed");
	}
	update_status(label, status) {
		var doc = this.frm.doc;
		var me = this;
		frappe.ui.form.is_saving = true;
		frappe.call({
			method: "erpnext.selling.doctype.sales_order.sales_order.update_status",
			args: { status: status, name: doc.name },
			callback: function (r) {
				me.frm.reload_doc();
			},
			always: function () {
				frappe.ui.form.is_saving = false;
			},
		});
	}
};


function get_balance(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	frappe.call({
		method: "erpnext.selling.doctype.sales_order.sales_order.get_lot_detail",
		args: {
			"branch": cur_frm.doc.branch,
			"item_code": d.item_code,
			"lot_number": d.lot_number,
			"total_pieces": d.total_pieces
		},
		callback: function(r) {
			if(r.message){
			var balance = r.message[0]['total_volume'];
			var lot_check = r.message[0]['lot_check'];
				if(lot_check)
				{
					if(balance < 0){
						frappe.msgprint("No available volume under the selected Lot");
					}
					else{
						frappe.model.set_value(cdt, cdn, "qty", balance);
					}
				}
			}
			else{
				frappe.msgprint("Invalid Lot Number. Please verify the lot number with Material and Branch");
			}
		}
	});
}



var custom_map_current_doc = function(opts) {
	if(opts.get_query_filters) {
		opts.get_query = function() {
			//return {filters: opts.get_query_filters};
			return opts.get_query_filters;
		}
	}
	var _map = function() {
		// remove first item row if empty
		if($.isArray(cur_frm.doc.items) && cur_frm.doc.items.length > 0) {
			if(!cur_frm.doc.items[0].item_code) {
				cur_frm.doc.items = cur_frm.doc.items.splice(1);
			}
		}

		return frappe.call({
			// Sometimes we hit the limit for URL length of a GET request
			// as we send the full target_doc. Hence this is a POST request.
			type: "POST",
			method: opts.method,
			args: {
				"source_name": opts.source_name,
				"target_doc": cur_frm.doc
			},
			callback: function(r) {
				if(!r.exc) {
					var doc = frappe.model.sync(r.message);
					cur_frm.refresh();
				}
			}
		});
	}
	if(opts.source_doctype) {
		var d = new frappe.ui.Dialog({
			title: __("Get From ") + __(opts.source_doctype),
			fields: [
				{
					fieldtype: "Link",
					label: __(opts.source_doctype),
					fieldname: opts.source_doctype,
					options: opts.source_doctype,
					get_query: opts.get_query,
					reqd:1
				},
			]
		});
		d.set_primary_action(__('Get Items'), function() {
			var values = d.get_values();
			if(!values)
				return;
			opts.source_name = values[opts.source_doctype];
			d.hide();
			_map();
		})
		d.show();
	} else if(opts.source_name) {
		_map();
	}
}

extend_cscript(cur_frm.cscript, new erpnext.selling.SalesOrderController({ frm: cur_frm }));
