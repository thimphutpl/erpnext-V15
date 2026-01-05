// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Asset Disposal", {
	// onload: function (frm) {
	// 	// frm.set_query("asset", "item", (doc) => {
	// 	// 	alert
	// 	// 	return {
	// 	// 		filters: {
	// 	// 			asset_category:doc.asset_category,
	// 	// 			status: ["not in", ["Draft","Sold","Scrapped","Submitted","Cancelled"]],
	// 	// 			// status: ["in", ["Fully Depreciated"]],
	// 	// 		}
	// 	// 	}
	// 	// })
	// 	if (frm.fields_dict['item']) {
	// 		frm.fields_dict['item'].grid.get_field('asset').get_query = function (doc, cdt, cdn) {
	// 			return {
	// 				query: "erpnext.assets.doctype.bulk_asset_disposal.bulk_asset_disposal.get_filtered_assets",
	// 				filters: {
	// 					asset_category: doc.asset_category,
	// 					branch: doc.branch
	// 				}
	// 			};
	// 		};
	// 	}
	// },

	refresh(frm) {
		if ((frm.doc.docstatus == 1 && frm.doc.scrap == "Sale Asset") && frm.doc.sales_invoice == null) {
			cur_frm.add_custom_button(__("Make Sales Invoice"),
				function () {
					frm.events.make_sales_invoice(frm);
				}
			).addClass("btn-primary custom-create custom-create-css")
		}

		frm.set_query("asset", "item", function (doc, cdt, cdn) {
			var filters = {
				"asset_category": doc.asset_category,
				"docstatus": 1
			};

			// Strict branch matching - only show assets from selected branch
			if (doc.branch) {
				filters["branch"] = doc.branch;
			}

			return {
				filters: filters
			};
		});
	},

	// scrap: function (frm) {
	// 	// frm.doc.scrap_date = Date.now(); #comment by Jai, 20 July 2022
	// 	// frm.refresh_fields()
	// 	frm.set_df_property('customer', 'reqd', frm.doc.scrap == 'Sale Asset' ? 1 : 0)
	// 	frm.toggle_display('customer', frm.doc.scrap == 'Sale Asset' && frm.doc.to_employee == 1 ? 1 : 0)
	// },
	// to_employee: function (frm) {
	// 	if(frm.doc.scrap == "Sale Asset"){
	// 		if (frm.doc.to_employee) {
	// 			// Checkbox is checked → hide customer
	// 			frm.set_df_property("customer", "hidden", 1);
	// 			frm.set_df_property("employee", "reqd", 1)
	
	// 		} else {
	// 			// Checkbox is unchecked → show customer
	// 			frm.set_df_property("customer", "hidden", 0);
	// 			frm.set_df_property("customer", "reqd", 1)
	// 		}
	// 	}
	// 	else{
	// 		// if (frm.doc.to_employee) {
	// 			// Checkbox is checked → hide customer
	// 		frm.set_df_property("customer", "hidden", 1);
	// 		frm.set_df_property("employee", "reqd", 0)
	// 		// } else {
	// 		// Checkbox is unchecked → show customer
	// 		frm.set_df_property("customer", "hidden", 1);
	// 		frm.set_df_property("customer", "reqd", 0)
	// 		// }
	// 	}
	// },
	branch: function (frm) {
		// Clear items when branch changes
		frm.clear_table("item");
		frm.refresh_field("item");
	},

	asset_category: function (frm) {
		// Clear items when category changes
		frm.clear_table("item");
		frm.refresh_field("item");
	},

	// Optional: also run on form load to set initial visibility
	// onload: function(frm) {
	//     if (frm.doc.to_employee) {
	//         frm.set_df_property("customer", "hidden", 1);
	//     } else {
	//         frm.set_df_property("customer", "hidden", 0);
	//     }
	// },
	onload: function (frm) {
		// Run same logic on form load to set initial visibility
		frm.trigger('to_employee');
	},

	make_sales_invoice: function (frm) {
		frappe.call({
			method: "erpnext.assets.doctype.bulk_asset_disposal.bulk_asset_disposal.sale_asset",
			args: {
				branch: frm.doc.branch,
				// business_activity: frm.doc.business_activity,
				name: frm.doc.name,
				scrap_date: frm.doc.scrap_date,
				customer: frm.doc.customer,
				employee: frm.doc.employee,
				posting_date: frm.doc.scrap_date
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
			}
		});
	},

	on_submit: function (frm) {
		console.log("on_submit")
		if (frm.doc.scrap == 'Scrap Asset') {
			frappe.set_route("List", "Journal Entry");
		}
	}
});

// frappe.ui.form.on('Bulk Asset Disposal Item', {
// 	// asset:function(frm,cdt,cdn){

// 	// }
// 	item_code:function(frm,cdt,cdn){
// 		var item = locals[cdt][cdn]
// 		frappe.call({
// 			method: "frappe.client.get_value",
// 			args: {
// 				doctype: "Item",
// 				fieldname: ["item_name", "stock_uom"],
// 				filters: {
// 					name: item.item_code
// 				}
// 			},
// 			callback: function(r) {
// 				frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name)
// 				frappe.model.set_value(cdt, cdn, "uom", r.message.stock_uom)
// 				cur_frm.refresh_field("item_name")
// 				cur_frm.refresh_field("uom")
// 			}
// 		})
// 	}
// })

// frappe.ui.form.on("Bulk Asset Disposal Item", {
// 	asset: function (frm, cdt, cdn) {
// 		var row = locals[cdt][cdn];
// 		if (!row.asset) return;

// 		// Copy parent fields to child row for display
// 		frappe.model.set_value(cdt, cdn, "scrap_date", frm.doc.scrap_date);
// 		frappe.model.set_value(cdt, cdn, "asset_category", frm.doc.asset_category);
// 		frappe.model.set_value(cdt, cdn, "branch", frm.doc.branch);

// 		// Get asset details
// 		frappe.call({
// 			method: "erpnext.assets.doctype.bulk_asset_disposal.bulk_asset_disposal.get_asset_details",
// 			args: { asset_name: row.asset },
// 			callback: function (r) {
// 				if (r.message) {
// 					frappe.throw(message)
// 					frappe.model.set_value(cdt, cdn, "item_code", r.message.item_code);
// 					frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
// 					frappe.model.set_value(cdt, cdn, "uom", r.message.uom);
// 				}
// 			}
// 		});
// 	}
// });

frappe.ui.form.on("Bulk Asset Disposal Item", {
	asset: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (!row.asset) return;

		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Asset",
				name: row.asset
			},
			callback: function (r) {
				if (r.message) {
					var asset = r.message;

					// STRICT VALIDATION
					var errors = [];

					if (asset.asset_category !== frm.doc.asset_category) {
						errors.push(__("Category: Asset belongs to {0}, but you selected {1}",
							[asset.asset_category, frm.doc.asset_category]));
					}

					if (frm.doc.branch && asset.branch !== frm.doc.branch) {
						errors.push(__("Branch: Asset belongs to {0}, but you selected {1}",
							[asset.branch, frm.doc.branch]));
					}



					if (errors.length > 0) {
						var error_msg = __("Cannot add asset {0}:<br>", [row.asset]) + errors.join("<br>");
						frappe.throw(error_msg);
						frappe.model.set_value(cdt, cdn, "asset", "");
						return;
					}

					// Set values if all validations pass
					frappe.model.set_value(cdt, cdn, "item_code", asset.item_code);
					frappe.model.set_value(cdt, cdn, "item_name", asset.item_name);
					frappe.model.set_value(cdt, cdn, "uom", asset.uom || "Nos");
				}
			}
		});
	}
});
frappe.form.link_formatters['Item'] = function (value, doc) {
	return value
}