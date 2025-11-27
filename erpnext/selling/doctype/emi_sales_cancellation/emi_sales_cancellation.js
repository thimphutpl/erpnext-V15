// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('EMI Sales Cancellation', {
	onload: function(frm) {
		if(!frm.doc.requested_by){
			frm.set_value("requested_by", frm.doc.owner);
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee", 
					fieldname:"region",
					filters: {
						"user_id": frm.doc.owner
					}
				},
				callback: function(r) {
					// console.log(r.message);
					if(r.message.region) {
						cur_frm.set_value("region", r.message.region)
					}
				}
			});
			frm.refresh_fields();
		}
		if(frappe.session.user != frm.doc.owner){
			frm.set_df_property("reason", "read_only", 1);
			frm.refresh_field("reason");
		}
		else{
			frm.set_df_property("reason", "read_only", 0);
			frm.refresh_field("reason");		
		}
	},
	refresh: function(frm){
		frm.set_query('btl_sales', function (doc) {
			return {
				filters: {
					"docstatus": 1,
					"owner": frm.doc.owner
				}
			};
		});
		frappe.call({
			method: "check_employee",
			doc: frm.doc
		})
	},
});

cur_frm.fields_dict['items'].grid.get_field('btl_sales').get_query = function(frm, cdt, cdn) {
	return {
		filters: {
			"docstatus": 1,
			"owner": cur_frm.doc.owner
		}
	}
}