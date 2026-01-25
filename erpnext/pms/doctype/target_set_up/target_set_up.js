// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Target Set Up', {
	onload: (frm) => {
		frm.set_query("eas_calendar", function () {
			return {
				filters: {
					'docstatus': 1
				}
			}
		})
	},

	// refresh: function (frm) {
	// 	frm.set_query('employee', function () {
	// 		return {
	// 			filters: {
	// 				eas_group: 'Group I'
	// 			}
	// 		};
	// 	});
	// },
	refresh: function (frm) {

		// Employee filter
		// frm.set_query('employee', function () {
		// 	return {
		// 		filters: {
		// 			eas_group: 'Group I'
		// 		}
		// 	};
		// });

		if (frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Create Review'), () => {
				frappe.model.open_mapped_doc({
					method: "erpnext.pms.doctype.target_set_up.target_set_up.create_review",
					frm: frm // Use the parameter from the function
				});
			}).addClass("btn-primary custom-create custom-create-css");
		}
		// if (frm.doc.docstatus == 1){
		// 	frm.add_custom_button(__('Create Evaluation'), ()=>{
		// 		frappe.model.open_mapped_doc({
		// 			method: "erpnext.pms.doctype.target_set_up.target_set_up.create_evaluation",	
		// 			frm: cur_frm
		// 		});
		// 	}).addClass("btn-primary custom-create custom-create-css")
		// }


		// default: make close_target read-only and added by kinzang
		frm.set_df_property("close_target", "read_only", 1);

		// only editable when Approved
		if (frm.doc.workflow_state === "Approved" && frm.doc.docstatus == 1) {
			frm.set_df_property("close_target", "read_only", 0);
		}

	}
});

frappe.ui.form.on('Performance Target Evaluation', {
	weightage: (frm) => {
		frappe.call({
			method: 'calculate_total_weightage',
			doc: frm.doc,
			callback: () => {
				frm.refresh_field('total_weightage');
			}
		})
	},

})

// var add_btn = (frm)=>{
// 	if ( frm.doc.docstatus == 1 ){
// 		frm.add_custom_button(__('Create Review'), ()=>{
// 			frappe.model.open_mapped_doc({
// 				method: "erpnext.pms.doctype.target_set_up.target_set_up.create_review",	
// 				frm: cur_frm
// 			});
// 		}).addClass("btn-primary custom-create custom-create-css");
// 	}
// }