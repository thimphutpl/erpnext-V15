// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Service Sales Jobcard", {
    setup: function (frm) {
		frm.set_query("price_costing", "table_fspm", function (doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					"docstatus": 1,
					"item": row.item_code,
				}
			}
		});
    },
	refresh(frm) {
        calculate_payable_amount(frm);
        // Ensure Save button is always visible
        if(frm.doc.docstatus === 0) {
            frm.page.show_save();
        }

        // Control Submit button based on status
        control_submit_button(frm);

        if (!frm.doc.sales_order && frm.doc.docstatus == 1 && frm.doc.jobcard_type != "Free Services")  {
			frm.add_custom_button(__("Service Sales Order"), function () {
				frm.trigger("create_service_sales_order");
				},
				__("Create")
			);
			frm.add_custom_button(__("Spares Sales Order"), function () {
				frm.trigger("create_spare_sales_order");
				},
				__("Create")
			);
		}
        if(frm.doc.docstatus == 1) {
            frm.add_custom_button(__('View GL Entries'), function() {
                frappe.set_route('query-report', 'General Ledger', {voucher_no: frm.doc.name});
            }, __('View'));
        }
        
	},

    jobcard_status(frm) {
        // Re-check when status changes
        control_submit_button(frm);
    },

    create_service_sales_order: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.service_sales_jobcard.service_sales_jobcard.make_service_sales_jobcard",
			frm: cur_frm
		})
	},
    create_spare_sales_order: function (frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.selling.doctype.service_sales_jobcard.service_sales_jobcard.make_spare_sales_jobcard",
			frm: cur_frm
		})
	},

    // jocard type for showing requesting branch and cost center
    jobcard_type(frm) {
        frm.trigger("toggle_inter_company_fields");
        // if(frm.doc.jobcard_type){
        //     frm.set_df_property("customer_id", "reqd", 1);

        // }
    },

    onload(frm) {
        frm.trigger("toggle_inter_company_fields");
    },

    toggle_inter_company_fields(frm) {
        if (!frm.doc.jobcard_type) {
            frm.set_df_property("requesting_branch", "hidden", 1);
            frm.set_df_property("requesting_cost_center", "hidden", 1);
            return;
        }

        // Fetch inter_company value from Jobcard Type
        frappe.db.get_value("Jobcard Type", frm.doc.jobcard_type, "inter_company")
            .then(r => {
                let inter_company = r.message.inter_company;

                if (inter_company == 1) {
                    frm.set_df_property("requesting_branch", "hidden", 0);
                    frm.set_df_property("requesting_cost_center", "hidden", 0);
                } else {
                    frm.set_df_property("requesting_branch", "hidden", 1);
                    frm.set_df_property("requesting_cost_center", "hidden", 1);
                }
            });
    }
});

function control_submit_button(frm) {
    // Hide Submit for Ongoing
    if (frm.doc.jobcard_status === "Ongoing") {
        // Hide primary submit button
        frm.page.set_primary_action(null);
        frappe.dom.hide_submit();
        $("button[data-label='Submit']").hide();

        // Show Save button
        if(frm.doc.docstatus === 0) {
            frm.page.show_save();
        }
    } 
    else if (frm.doc.jobcard_status === "Completed" && frm.doc.docstatus != 1) {
        // Restore Submit
        frm.page.set_primary_action(__('Submit'), () => frm.savesubmit());
        $("button[data-label='Submit']").show();
    }
}


frappe.ui.form.on('Jobcard Service Details', {
    // rate: function(frm, cdt, cdn) {
    //     calculate_amount(frm, cdt, cdn);
    // },
    // quantity: function(frm, cdt, cdn) { // Note: 'qty' is the standard field name, not 'quantity'
    //     calculate_amount(frm, cdt, cdn);
    // }
    rate: function(frm, cdt, cdn) {
        update_item_amount(frm, cdt, cdn);
        calculate_payable_amount(frm);
    },
    quantity: function(frm, cdt, cdn) {
        update_item_amount(frm, cdt, cdn);
        calculate_payable_amount(frm);
    },
    items_add: function(frm, cdt, cdn) {
        calculate_payable_amount(frm);
    },
    items_remove: function(frm, cdt, cdn) {
        calculate_payable_amount(frm);
    }
});

// function calculate_amount(frm, cdt, cdn) {
//     let total_payable = 0.0;
//     let row = frappe.get_doc(cdt, cdn);
//     if (row.rate && row.quantity) {
//         row.amount = row.rate * row.quantity;
//     } else {
//         row.amount = 0;
//     }
//     // if (item.amount) {
//     //     total_payable += flt(item.amount);
//     // }
//     refresh_field('items'); // Refresh the entire child table
// }

function update_item_amount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.rate && row.quantity) {
        row.amount = flt(row.rate) * flt(row.quantity);
        refresh_field('amount', cdn, 'items');
    }
}

function calculate_payable_amount(frm) {
    let total_payable = 0.0;
    
    $.each(frm.doc.items || [], function(i, item) {
        // Ensure item amount is calculated
        if (item.rate && item.quantity && !item.amount) {
            item.amount = flt(item.rate) * flt(item.quantity);
        }
        
        if (item.amount) {
            total_payable += flt(item.amount);
        }
    });
    
    frm.set_value('payable_amount', total_payable);
    frm.refresh_field('payable_amount');
}


frappe.ui.form.on('Jobcard Spareparts Details', {
	price_costing: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.call({
			method: 'erpnext.selling.doctype.sales_order.sales_order.get_selling_price',
			args: { item_code: row.item_code, price_template: row.price_costing},
			callback: function (r) {
				if (r.message) {
					frappe.model.set_value(cdt, cdn, 'rate', r.message);
				}else{
					frappe.msgprint('Selling Price not found for the selected Item');
				}
			}
		});
	},
});
