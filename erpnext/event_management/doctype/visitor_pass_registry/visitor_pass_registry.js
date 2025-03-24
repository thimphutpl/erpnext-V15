// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visitor Pass Registry", {
	setup(frm) {
		frm.set_query("cashier", function (doc) {
			return {
				query: "erpnext.event_management.doctype.visitor_pass_registry.visitor_pass_registry.get_cashiers",
				filters: { parent: doc.location },
			};
		});

		frm.set_query("mode_of_payment", "items", function(doc){
			return {
				query: "erpnext.event_management.doctype.visitor_pass_registry.visitor_pass_registry.get_mode_of_payment",
				filters: { parent: doc.location },
			};
		});

		frm.set_query("mode_of_payment", "other_charges", function(doc){
			return {
				query: "erpnext.event_management.doctype.visitor_pass_registry.visitor_pass_registry.get_mode_of_payment",
				filters: { parent: doc.location },
			};
		});

		frm.set_query("location", function(){
			return {
				filters: {
					'disabled': 0,
					'is_recreational_park': 1,
				}
			}
		});
	},

	refresh(frm) {
		// if (frm.doc.docstatus == 1) {
        //     if (!["Closed"].includes(frm.doc.status)) {
        //         let close_btn = frm.add_custom_button(
		// 			__("Close"),
		// 			() => frm.trigger("close_visitor_pass_registry"),
		// 			__("Status")
		// 		);
		// 		close_btn.addClass("btn-danger");
        //     }
        // }
		if (frm.doc.docstatus == 0) {
			frm.add_custom_button(__("Add Entry Fee"), () => 
				frm.trigger("add_entry_fee"),
				__("Add")
			);

			frm.add_custom_button(__("Other Charges"), () => 
				frm.trigger("add_other_charges"),
				__("Add")
			);
		}
	},

	location: (frm) => {
		if (frm.doc.location) {
			frappe.db.get_doc("Location", frm.doc.location).then(({ payments }) => {
				if (payments.length) {
					frm.doc.transaction_details = [];
					payments.forEach(({ mode_of_payment }) => {
						frm.add_child("transaction_details", { mode_of_payment });
					});
					frm.refresh_field("transaction_details");
				}
			});
		}
	},

    // close_visitor_pass_registry(frm) {
    //     frappe.confirm(
    //         __("Are you sure you want to close this Visitor Pass?"),
    //         () => frm.events.update_status(frm, "Closed")
    //     );
    // },

    // update_status(frm, status) {
    //     frappe.call({
    //         method: "erpnext.event_management.doctype.visitor_pass_registry.visitor_pass_registry.update_status",
    //         args: { status: status, name: frm.doc.name },
    //         callback: function (r) {
    //             if (!r.exc) {
    //                 frm.set_value("status", status);
    //                 frm.reload_doc();
    //             }
    //         },
    //         error: function (err) {
    //             frappe.msgprint(__("Failed to update status: ") + err.message);
    //         }
    //     });
    // },

	add_entry_fee: function(frm) {
        let fields = [
            // { fieldtype: "Section Break", label: __("Ticket Detail") },
			{
                fieldtype: "Link",
                label: __("Ticket Type"),
                fieldname: "ticket_type",
                options: "Ticket Type",
                reqd: 1,
            },
            
            { fieldtype: "Column Break" },
			{
                fieldtype: "Int",
                label: __("Qty"),
                fieldname: "qty",
                reqd: 1,
				default: 1,
            },
            { fieldtype: "Column Break" },
            {
                fieldtype: "Link",
                label: __("Mode of Payment"),
                fieldname: "mode_of_payment",
                options: "Mode of Payment",
                reqd: 1,
				get_query: function () {
					return {
						query: "erpnext.event_management.doctype.visitor_pass_registry.visitor_pass_registry.get_mode_of_payment",
						filters: { parent: frm.doc.location },
					};
				},
            },
        ];

        frappe.prompt(
            fields,
            (data) => {
                frm.events.add_new_entry_fee(frm, data);
            },
            __("Add Entry Fee Details"),
            __("Add")
        );
    },

    add_new_entry_fee: function(frm, data) {
        if (!frm.doc.items) {
            frm.doc.items = [];
        }

		frappe.db.get_value("Ticket Type", data.ticket_type, "ticket_price", (r) => {
			if (r && r.ticket_price) {
				let ticket_price = r.ticket_price;
	
				let row = frm.add_child("items", {
					ticket_type: data.ticket_type,
					qty: data.qty,
					ticket_price: ticket_price,
					mode_of_payment: data.mode_of_payment,
					amount: data.qty * ticket_price
				});
	
				frm.refresh_field("items");
				frappe.msgprint(__("Entry Fee Added Successfully!"));
			} else {
				frappe.msgprint(__("Ticket price not found for the selected ticket type."));
			}
		});
	},

	add_other_charges: function(frm) {
		let fields = [
			{
				fieldtype: "Link",
				label: __("Fee Type"),
				fieldname: "fee_type",
				options: "Fee Type",
				reqd: 1,
			},
	
			{ fieldtype: "Column Break" },
			{
				fieldtype: "Int",
				label: __("Qty"),
				fieldname: "qty",
				reqd: 1,
				default: 1,
			},
			{ fieldtype: "Column Break" },
			{
				fieldtype: "Link",
				label: __("Mode of Payment"),
				fieldname: "mode_of_payment",
				options: "Mode of Payment",
				reqd: 1,
				get_query: function () {
					return {
						query: "erpnext.event_management.doctype.visitor_pass_registry.visitor_pass_registry.get_mode_of_payment",
						filters: { parent: frm.doc.location },
					};
				},
			},
		];
	
		frappe.prompt(
			fields,
			(data) => {
				frm.events.add_new_other_charges(frm, data);
			},
			__("Add Other Details"),
			__("Add")
		);
	},
	
	add_new_other_charges: function(frm, data) {
		// frappe.call({
		// 	method: "add_other_charges",
		// 	args: {
		// 		fee_type: data.fee_type,
		// 		qty: data.qty,
		// 		mode_of_payment: data.mode_of_payment
		// 	},
		// 	callback: function(response) {
		// 		if(response.message) {
		// 			frappe.msgprint(response.message);
		// 		}
		// 	}
		// });

		if (!frm.doc.other_charges) {
			frm.doc.other_charges = [];
		}
	
		frappe.db.get_value("Fee Type", data.fee_type, "rate", (r) => {
			if (r && r.rate) {
				let rate = r.rate;
	
				let row = frm.add_child("other_charges", {
					fee_type: data.fee_type,
					qty: data.qty,
					rate: rate,
					mode_of_payment: data.mode_of_payment,
					amount: data.qty * rate
				});
	
				frm.refresh_field("other_charges");
				frappe.msgprint(__("Other Charges Added Successfully!"));
			} else {
				frappe.msgprint(__("Rate not found for the selected fee type."));
			}
		});
	}
	
});

frappe.ui.form.on("Visitor Pass Registry Item", {
	ticket_type: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

    qty: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

	ticket_price: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

	calculate: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
		
        frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.ticket_price));
    },
});

frappe.ui.form.on("Visitor Pass Other Charges", {
	fee_type: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

    qty: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

	ticket_price: function (frm, cdt, cdn) {
		frm.trigger("calculate", cdt, cdn);
	},

	calculate: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
		
        frappe.model.set_value(cdt, cdn, "amount", flt(row.qty) * flt(row.rate));
    },
});
