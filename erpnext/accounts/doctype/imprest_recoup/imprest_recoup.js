// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Imprest Recoup', {

	setup: function (frm) {
		// Set query for party (employee) field
		frm.set_query("party", erpnext.queries.employee);  // Changed to employee query

		// Set query for approver field
		frm.set_query("approver", function () {
			if (!frm.doc.party) {
				frappe.msgprint(__("Please select an employee first"));
				return;
			}

			return {
				query: "erpnext.accounts.doctype.imprest_recoup.imprest_recoup.get_approvers",
				filters: {
					party: frm.doc.party  // Changed from 'employee' to 'party' to match Python
				}
			};
		});
	},

	party: function (frm) {
		// Clear approver when employee changes
		frm.set_value("approver", null);

		// Fetch new approver if employee is selected
		if (frm.doc.party) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: "Employee",
					fieldname: "expense_approver",
					filters: { name: frm.doc.party }
				},
				callback: function (r) {
					if (r.message && r.message.expense_approver) {
						frm.set_value("approver", r.message.expense_approver);
					}
				}
			});
		}
	},

	onload: function (frm) {
		frm.set_query('expense_account', 'items', function () {
			return {
				"filters": {
					"account_type": "Expense Account"
				}
			};
		});

		frm.set_query('account', 'items', function () {
			return {
				filters: [
					["is_group", "=", 0],
					["root_type", "!=", "Asset"]
				]
			};
		});
	},
	refresh: function (frm) {
		frm.set_query("project", function () {
			return {
				"filters": {
					"branch": frm.doc.branch
				}
			}
		});
	},

	"get_imprest_advance": function (frm) {
		get_imprest_advance(frm)
	},

	branch: function (frm) {
		frm.set_value('party_type', '');
		frm.set_value('party', '');
		frm.set_value('items', '');
		frm.refresh_field('items')
		frm.set_value('imprest_advance_list', '');
		frm.refresh_field('imprest_advance_list')

		// frm.set_query('party', function() {
		// 	return {
		// 		filters: {
		// 			"branch": frm.doc.branch
		// 		}
		// 	};
		// });
	},
	// Step 2: User selects taxes_and_charges
	taxes_and_charges: function (frm) {
		// Clear values if no template is selected
		if (!frm.doc.taxes_and_charges) {
			frm.set_value('account_head', '');
			frm.set_value('tax_rate', 0);
			frm.set_value('gst_amount', 0);
			frm.set_value('total_gst_amount', 0);
			return;
		}

		// Fetch tax lines for the selected template
		frappe.call({
			method: "erpnext.accounts.doctype.imprest_recoup.imprest_recoup.get_taxes_for_template",
			args: { template_name: frm.doc.taxes_and_charges },
			callback: function (res) {
				if (res.message && res.message.length) {
					const tax = res.message[0]; // take the first tax line
					frm.set_value('account_head', tax.account_head);
					frm.set_value('tax_rate', flt(tax.rate));
				} else {
					// Clear if no tax found for template
					frm.set_value('account_head', '');
					frm.set_value('tax_rate', 0);
				}
			}
		});
	},


});

frappe.ui.form.on("Imprest Recoup Item", {
	amount: function (frm, cdt, cdn) {
		get_imprest_advance(frm)
	},
	recoup_type: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (!frm.doc.company) {
			d.recoup_type = "";
			frappe.msgprint(__("Please set the Company"));
			this.frm.refresh_fields();
			return;
		}

		if (!d.recoup_type) {
			return;
		}
		return frappe.call({
			method: "erpnext.accounts.doctype.imprest_recoup.imprest_recoup.get_imprest_recoup_account",
			args: {
				"recoup_type": d.recoup_type,
				"company": frm.doc.company
			},
			callback: function (r) {
				if (r.message) {
					d.account = r.message.account;
				}
				frm.refresh_field("items")
				frm.refresh_fields();
			}
		});
	}
})

function check_and_set_tax_template(frm) {
	const intl_template = "GST 5% (International) - CDCL" || "GST 5% (Domestic) - CDCL";
	frm.set_query("taxes_and_charges", function () {
		return {
			filters: {
				company: frm.doc.company,
				docstatus: ["!=", 2],
				title: ["=", intl_template]
			}
		};
	});
}


var get_imprest_advance = function (frm) {
	frm.set_value('total_amount', 0);
	frappe.call({
		method: 'populate_imprest_advance',
		doc: frm.doc,
		callback: () => {
			frm.refresh_field('imprest_advance_list')
			frm.refresh_fields()
		}
	})
}

