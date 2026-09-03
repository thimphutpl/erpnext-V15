frappe.ui.form.on("Advance", {
    setup: function(frm) {
        frm.set_query("branch", function() {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
        frm.set_query("budget_activity","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
         frm.set_query("budget_sub_activity","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
        frm.set_query("retention","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
         frm.set_query("tds","advance_details",function(){
            return{
                 filters: {
                    company: frm.doc.company
                }

            }
        })
    },

 
    company:function(frm){
        if (!frm.doc.company){
            frm.set_value("branch","")
        }

    },
    
    party_type: function (frm) {
        toggle_party_field(frm);
    },
    


    
});


frappe.ui.form.on("Advance Item", {

    apply_tds: function(frm, cdt, cdn) {
        toggle_tds(frm, cdt, cdn);
    },
    apply_retention: function(frm, cdt, cdn) {
        toggle_retention(frm, cdt, cdn);
    },

    opening_balance: function(frm, cdt, cdn) {
        calculate_tds(frm, cdt, cdn);
        calculate_net_amount(frm, cdt, cdn);
    },
    tds_rate: function(frm, cdt, cdn) {
        calculate_tds(frm, cdt, cdn);
     
    },

    retention_rate: function(frm, cdt, cdn) {
        calculate_retention(frm, cdt, cdn);
  
    },
    retention: function(frm, cdt, cdn) {
        calculate_retention(frm, cdt, cdn);
    },
    tds_amount: function(frm, cdt, cdn) {
        calculate_net_amount(frm, cdt, cdn);
    },
    retention_amount: function(frm, cdt, cdn) {
        calculate_net_amount(frm, cdt, cdn);
    },


    tds: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.tds) {
            frappe.model.set_value(cdt, cdn, "tds_account", "");
            frappe.model.set_value(cdt, cdn, "tds_rate", 0);
            frappe.model.set_value(cdt, cdn, "tds_amount", 0);
            return;
        }

        frappe.call({
            method: "erpnext.accounts.doctype.advance.advance.tax_account",
            args: {
                name: row.tds,
                company: frm.doc.company
            },
            callback: function(r) {
                if (r.message) {
                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "tds_account",
                        r.message.account
                    );

                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "tds_rate",
                        r.message.tax_withholding_rate
                    );
                }
            }
        });
        calculate_tds(frm, cdt, cdn);
    },

    form_render: function(frm, cdt, cdn) {
        toggle_tds(frm, cdt, cdn);
        toggle_retention(frm, cdt, cdn);
    }
});



function toggle_tds(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let grid_row = frm.fields_dict.advance_details.grid.grid_rows_by_docname[cdn];

    if (!grid_row) {
        return;
    }

    if (row.apply_tds) {
        grid_row.toggle_reqd("tds_account", true);
        grid_row.toggle_reqd("tds", true);
        grid_row.toggle_reqd("tds_rate", true);
        grid_row.toggle_reqd("tds_amount", true);
    
        grid_row.toggle_display("tds_account",true)
        grid_row.toggle_display("tds", true);
        grid_row.toggle_display("tds_rate", true);
        grid_row.toggle_display("tds_amount", true);

    } else {

        grid_row.toggle_reqd("tds_account", false);
        grid_row.toggle_reqd("tds", false);
        grid_row.toggle_reqd("tds_rate", false);
        grid_row.toggle_reqd("tds_amount", false);

        grid_row.toggle_display("tds_account",false)
        grid_row.toggle_display("tds", false);
        grid_row.toggle_display("tds_rate", false);
        grid_row.toggle_display("tds_amount", false);

        frappe.model.set_value(cdt, cdn, "tds", "");
        frappe.model.set_value(cdt, cdn, "tds_rate", 0);
        frappe.model.set_value(cdt, cdn, "tds_amount", 0);
          frappe.model.set_value(cdt, cdn, "tds_account","");
    }
}


function toggle_retention(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let grid_row = frm.fields_dict.advance_details.grid.grid_rows_by_docname[cdn];

    if (!grid_row) {
        return;
    }

    if (row.apply_retention) {

        grid_row.toggle_reqd("retention",true)
        grid_row.toggle_reqd("retention_account", true);
        grid_row.toggle_reqd("retention_rate", true);
        grid_row.toggle_reqd("retention_amount", true);
        grid_row.toggle_display("retention",true)
        grid_row.toggle_display("retention_account", true);
        grid_row.toggle_display("retention_rate", true);
        grid_row.toggle_display("retention_amount", true);

    } else {


        grid_row.toggle_reqd("retention",false)
        grid_row.toggle_reqd("retention_account", false);
        grid_row.toggle_reqd("retention_rate", false);
        grid_row.toggle_reqd("retention_amount", false);
        grid_row.toggle_display("retention", false);
        grid_row.toggle_display("retention_account", false);
        grid_row.toggle_display("retention_rate", false);
        grid_row.toggle_display("retention_amount", false);

        frappe.model.set_value(cdt, cdn, "retention", "");
        frappe.model.set_value(cdt, cdn, "retention_rate", 0);
        frappe.model.set_value(cdt, cdn, "retention_account", 0);
        frappe.model.set_value(cdt, cdn, "retention_account", "");
    }
}



function toggle_party_field(frm) {
    if (!frm.doc.party_type) {
        frm.set_df_property("customer", "hidden", 1);
        frm.set_df_property("advance_type", "hidden", 1);
        frm.set_df_property("advance_type", "reqd", 0);
        frm.set_df_property("customer", "reqd", 0);
        frm.set_value("customer", "");
    } else {
        frm.set_df_property("customer", "hidden", 0);
        frm.set_df_property("advance_type", "hidden", 0);
        frm.set_df_property("customer", "reqd", 1);
        frm.set_df_property("advance_type", "reqd", 1);
    }

    frm.set_query("advance_type", function() {
        return {
            filters: {
                company: frm.doc.company
                // party_type: frm.doc.party_type
            }
        };
    });
}

function calculate_tds(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.apply_tds || !row.opening_balance || !row.tds_rate) {
        frappe.model.set_value(cdt, cdn, "tds_amount", 0);
        return;
    }

    let opening_balance = flt(row.opening_balance);
    let tds_rate = flt(row.tds_rate);

    let tds_amount = opening_balance * tds_rate / 100;

    frappe.model.set_value(
        cdt,
        cdn,
        "tds_amount",
        tds_amount
    );
}

function calculate_retention(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (!row.apply_tds || !row.opening_balance || !row.retention_rate) {
        frappe.model.set_value(cdt, cdn, "retention_amount", 0);
        return;
    }

    let opening_balance = flt(row.opening_balance);
    let retention_rate = flt(row.retention_rate);

    let retention_amount = opening_balance * retention_rate / 100;

    frappe.model.set_value(
        cdt,
        cdn,
        "retention_amount",
        retention_amount
    );
}

function calculate_net_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    let net_amount =
        flt(row.opening_balance) -
        flt(row.tds_amount) -
        flt(row.retention_amount);

    frappe.model.set_value(
        cdt,
        cdn,
        "amount",
        net_amount
    );
}