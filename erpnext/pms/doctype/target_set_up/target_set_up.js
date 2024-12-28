// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// developed by Birendra on 01/02/2021
frappe.ui.form.on('Target Set Up', {
	onload: (frm) => {
		frm.set_query("eas_calendar", function(){
			return {
				filters: {
					'docstatus': 1
				}
			}
		})
	},

	eas_calendar: (frm)=>{
		get_competency(frm)
	},

	refresh: (frm)=>{
		add_btn(frm)
		hr_add_btn(frm)

		if (frm.doc.docstatus == 0 && frappe.user.has_role(['HR Manager', 'HR User'])){
			frm.set_df_property('set_manual_approver', 'read_only', 0);
		}else{
			frm.set_df_property('set_manual_approver', 'read_only', 1);
		}
	},

	set_manual_approver:function(frm){
		if (flt(frm.doc.set_manual_approver) == 1){
			frm.set_df_property('approver', 'read_only', 0);
		}
		else{
			frm.set_df_property('approver', 'read_only', 1);
		}
	},
});

cur_frm.cscript.approver = function(doc){
	frappe.call({
		"method": "set_approver_designation",
		"doc": doc,
		"args":{
			"approver": doc.approver
		},
		callback: function(r){
			if(r){
				console.log(r.message)
				cur_frm.set_value("approver_designation",r.message);
				cur_frm.refresh_field("approver_designation")

			}
		}
	})
};

frappe.ui.form.on('Performance Target Evaluation',{
	weightage:(frm)=>{
		frappe.call({
			method: 'calculate_total_weightage',
			doc: frm.doc,
			callback: ()=> {
				frm.refresh_field('total_weightage');
			}
		})
	},
	
})

var add_btn = (frm)=>{
	if ( frm.doc.docstatus == 1 ){
		frm.add_custom_button(__('Create Review'), ()=>{
			frappe.model.open_mapped_doc({
				method: "erpnext.pms.doctype.target_set_up.target_set_up.create_review",	
				frm: cur_frm
			});
		}).addClass("btn-primary custom-create custom-create-css");
	}
}

var hr_add_btn = (frm)=>{
	if (frm.doc.workflow_state == "Waiting Approval" && frappe.user.has_role(['HR Manager', 'HR User'])){
		frm.add_custom_button(__('Manual Approval'), ()=>{
			frappe.call({
				method: "erpnext.pms.doctype.target_set_up.target_set_up.manual_approval_for_hr",
				frm: cur_frm,
				
				args: {
					name: frm.doc.name,
					employee: frm.doc.employee,
					eas_calendar: frm.doc.eas_calendar,
				},	
				callback:function(){
					cur_frm.reload_doc()
				}
			});
		}).addClass("btn-primary");
	}
}

var get_competency=(frm)=>{
	if (frm.doc.designation) {
		return frappe.call({
			method: 'get_competency',
			doc: frm.doc,
			callback: ()=> {
				frm.refresh_field('competency');
				frm.refresh_fields()
			}
		})
	} else {
		frappe.msgprint('Your Designation is not defined under Employee Category')
	}
}