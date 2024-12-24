// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Imprest Settlement", {
    onload: function(frm) {
        frm.set_query("branch", function(doc){
            return {
                filters: {
                    'company': doc.company,
                }
            }
        });

        frm.set_query("party", function(doc) {
			if (doc.party_type === "Employee") {
				return {
					filters: {
						'company': doc.company,
					}
				};
			} else {
				return {};
			}
		});

		frm.set_query("account", "items", function(doc){
            return {
                filters: {
                    'company': doc.company,
                }
            }
        });
    },

	refresh(frm) {
		// show General Ledger
	frm.add_custom_button(__('Accounting Ledger'), function () {
		frappe.route_options = {
			voucher_no: frm.doc.name,
			from_date: frm.doc.posting_date,
			to_date: frm.doc.posting_date,
			company: frm.doc.company,
			group_by_voucher: false
		};
		frappe.set_route("query-report", "General Ledger");
	}, __("View"));
	cur_frm.page.set_inner_btn_group_as_primary(__('View'));
	},

	party: function(frm) {
		frm.events.get_imprest_advance(frm)
	},

    get_imprest_advance: function(frm){
		frm.events.get_imprest_advance(frm)
	},

	get_imprest_advance: function(frm) {
		frappe.call({
			method: 'populate_imprest_advance',
			doc: frm.doc,
			callback: (response) => {
				if (!response.exc) {
					frm.refresh_field('advances');
					frm.refresh_fields();
					frm.events.set_total_advance_amt(frm);
				} else {
					frappe.msgprint(__('Failed to fetch imprest advances.'));
				}
			},
			error: (error) => {
				frappe.msgprint(__('An error occurred while fetching imprest advances.'));
			}
		});
	},
	
	set_total_advance_amt: function(frm) {
		let total_amount = 0.0;
		$.each(frm.doc.advances || [], function(i, row) {
			if (row.advance_amount) {
				total_amount += flt(row.advance_amount);
			}
		});
		frm.set_value("total_advance_amount", total_amount);
		frm.refresh_field("total_advance_amount");
	},
	

	get_outstanding_invoices: function(frm) {
		const today = frappe.datetime.get_today();
		let fields = [
			{fieldtype:"Section Break", label: __("Posting Date")},
			{fieldtype:"Date", label: __("From Date"), fieldname:"from_posting_date", default:frappe.datetime.add_days(today, -30)},
			{fieldtype:"Link", label:__("Party Type"), fieldname:"party_type", options:"Party Type", default:"Supplier"},
			
			// {fieldtype:"Link", label:__("Cost Center"), fieldname:"cost_center", options:"Cost Center"},
			{fieldtype:"Column Break"},
			{fieldtype:"Date", label: __("To Date"),fieldname: "to_posting_date", default:today},
			{fieldtype:"Dynamic Link", label:__("Party"), fieldname:"party", options:"party_type"},
		];

		frappe.prompt(fields, function(filters){
			frappe.flags.allocate_payment_amount = true;
			frm.events.get_outstanding_documents(frm, filters)
		}, __("Filters"), __("Get Outstanding Documents"));
	},

	get_outstanding_documents: function(frm, filters) {
		frm.clear_table("references");

		if(!frm.doc.party) {
			return;
		}

		frm.events.check_mandatory_to_fetch(frm);
		var args = {
			"posting_date": frm.doc.posting_date,
			"company": frm.doc.company,
		}
		for (let key in filters) {
			args[key] = filters[key];
		}

		frappe.flags.allocate_payment_amount = filters['allocate_payment_amount'];

		return frappe.call({
			method: "erpnext.accounts.doctype.imprest_settlement.imprest_settlement.get_outstanding_reference_documents",
			args: {
				args: args
			},
			callback: function(r) {
				if(r.message) {
					$.each(r.message, function(i, d){						
						var c = frm.add_child("references")
						c.reference_doctype = d.voucher_type;
						c.reference_name = d.voucher_no;
						c.outstanding_amount = d.outstanding_amount;
						c.total_amount = d.invoice_amount;
						c.allocated_amount = d.outstanding_amount;
						c.account = d.account;
					});	
					frm.refresh_field("references");
					frm.events.set_total_allocated_amount(frm);
				}
			}
		});
	},

	set_total_allocated_amount: function(frm) {
		let total_allocated = 0.0
		$.each(frm.doc.references || [], function(i, row) {
			if (row.allocated_amount) {
				total_allocated += flt(row.allocated_amount);
			}
		});
		frm.set_value("total_allocated_amount", total_allocated);
		frm.refresh_field("total_allocated_amount");
	},

	check_mandatory_to_fetch: function(frm) {
		$.each(["Company", "Party Type", "Party"], function(i, field){
			if (!frm.doc[frappe.model.scrub(field)]) {
				frappe.msgprint(__("Please select {0} first", [field]));
				return false;
			}
		});
	}
});

