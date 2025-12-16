// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Price Costing", {
	refresh(frm) {
        
	},
    onload: function (frm) {
        if (!frm.doc.psoting_date) {
            frm.set_value('posting_date', frappe.datetime.get_today())
        }
    }
});

frappe.ui.form.on("Price Costing Item", {
    // item_code: calculate_landed_cost,
    // source_rate: calculate_landed_cost,
    // insurance: calculate_landed_cost,
    // frieght: calculate_landed_cost,
    // gst: calculate_landed_cost,
    // custom_duty: calculate_landed_cost,
    // excise_duty: calculate_landed_cost,
    // service_charges: calculate_landed_cost,
    // transportation_charges: calculate_landed_cost,
    // clearing_and_forwarding_charges: calculate_landed_cost,
    // bank_charges: calculate_landed_cost,
    // labour_charges: calculate_landed_cost,
    // processing_percent: function(frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if(row.landed_cost){
    //         processing_amount = row.landed_cost * (row.processing_percent/100)
    //         frappe.model.set_value(cdt, cdn, 'processing_amount', processing_amount);
    //     }
    // },
    // bank_charges_percent: function(frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if(row.landed_cost){
    //         bank_charges_amount = row.landed_cost * (row.bank_charges_percent/100)
    //         frappe.model.set_value(cdt, cdn, 'bank_charges_amount', bank_charges_amount);
    //     }
    // },
    // stock_holding_percent: function(frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if(row.landed_cost){
    //         stock_holding_amount = row.landed_cost * (row.stock_holding_percent/100)
    //         frappe.model.set_value(cdt, cdn, 'stock_holding_amount', stock_holding_amount);
    //     }
    // },
    // margin_percent: function(frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if(row.landed_cost){
    //         margin_amount = row.landed_cost * (row.margin_percent/100)
    //         frappe.model.set_value(cdt, cdn, 'margin_amount', margin_amount);
    //     }
    // },
});

// function calculate_landed_cost(frm, cdt, cdn) {
//     var row = locals[cdt][cdn];
//     let total = flt(row.source_rate) +
//         flt(row.insurance) +
//         flt(row.frieght) +
//         flt(row.gst) +
//         flt(row.custom_duty) +
//         flt(row.excise_duty) +
//         flt(row.service_charges) +
//         flt(row.clearing_and_forwarding_charges) +
//         flt(row.bank_charges) +
//         flt(row.transportation_charges) +
//         flt(row.labour_charges);

//     frappe.model.set_value(cdt, cdn, 'landed_cost', total);
// }
