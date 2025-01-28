// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Allocation", {
	setup: function(frm) {
		frm.get_docfield("items").allow_bulk_edit = 1;			
			
	},
	refresh: function(frm) {

	},
});
frappe.ui.form.on('Expense Allocation Item',{
	quantity: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn){
		calculate_amount(frm, cdt, cdn);
	},
	
	amount: function(frm){
		update_totals(frm);
	},
	"expense_type": function(frm, cdt, cdn){
		update_fetch_data(cdt, cdn)
	},
});
var calculate_amount = function(frm, cdt, cdn){
	var child  = locals[cdt][cdn];
	var amount = 0.0;
	
	amount = parseFloat(child.quantity || 0.0)*parseFloat(child.rate || 0.0);
	frappe.model.set_value(cdt, cdn, "amount", parseFloat(amount || 0.0));
}

var update_totals = function(frm){
	var det = frm.doc.items || [];
	var tot_amount= 0.0;
		
		
	for(var i=0; i<det.length; i++){
			tot_amount += parseFloat(det[i].amount || 0.0);
	}
	cur_frm.set_value("total_amount",tot_amount);
	
}

cur_frm.fields_dict['items'].grid.get_field('cost_center').get_query = function(frm, cdt, cdn) {
	return {
            "filters": {
                "is_disabled": 0,
                "is_group": 0
            }
        };
}
function update_fetch_data(cdt, cdn){
	var item = locals[cdt][cdn];
	frappe.call({
		method: "erpnext.accounts.doctype.expense_allocation.expense_allocation.update_fetch_data",
		args: {
			"expense_for": item.expense_for,
			"expense_type":item.expense_type

		},
		callback: function(r) {
			if(r.message) {
				console.log(r.message)
				frappe.model.set_value(cdt, cdn, "equipment_number", flt(r.message[0]))
				frappe.model.set_value(cdt, cdn, "id_card", flt(r.message[1]))
			}
		}
	})
}
