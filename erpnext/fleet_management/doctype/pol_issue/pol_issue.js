// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('POL Issue', {
    onload: function (frm) {
        if (!frm.doc.posting_date) {
            frm.set_value('posting_date', frappe.datetime.now_date());
        }
        frm.trigger("issue_from");
    },

    refresh: function (frm) {
        if (frm.doc.docstatus == 1) {
            cur_frm.add_custom_button(__("Stock Ledger"), function () {
                frappe.route_options = {
                    voucher_no: frm.doc.name,
                    from_date: frm.doc.posting_date,
                    to_date: frm.doc.posting_date,
                    company: frm.doc.company
                };
                frappe.set_route("query-report", "Stock Ledger Report");
            }, __("View"));

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

    // tanker: function (frm) {
    //     if (frm.doc.tanker) {
    //         frappe.call({
    //             method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_data", // Update with the correct path
    //             args: {
    //                 tanker: frm.doc.tanker,
    //                 branch: frm.doc.branch,
    //                 pol_type: frm.doc.pol_type,
    //             },
    //             callback: function (response) {
    //                 if (response.message) {
    //                     // let data = response.message;
    //                     // frappe.msgprint({
    //                     //     title: __('Fetched Equipment Data'),
    //                     //     message: `<pre>${JSON.stringify(data, null, 4)}</pre>`,
    //                     //     indicator: 'green'
    //                     // });
    //                     frm.set_value('tank_balance', response.message[0]);
    //                     // frm.set_value('rate', response.message[1]);
    //                 } else {
    //                     frappe.msgprint(__('No data found for the selected Tanker'));
    //                 }
    //             }
    //         });
    //     } else {
    //         frm.set_value('tank_balance', '');
    //     }
    //     refresh_fields();
    // },
    tanker: function (frm) {
        if (frm.doc.tanker) {
            frappe.call({
                method: "erpnext.fleet_management.doctype.pol_issue.pol_issue.get_equipment_data",
                args: {
                    tanker: frm.doc.tanker,
                    branch: frm.doc.branch,
                    pol_type: frm.doc.pol_type,
                },
                callback: function (response) {
                    if (response.message) {
                        frm.set_value('tank_balance', response.message);
                    } else {
                        frappe.msgprint(__('No data found for the selected Tanker'));
                    }
                }
            });
        } else {
            frm.set_value('tank_balance', '');
        }
    },
    issue_from: function (frm) {
        if (frm.doc.issue_from === "Fuelbook") {
            frm.set_df_property("fuel_book", "hidden", 0);
            frm.set_df_property("fuel_book", "reqd", 1);

        } else {
            // For any other Event Type
            frm.set_df_property("fuel_book", "hidden", 1);
            frm.set_df_property("fuel_book", "reqd", 0);
        }

    },


    "items_on_form_rendered": function (frm, grid_row, cdt, cdn) {
        var row = cur_frm.open_grid_row();
    },
});

frappe.ui.form.on("POL Issue", "refresh", function (frm) {
    cur_frm.set_query("pol_type", function () {
        return {
            "filters": {
                "disabled": 0,
                "is_pol_item": 1
            }
        };
    });

    cur_frm.set_query("warehouse", function () {
        return {
            query: "erpnext.controllers.queries.filter_branch_wh",
            filters: { 'branch': frm.doc.branch }
        }
    });

    frm.fields_dict['items'].grid.get_field('equipment_warehouse').get_query = function (doc, cdt, cdn) {
        item = locals[cdt][cdn]
        return {
            "query": "erpnext.controllers.queries.filter_branch_wh",
            filters: { 'branch': item.equipment_branch }
        }
    }

    frm.fields_dict['items'].grid.get_field('hiring_warehouse').get_query = function (doc, cdt, cdn) {
        item = locals[cdt][cdn]
        return {
            "query": "erpnext.controllers.queries.filter_branch_wh",
            filters: { 'branch': item.hiring_branch }
        }
    }

    frm.fields_dict['items'].grid.get_field('equipment').get_query = function (doc, cdt, cdn) {
        doc = locals[cdt][cdn]

        return {
            filters: {
                "is_disabled": 0,
                "equipment_type": ["not in", ['Skid Tank', 'Barrel']]
            }
        }
    }

})
