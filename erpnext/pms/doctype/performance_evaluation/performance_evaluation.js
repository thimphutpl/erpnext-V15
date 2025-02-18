// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Performance Evaluation', {
	setup: (frm) => {
		apply_filter(frm);
	},

	onload: function (frm) {
		let grid = frm.fields_dict['evaluate_target_item'].grid;
        grid.cannot_add_rows = true;

		let com = frm.fields_dict['evaluate_competency_item'].grid;
        com.cannot_add_rows = true;
	},
	
	refresh: (frm) => {
		if (frm.doc.docstatus === 1) {
			cur_frm.add_custom_button('Appeal', function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.pms.doctype.performance_evaluation.performance_evaluation.pms_appeal",	
					frm: cur_frm
				});
			});
		}
	},

	get_competency: function(frm) {
		if(frm.doc.docstatus != 1){
			get_competency(frm)
		}
	},
});

frappe.ui.form.on('Evaluate Competency', {
	form_render: (frm, cdt, cdn) => {
		var row = locals[cdt][cdn]
		if(row.parentfield=="evaluate_competency_item" && frappe.session.user!=frm.doc.approver){
			frm.fields_dict['evaluate_competency_item'].grid.grid_rows_by_docname[cdn].toggle_editable('achievement', false);

		}
	}
})

frappe.ui.form.on('Evaluate Target Item', {
	form_render: (frm, cdt, cdn) => {
		var row = locals[cdt][cdn]
		// if(frappe.session.user!=frm.doc.approver){
		// 	frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].docfields[16].read_only=1
		// 	frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].docfields[17].read_only=1
		// 	frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].docfields[20].read_only=1

		// }

		// if ( frm.doc.docstatus == 1){
		// 	if (frappe.user.has_role(['HR Manager', 'HR User'])){
		// 		frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].toggle_editable('reverse_formula', true);
		// 		// frappe.meta.get_docfield("Evaluate Target Item","reverse_formula",cur_frm.doc.name).read_only = 0
		// 	}else{
		// 		// frappe.meta.get_docfield("Evaluate Target Item","reverse_formula",cur_frm.doc.name).read_only = 1
		// 		frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].toggle_editable('reverse_formula', false);
		// 	}
		// }
		// frappe.call({
		// 	method: "check_employee_or_supervisor",
		// 	doc: frm.doc,
		// 	args: {"auditor": row.employee},
		// 	callback: function(r){
		// 		if(r.message[0] == 1){
		// 			frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].toggle_editable('employee_remarks', true);
		// 			frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].toggle_editable('supervisor_remarks', false);
		// 		}else if(r.message[1]==1){
		// 			frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].toggle_editable('supervisor_remarks', true);
		// 			frm.fields_dict['evaluate_target_item'].grid.grid_rows_by_docname[cdn].toggle_editable('employee_remarks', false);
		// 		}
		// 		frm.refresh_field("evaluate_target_item");
		// 	}
		// })
		
	},
})

var apply_filter = (frm) => {
	cur_frm.set_query('eas_calendar', function () {
		return {
			'filters': {
				'docstatus': 1
			}
		};
	});
}

function get_competency(frm) {
	frappe.call({
		method: "get_competency",
		doc: frm.doc,
		callback: (r) => {
			frm.refresh_fields()
		}
	})
}