// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("POL Advance", {
    setup(frm){
        frm.set_query("equipment", function(){
            return {
                query: "erpnext.fleet_management.doctype.pol_advance.pol_advance.get_equipment_by_parent_cost_center",
                filters: {
                    cost_center: frm.doc.cost_center
                }
            };
        });

        frm.set_query("fuelbook", function(){
            return {
                filters: {
                    'equipment': frm.doc.equipment,
                    'disabled': 0,
                }
            }
        });
    },

	refresh(frm) {
        refresh_html(frm);
        if (frm.doc.docstatus == 1 && frm.doc.status == "Cancelled") {
		
			cur_frm.add_custom_button(__('Update Journal Entry'), function() {
				// frappe.route_options = {
				// 	voucher_no: frm.doc.name,
				// 	from_date: frm.doc.posting_date,
				// 	to_date: frm.doc.posting_date,
				// 	company: frm.doc.company,
				// 	group_by_voucher: false
				// };
				// frappe.set_route("query-report", "General Ledger");
			}, __("Update"));
		
		}
	},

    advance_amount: (frm) => {
		calculate_balance(frm);
	},
});

var calculate_balance=(frm)=>{
    if (frm.doc.advance_amount > 0 ){
        cur_frm.set_value("balance_amount", frm.doc.advance_amount)
        cur_frm.set_value("adjusted_amount", 0)
    }
}


var refresh_html = function(frm){
	var journal_entry_status = "";
	if(frm.doc.journal_entry_status){
		journal_entry_status = '<div style="font-style: italic; font-size: 0.8em; ">* '+frm.doc.journal_entry_status+'</div>';
	}
	
	if(frm.doc.journal_entry){
		$(cur_frm.fields_dict.journal_entry_html.wrapper).html('<label class="control-label" style="padding-right: 0px;">Journal Entry</label><br><b>'+'<a href="/desk/Form/Journal Entry/'+frm.doc.journal_entry+'">'+frm.doc.journal_entry+"</a> "+"</b>"+journal_entry_status);
	}	
}
