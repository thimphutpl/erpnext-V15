// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Life Extension", {
	refresh(frm) {

	},
  asset(frm){
      if(frm.doc.asset){
          frappe.call({
              method: "frappe.client.get",
              args: {
                doctype: "Asset",
                name: frm.doc.asset
              },
              callback(r) {
                let rows = r.message.finance_books; // child table fieldname
                let value = rows?.[0]?.value_after_depreciation;
                let total_number_of_depreciations = rows?.[0]?.total_number_of_depreciations;
                frm.set_value("current_asset_value", value);
                frm.set_value("old_remaining_dep", flt(value/(r.message.gross_purchase_amount/total_number_of_depreciations)))
                frm.refresh_field("current_asset_value");
              }
            });
      }
  },
  additional_life: function(frm){
    if(frm.doc.additional_life){
      frm.set_value("new_remaining_dep", frm.doc.old_remaining_dep+frm.doc.additional_life);
	  frm.refresh_field("new_remaining_dep");
    }
  }
});
