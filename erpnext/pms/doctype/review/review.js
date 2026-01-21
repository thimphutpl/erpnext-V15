// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Review', {
	refresh: function (frm) {
		if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Create Evaluation'), () => {
				frappe.model.open_mapped_doc({
					method: "erpnext.pms.doctype.review.review.create_evaluation",
					frm: cur_frm
				});
			}).addClass("btn-primary custom-create custom-create-css")
		}
		//Approver can edit remarks
		// if (frm.doc.approver == frappe.session.user) {
		// 	frappe.meta.get_docfield("Review Target Item", "appraisees_remarks", cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
		// 	frappe.meta.get_docfield("Review Competency Item", "appraisees_remarks", cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
		// 	frappe.meta.get_docfield("Additional Achievements", "appraisees_remarks", cur_frm.doc.name).read_only = frappe.session.user == frm.doc.approver
		// }
		set_child_from_to_readonly(frm);
		set_appraisers_remarks_readonly(frm);

	},





	get_target: function (frm) {
		get_target(frm);
	},

	eas_calendar: function (frm) {
		cur_frm.refresh_fields()
	}
})

var add_btn = function (frm) {
	if (frm.doc.docstatus == 1) {
		frm.add_custom_button(__('Create Evaluation'), () => {
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
	} else {
		frappe.throw("Select EAS Calendar to get <b>Competency</b>")
	}
}

var get_target = function (frm) {
	//get traget from py file
	if (frm.doc.required_to_set_target && frm.doc.eas_calendar) {
		frappe.call({
			method: 'get_target',
			doc: frm.doc,
			callback: (r) => {
				frm.refresh_field("review_target_item")
			}
		})
	} else {
		frappe.throw("Select EAS Calendar to get <b>Target</b>")
	}
}



// ---------------------------------------------------
// NEW CODE: Enable from/to date only for NEW ROWS. Added by kinzang.n
// ---------------------------------------------------

// frappe.ui.form.on('Review Target Item', {

// 	// when row is added
// 	review_target_item_add: function (frm, cdt, cdn) {
// 		let row = locals[cdt][cdn];

// 		if (frm.doc.owner === frappe.session.user) {
// 			let grid_row = frm.fields_dict["review_target_item"].grid.get_row(cdn);

// 			grid_row.toggle_enable("from_date", true);
// 			grid_row.toggle_enable("to_date", true);
// 		}
// 	},

// 	// when row is rendered (refresh grid)
// 	review_target_item_form_render: function (frm, cdt, cdn) {
// 		set_row_readonly(frm, cdt, cdn);
// 	}
// });
frappe.ui.form.on("Review Target Item", {
	review_target_item_form_render: function (frm, cdt, cdn) {
		set_row_readonly(frm, cdt, cdn);
		set_appraisers_remarks_readonly(frm);
	},
	review_target_item_add: function (frm, cdt, cdn) {
		set_row_readonly(frm, cdt, cdn);
		set_appraisers_remarks_readonly(frm);
	},
	review_target_item_remove: function (frm, cdt, cdn) {
		set_child_from_to_readonly(frm);
	}
});

function set_appraisers_remarks_readonly(frm) {
	if (!frm.fields_dict.review_target_item) return;

	const is_approver = frm.doc.approver === frappe.session.user;
	const grid = frm.fields_dict.review_target_item.grid;

	grid.grid_rows.forEach(row => {
		grid.update_docfield_property(
			"appraisers_remarks",
			"read_only",
			!is_approver,
			row.doc
		);
		row.refresh();
	});
}



// ---------------------------------------------------
// Set readonly for existing rows
// ---------------------------------------------------

function set_child_from_to_readonly(frm) {
	//const is_approver = frm.doc.approver === frappe.session.user;

	if (!frm.fields_dict["review_target_item"]) return

	frm.fields_dict["review_target_item"].grid.grid_rows.forEach((row) => {
		//let doc = row.doc;
		set_row_readonly(frm, row.doc.doctype, row.doc.name);
	});

}

function set_row_readonly(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let grid = frm.fields_dict["review_target_item"].grid;

	// Approver can edit everything
	if (frm.doc.approver === frappe.session.user) {
		grid.update_docfield_property("from_date", "read_only", false, row);
		grid.update_docfield_property("to_date", "read_only", false, row);
		grid.update_docfield_property("appraisees_remarks", "read_only", true, row);
	}
	// Employee can edit ONLY NEW ROWS
	else if (frm.doc.owner === frappe.session.user && row.__islocal) {
		grid.update_docfield_property("from_date", "read_only", false, row);
		grid.update_docfield_property("to_date", "read_only", false, row);
		grid.update_docfield_property("appraisees_remarks", "read_only", false, row);
	}
	// Employee cannot edit existing rows
	else if (frm.doc.owner === frappe.session.user) {
		grid.update_docfield_property("from_date", "read_only", true, row);
		grid.update_docfield_property("to_date", "read_only", true, row);
		grid.update_docfield_property("appraisees_remarks", "read_only", false, row);
	}

	// All other users
	else {
		grid.update_docfield_property("appraisees_remarks", "read_only", true, row);
	}


	// Force refresh the row
	grid.get_row(cdn).refresh();
}


frappe.form.link_formatters['Employee'] = function (value, doc) {
	return value
}

//TILL HEREa