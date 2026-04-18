// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Allotment Item", {
    refresh(frm) {
        if (!frm.doc.sales_order && frm.doc.docstatus == 1) {
            frm.add_custom_button(__("Sales Order"), function () {
                frm.trigger("create_sales_order");
            },
                __("Create")
            );
        }
        // if (frm.doc.docstatus == 1)  {
        // 	frm.add_custom_button(__("Purchase Order"), function () {
        // 		frm.trigger("create_purchase_order");
        // 		},
        // 		__("Create")
        // 	);
        // }
        frm.set_query("price_costing", "items", function (doc, cdt, cdn) {
            let row = locals[cdt][cdn];

            return {
                query: "erpnext.crm.doctype.c1_status.c1_status.get_filtered_items",
                filters: {
                    item_code: row.item_code
                }
            };
        });

    },
    get_details: function (frm) {
        frappe.call({
            method: "erpnext.crm.doctype.allotment_item.allotment_item.get_details",
            callback: function (r) {
                if (r.message) {
                    frm.clear_table("items");
                    r.message.forEach(function (row) {
                        let child = frm.add_child("items");
                        child.customer_id = row.customer_id
                        child.salutation = row.salutation
                        child.customer_name = row.customer_name
                        child.phone_number = row.phone_number
                        child.email_id = row.email_id
                        child.primary_address = row.primary_address
                        child.customer_details = row.customer_details
                        child.responsible_branch = row.responsible_branch
                        child.customer_report = row.customer_report
                        child.item_code = row.item_code
                        child.item_name = row.item_name
                        child.qty = row.qty
                        child.rate = row.net_price
                        child.c2_status = row.name
                        child.price_costing = row.price_costing
                        child.tvo_numbervc_numbervi_number = row.tvo
                    });

                    // Refresh the table to show the new data
                    frm.refresh_field("items");
                }
            }
        })
    },
    // before_submit: function(frm) {
    //     let selected = frm.fields_dict.items.grid.get_selected_children();
    //     let selected_names = selected.map(row => row.name);
    //     frm.set_value("selected_rows", JSON.stringify(selected_names));
    //     alert(frm.doc.selected_rows)
    // }
    // create_sales_order: function (frm) {
    // 	frappe.model.open_mapped_doc({
    // 		method: "erpnext.crm.doctype.allotment_item.allotment_item.create_sales_order",
    // 		frm: cur_frm
    // 	})
    // },
    create_sales_order: function (frm) {
        frappe.call({
            method: "erpnext.crm.doctype.allotment_item.allotment_item.create_sales_order",
            args: {
                docname: frm.doc.name
            },
            callback: function (r) {
                if (r.message) {
                    let links = r.message.map(name => {
                        return `<a href="/app/sales-order/${name}" target="_blank">${name}</a>`;
                    });
                    frappe.msgprint(
                        "Sales Orders Created:<br>" + links.join("<br>")
                    );
                    frm.reload_doc();
                }
            }
        });
    },
    create_purchase_order: function (frm) {
        frappe.model.open_mapped_doc({
            method: "erpnext.crm.doctype.allotment_item.allotment_item.create_purchase_order",
            frm: cur_frm
        })
    },
});


frappe.ui.form.on('Allotment Item Item', {
    price_costing: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.price_costing && row.item_code) {
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
    item_code: function (frm, cdt, cdn) {
        frm.refresh_field("items");
    }
});
