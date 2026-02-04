// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("branch", "expense_bank_account", "bank_account")
cur_frm.add_fetch("fuelbook", "supplier", "supplier")
cur_frm.add_fetch("branch", "expense_bank_account", "bank_account")


frappe.ui.form.on('HSD Payment', {
	onload: function (frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},

	refresh: function (frm) {
		create_custom_buttons(frm);
		if (frm.doc.docstatus == 1) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function () {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}

	},
	taxes_and_charges: function (frm) {
		if (!frm.doc.taxes_and_charges || !frm.doc.supplier) {
			frm.set_value('account_head', '');
			frm.set_value('tax_rate', 0);
			frm.set_value('gst_amount', 0);
			frm.set_value('total_gst_amount', 0);
			frm.set_value('rate_including_gst', 0);
			frm.set_value('included_gst', 0);
			return;
		}

		frappe.db.get_doc("Supplier", frm.doc.supplier).then(supplier => {
			let template_name = (supplier.country !== "Bhutan")
				? "GST 5% (International) - CDCL"
				: "GST 5% (Domestic) - CDCL";

			// Only auto-fill if the user selected the correct template
			if (frm.doc.taxes_and_charges !== template_name) {
				frm.set_value('account_head', '');
				frm.set_value('tax_rate', 0);
				frm.set_value('included_gst', 0);
				return;
			}

			// Fetch tax lines from backend
			frappe.call({
				method: "erpnext.fleet_management.doctype.pol_receive.pol_receive.get_taxes_for_template",
				args: { template_name: template_name },
				callback: function (res) {
					if (res.message && res.message.length) {
						const tax = res.message[0];
						frm.set_value('account_head', tax.account_head);
						frm.set_value('tax_rate', flt(tax.rate));
						frm.set_value('included_gst', 1);
					}
				}
			});
		});
	},
	"branch": function (frm) {
		return frappe.call({
			method: "erpnext.custom_utils.get_cc_warehouse",
			args: {
				"branch": frm.doc.branch
			},
			callback: function (r) {
				cur_frm.set_value("cost_center", r.message.cc)
				cur_frm.refresh_fields()
			}
		})
	},

	"get_pol_invoices_with_gst": function (frm) {
		if (frm.doc.fuelbook) {
			return frappe.call({
				method: "get_invoices_with_gst",
				doc: frm.doc,
				callback: function (r, rt) {
					frm.refresh_field("items");
					frm.refresh_fields();

					const GST_RATE = 5;
					let html = `<table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Receive POL Reference</th>
                                        <th>GST %</th>
                                        <th>GST Amount</th>
                                        <th>Amount Without GST</th>
                                        <th>Total Amount</th>
                                    </tr>
                                </thead>
                                <tbody>`;

					(frm.doc.items || []).forEach(row => {
						if (!row.amount_without_gst) return;
						let gst_amount = flt(row.amount_without_gst * (GST_RATE / 100), 2);
						html += `<tr>
                            <td>${row.pol || ""}</td>
                            <td>${GST_RATE}</td>
                            <td>${gst_amount}</td>
                            <td>${row.amount_without_gst}</td>
                            <td>${row.payable_amount}</td>
                         </tr>`;
					});
					html += `</tbody></table>`;

					frm.set_value("tax_break_html", html);
					frm.refresh_field("tax_break_html");
				}
			});
		}
		else {
			msgprint("Select Fuelbook before clicking on the button")
		}
	},
	"get_pol_invoices_without_gst": function (frm) {
		if (frm.doc.fuelbook) {
			return frappe.call({
				method: "get_invoices_without_gst",
				doc: frm.doc,
				callback: function (r, rt) {
					frm.refresh_field("items");
					frm.refresh_fields();

				}
			});
		}
		else {
			msgprint("Select Fuelbook before clicking on the button")
		}
	},

	"amount": function (frm) {
		if (frm.doc.amount > frm.doc.actual_amount) {
			cur_frm.set_value("amount", frm.doc.actual_amount)
			msgprint("Amount cannot be greater than the Total Payable Amount")
		}
		else {
			var total = frm.doc.amount
			frm.doc.items.forEach(function (d) {
				var allocated = 0
				if (total > 0 && total >= d.payable_amount) {
					allocated = d.payable_amount
				}
				else if (total > 0 && total < d.payable_amount) {
					allocated = total
				}
				else {
					allocated = 0
				}

				d.allocated_amount = allocated
				d.balance_amount = d.payable_amount - allocated
				total -= allocated
			})
			cur_frm.refresh_field("items")
		}
	}
});

frappe.ui.form.on("HSD Payment", "refresh", function (frm) {
	cur_frm.set_query("fuelbook", function () {
		return {
			"filters": {
				"disabled": 0,
				"branch": frm.doc.branch
			}
		};
	});
})

frappe.ui.form.on("HSD Payment Item", {
	"pol": function (frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		rec_amount = flt(frm.doc.amount)
		act_amount = flt(frm.doc.actual_amount)
		if (item.pol) {
			frappe.call({
				method: "frappe.client.get_value",
				args: {
					doctype: item.reference_type,
					fieldname: ["payable_amount"],
					filters: {
						name: item.pol
					}
				},
				callback: function (r) {
					frappe.model.set_value(cdt, cdn, "payable_amount", r.message.payable_amount)
					frappe.model.set_value(cdt, cdn, "allocated_amount", r.message.payable_amount)
					cur_frm.refresh_field("payable_amount")
					cur_frm.refresh_field("allocated_amount")

					cur_frm.set_value("actual_amount", act_amount + flt(r.message.payable_amount))
					cur_frm.refresh_field("actual_amount")
					cur_frm.set_value("amount", rec_amount + flt(r.message.payable_amount))
					cur_frm.refresh_field("amount")
				}
			})
		}
	},

	"before_items_remove": function (frm, cdt, cdn) {
		doc = locals[cdt][cdn]
		amount = flt(frm.doc.amount)
		ac_amount = flt(frm.doc.actual_amount) - flt(doc.payable_amount)
		cur_frm.set_value("actual_amount", ac_amount)
		cur_frm.refresh_field("actual_amount")
		cur_frm.trigger("amount")
	}
})
var create_custom_buttons = function (frm) {
	var status = ["Failed", "Upload Failed", "Cancelled"];

	if (frm.doc.docstatus == 1 && frm.doc.amount > 0  /*&& !frm.doc.cheque_no*/) {
		console.log(frm.doc.docstatus, frm.doc.amount)
		if (!frm.doc.bank_payment || status.includes(frm.doc.payment_status)) {
			frm.page.set_primary_action(__('Process Payment'), () => {
				frappe.model.open_mapped_doc({
					method: "erpnext.fleet_management.doctype.hsd_payment.hsd_payment.make_bank_payment",
					frm: cur_frm
				})
			});
		}
	}
}