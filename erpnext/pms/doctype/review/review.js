// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Review', {
	refresh: function(frm){
		if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Create Evaluation'), ()=>{
				frappe.model.open_mapped_doc({
					method: "erpnext.pms.doctype.review.review.create_evaluation",	
					frm: cur_frm
				});
			}).addClass("btn-primary custom-create custom-create-css")
		}
		
		if (frm.doc.approver == frappe.session.user){
			frappe.meta.get_docfield("Review Target Item", "appraisees_remarks", cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
			frappe.meta.get_docfield("Review Competency Item", "appraisees_remarks", cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
			frappe.meta.get_docfield("Additional Achievements", "appraisees_remarks", cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
		}	
	},
	
	get_target: function(frm){
		get_target(frm);
	},
	
	eas_calendar: function(frm) {
		cur_frm.refresh_fields()
	}
})

var add_btn = function(frm){
	if (frm.doc.docstatus == 1){
		frm.add_custom_button(__('Create Evaluation'), ()=>{
			frappe.model.open_mapped_doc({
				method: "erpnext.pms.doctype.review.review.create_evaluation",	
				frm: cur_frm
			});
		}).addClass("btn-primary custom-create custom-create-css")
	}
}

var get_competency = (frm) => {
	if (frm.doc.eas_calendar) {
		frappe.call({
			method: "get_competency",
			doc: frm.doc,
			callback: (r) => {
				cur_frm.refresh_field("review_competency_item")
			}
		})
	}else{
		frappe.throw("Select EAS Calendar to get <b>Competency</b>")
	}
}

var get_target = function(frm){
	//get traget from py file
	if (frm.doc.required_to_set_target && frm.doc.eas_calendar) {
		frappe.call({
			method: 'get_target',
			doc: frm.doc,
			callback: (r) =>{
				frm.refresh_field("review_target_item")
			}
		})
	}else{
		frappe.throw("Select EAS Calendar to get <b>Target</b>")
	}
}

frappe.ui.form.on('Review Target Item',{
	form_render:function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
		frappe.meta.get_docfield("Review Target Item", "appraisees_remarks", cur_frm.doc.name).read_only = frm.doc.docstatus
		// frm.refresh_field('items')
	},
})

var make_child_table_field_editable = (frm) => {
    // frm.fields_dict["review_target_item"].grid.get_field("appraisees_remarks").df.read_only =
    //     frappe.session.user !== "Administrator"; // Editable for Administrator
    // frm.fields_dict["review_competency_item"].grid.get_field("appraisees_remark").df.read_only =
    //     frappe.session.user !== frm.doc.approver; // Editable for the approver

    // // Refresh the fields to apply the changes
    // frm.refresh_field("review_target_item");
    // frm.refresh_field("review_competency_item");
	frappe.meta.get_docfield("Review Target Item","appraisees_remarks",cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver,
	frappe.meta.get_docfield("Review Competency Item","appraisees_remark",cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
};



frappe.form.link_formatters['Employee'] = function(value, doc) {
	return value
}