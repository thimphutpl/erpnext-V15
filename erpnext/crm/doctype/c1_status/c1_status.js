// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("C1 Status", {
	refresh(frm) {
        if (!frm.doc.c2_status && frm.doc.docstatus == 1)  {
			frm.add_custom_button(__("C2 Status"), function () {
				frm.trigger("create_c2_status");
				},
				__("Create")
			);
		};
        frm.fields_dict["items"].grid.get_field("item_code").get_query = () => {
            return {
                filters: {
                    item_group: "Sales Product"
                }
            };
        };
        frm.set_query("price_costing", "items", function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
        
            return {
                query: "erpnext.crm.doctype.c1_status.c1_status.get_filtered_items",
                filters: {
                    item_code: row.item_code
                }
            };
        });
	},
    create_c2_status: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.c1_status.c1_status.make_c1_status",
			frm: cur_frm
		})
	},
});

frappe.ui.form.on('Customer Quotation Details', {
    price_costing: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.price_costing && row.item_code){
            frappe.call({
                method: "erpnext.crm.doctype.c1_status.c1_status.get_item_rate",
                args: {
                    price_costing: row.price_costing,
                    item: row.item_code,
                },
                callback: function (r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, "rate", r.message);
                        row.trigger("rate")
                    }
                },
            });
        }
    },
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    quantity: function(frm, cdt, cdn) { 
        calculate_amount(frm, cdt, cdn);
    },
    gst: function(frm, cdt, cdn) { 
        calculate_amount(frm, cdt, cdn);
    },
    bst: function(frm, cdt, cdn) { 
        calculate_amount(frm, cdt, cdn);
    },
    cd: function(frm, cdt, cdn) { 
        calculate_amount(frm, cdt, cdn);
    },
    gt: function(frm, cdt, cdn) { 
        calculate_amount(frm, cdt, cdn);
    },
    et: function(frm, cdt, cdn) { 
        calculate_amount(frm, cdt, cdn);
    },
    amount: function(frm, cdt, cdn) {
        update_item_amount(frm, cdt, cdn);
        calculate_payable_amount(frm);
    },
    discount_amount: function(frm, cdt, cdn) {
        update_item_amount(frm, cdt, cdn);
        calculate_payable_amount(frm);
    },
    item_code: function(frm, cdt, cdn) {
        frm.refresh_field("items");
    }
    // items_add: function(frm, cdt, cdn) {
    //     calculate_payable_amount(frm);
    // },
    // items_remove: function(frm, cdt, cdn) {
    //     calculate_payable_amount(frm);
    // },
});

function update_item_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    // if (row.amount && row.discount_amount) {
        row.net_price = flt(row.amount || 0) - flt(row.discount_amount || 0);
        refresh_field('net_price', cdn, 'items');
        
    // }
}

function calculate_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    row.amount = (flt(row.rate || 0) + flt(row.gst || 0) + flt(row.bst || 0) + flt(row.cd || 0) + flt(row.gt || 0) + flt(row.et || 0)) * flt(row.quantity || 0);
    row.net_price = row.amount;
    refresh_field('amount', cdn, 'items');
    refresh_field('net_price', cdn, 'items');

    // frappe.model.set_value(cdt, cdn, "amount", amount);
}
