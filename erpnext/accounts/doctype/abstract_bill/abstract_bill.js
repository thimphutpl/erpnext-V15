// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Abstract Bill", {
	setup: function(frm) {
		frm.set_query("fiscal_year", function () {
			return {
				query: "erpnext.accounts.doctype.abstract_bill.abstract_bill.get_fiscal_year",
				filters: {
					company: frm.doc.company,
				}
			};
		});
	},

    onload: (frm) => {
		frm.set_query("branch", function(doc) {
			return {
				filters: {
					'company': doc.company,
				}
			}
		});

        frm.set_query("cost_center", "items", function(doc) {
            return {
                filters: {
                    'is_group': 0
                }
            }
        });

        frm.set_query("account", "items", function(doc){
            return {
                filters: {
                    'is_group': 0
                }
            }
        })

        frm.set_query("party", "items", function(doc, cdt, cdn){
            var child = locals[cdt][cdn];
            if (doc.currency == "BTN" && child.party_type == "Supplier") {
                return {
                    filters: {
                        'country': 'Bhutan',
                    }
                };
            } else if (doc.currency != "BTN" && child.party_type == "Supplier") {
                return {
                    filters: {
                        'country': ['!=', 'Bhutan'],
                    }
                };
            }
        });        
    },

	refresh(frm) {
        refresh_html(frm);

		frm.trigger("currency");
		frm.trigger("set_dynamic_field_label");
	},

    international_payment: function (frm) {
        frm.events.clear_items_table(frm);
    },

    company: function (frm) {
        frm.events.clear_items_table(frm);
    },

    clear_items_table: function (frm) {
		frm.clear_table('items');
		frm.refresh();
	},

	transaction_type: (frm) => {
		frm.events.clear_items_table(frm);
	},

	get_items: function(frm){
		return frappe.call({
			doc: frm.doc,
			method: 'get_transactions_detail',
			callback: function(r) {
				if (r.message){
					
					frm.refresh_field("items");
				}
			},
			freeze: true,
			
		});
	},

    currency: (frm) => {
        let company_currency = erpnext.get_currency(frm.doc.company);
		if (company_currency != frm.doc.company) {
			frappe.call({
				method: "erpnext.setup.utils.get_exchange_rate",
				args: {
					from_currency: company_currency,
					to_currency: frm.doc.currency,
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("exchange_rate", flt(r.message));
						frm.set_df_property(
							"exchange_rate",
							"description",
							"1 " + frm.doc.currency + " = [?] " + company_currency
						);
					}
				},
			});
		} else {
			frm.set_value("exchange_rate", 1.0);
			frm.set_df_property("exchange_rate", "hidden", 1);
			frm.set_df_property("exchange_rate", "description", "");
		}

		frm.trigger("total_amount");
		frm.trigger("set_dynamic_field_label");
	},

    total_amount: (frm) => {
        frm.set_value("base_total_amount", flt(frm.doc.total_amount) * flt(frm.doc.exchange_rate));
    },

    set_dynamic_field_label: function (frm) {
		frm.trigger("change_grid_labels");
		frm.trigger("change_form_labels");
	},

    change_form_labels: function (frm) {
		let company_currency = erpnext.get_currency(frm.doc.company);
		frm.set_currency_labels(["base_total_amount"], company_currency);
		frm.set_currency_labels(["total_amount"], frm.doc.currency);

		// toggle fields
		frm.toggle_display(
			["exchange_rate", "base_total_amount"],
			frm.doc.currency != company_currency
		);
	},

    change_grid_labels: function (frm) {
		let company_currency = erpnext.get_currency(frm.doc.company);
		frm.set_currency_labels(["base_amount"], company_currency, "items");
		frm.set_currency_labels(["amount"], frm.doc.currency, "items");

		let item_grid = frm.fields_dict.items.grid;
		$.each(["base_amount"], function (i, fname) {
			if (frappe.meta.get_docfield(item_grid.doctype, fname))
				item_grid.set_column_disp(fname, frm.doc.currency != company_currency);
		});
		frm.refresh_fields();
	},

    calculate_total: function (frm) {
		let total = 0,
			base_total = 0;
		frm.doc.items.forEach((item) => {
			total += item.amount;
			base_total += item.base_amount;
		});

		frm.set_value({
			total_amount: flt(total),
			base_total_amount: flt(base_total),
		});
	},
});

frappe.ui.form.on("Abstract Bill Item", {
    calculate: function (frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		// frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
		frappe.model.set_value(cdt, cdn, "base_amount", flt(frm.doc.exchange_rate) * flt(row.amount));
		frm.trigger("calculate_total");
	},
	amount: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},
});

var refresh_html = function(frm){
	var journal_entry_status = "";
	if(frm.doc.journal_entry_status){
		journal_entry_status = '<div style="font-style: italic; font-size: 0.8em; ">* '+frm.doc.journal_entry_status+'</div>';
	}
	
	if(frm.doc.journal_entry){
		$(cur_frm.fields_dict.journal_entry_html.wrapper).html('<label class="control-label" style="padding-right: 0px;">Journal Entry</label><br><b>'+'<a href="/desk/Form/Journal Entry/'+frm.doc.journal_entry+'">'+frm.doc.journal_entry+"</a> "+"</b>"+journal_entry_status);
	}	
}
