// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("item_code","stock_uom","uom");
cur_frm.add_fetch("item_code","item_name","item_name");
frappe.ui.form.on('Asset Issue Details', {
	onload: function(frm){
		frm.set_query('item_code', function(doc, cdt, cdn) {
			return {
				filters: {
					"is_fixed_asset": '1'
				}
			}
		});
	},
	refresh: function (frm) {
		frm.set_query('issued_to', function(doc, cdt, cdn) {
			return {
				filters: {
					"branch": frm.doc.branch,
					"status":"Active"
				}
			}
		});
		frm.set_query("purchase_receipt",function(doc) {
			return {
				query: "erpnext.buying.doctype.asset_issue_details.asset_issue_details.check_item_code",
				filters: {
					'item_code': frm.doc.item_code,
					'branch': frm.doc.branch
				}
			}
		});
	},
	"qty": function (frm) {
		if (frm.doc.asset_rate) {
			frm.set_value("amount", frm.doc.qty * frm.doc.asset_rate);
		}
	},
	"asset_rate": function (frm) {
		if (frm.doc.qty) {
			frm.set_value("amount", frm.doc.qty * frm.doc.asset_rate);
		}
	},
	"purchase_receipt": function(frm){
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				parent: "Purchase Receipt",
				doctype: "Purchase Receipt Item",
				// fieldname: ["valuation_rate","rate","warehouse"],
				fieldname: ["base_net_rate", "base_rate", "warehouse"],
				filters: {
					"parent": frm.doc.purchase_receipt,
					"item_code": frm.doc.item_code
				}
			},
			callback: function(r){
				// if(r.message.valuation_rate){
				// 	cur_frm.set_value("asset_rate", r.message.valuation_rate)
				// }
				// else if(r.message.rate){
				// 	cur_frm.set_value("asset_rate", r.message.rate)
				// }
				// else{
				// 	frappe.throw("Not working")
				// }
				// cur_frm.set_value("warehouse",r.message.warehouse);
				if (r.message.base_net_rate) {
					cur_frm.set_value("asset_rate", r.message.base_net_rate);
				}
				else if (r.message.base_rate) {
					cur_frm.set_value("asset_rate", r.message.base_rate);
				}
				else {
					frappe.throw("Rate not found in Purchase Receipt Item");
				}
					cur_frm.set_value("warehouse",r.message.warehouse);

				}
			});

	},
	"asset_received_entries": function(frm){
		if(frm.doc.is_existing_asset == 1){
			frappe.call({
				method: "get_existing_details",
				doc: frm.doc,
				callback: function(m){
					if(m.message){
						frm.set_value("balance_qty", m.message[0]);
						frm.set_value("warehouse", m.message[1]);
						frm.set_value("asset_rate", m.message[2]);
						frm.refresh_fields();
					}
				}
			})
		}

	}
});


cur_frm.fields_dict['item_code'].get_query = function (doc) {
	return {
		"filters": {
			"item_group": "Fixed Assets"
		}
	}
}
