// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Audit Engagement Letter', {
	onload: function(frm){
		this.layout.primary_button = this.$wrapper.find(".btn-primary");
		console.log(cur_frm.primary_button.data-label)
		if(frm.doc.type){
			frappe.call({
				method: "get_message_template",
				doc:frm.doc,
				callback: function(r){
					frm.refresh_fields();
				}
			})
		}
	},
	refresh: function(frm){
		if(frappe.session.user != frm.doc.supervisor_email){
			frm.set_df_property('remarks','read_only',1)
		} else {
			frm.set_df_property('remarks','read_only',0)
		}
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__('Send Mail to CC'), () => {
				frappe.call({
					method: "notify_cc",
					doc: frm.doc,
					callback: function(r){
						// console.log(r.message)
					}
			})
			}, __('Action'));
			frm.add_custom_button(__('Send Mail to Supervisor'), () => {
				frappe.call({
					method: "notify_supervisor",
					doc: frm.doc,
					callback: function(r){
						// console.log(r.message)
					}
			})
			}, __('Action'));
			frm.add_custom_button(__('Send Mail to Auditors'), () => {
				frappe.call({
					method: "notify_auditors",
					doc: frm.doc,
					callback: function(r){
						// console.log(r.message)
					}
			})
			}, __('Action'));
		}
	},

	onload_post_render: function(frm) {	
		if(frm.doc.docstatus == 0){
			frm.toggle_display("get_audit_team",1);
		} else {
			frm.toggle_display("get_audit_team",0);
		}
	},
	type: (frm)=>{
		if(frm.doc.type){
			frappe.call({
				method: "get_message_template",
				doc:frm.doc,
				callback: function(r){
					frm.refresh_fields();
				}
			})
		}
	},
	get_audit_team: (frm)=>{
		if (frm.doc.prepare_audit_plan_no) {
			frappe.call({
				method: 'get_audit_team',
				doc: frm.doc,
				callback:  () =>{
					frm.refresh_field("audit_team");
				}
			})
		}else{
			frappe.throw("Required Reference No. to get <b>Audit Team</b>")
		}
	},
});
