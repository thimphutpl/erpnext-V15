// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Daily Sales Record", {
	ug_tank(frm) {
        if(frm.doc.ug_tank){
            frappe.call({
                method: "get_item_rate",
                doc: frm.doc,
                callback: function(r){
                    if(r.message){
                        frm.set_value("rate", r.message);
                        frm.refresh_field("rate");
                        frm.refresh_field("item_code")
                    }
                }
            })
        }
	},
    posting_date(frm){
        if(frm.doc.item_code){
            frappe.call({
                method: "get_item_rate",
                doc: frm.doc,
                callback: function(r){
                    if(r.message){
                        frm.set_value("rate", r.message);
                        frm.refresh_field("rate");
                    }
                }
            })
        }
    },    
    quantity_sold(frm){
        frm.set_value("amount", flt(flt(frm.doc.rate) * flt(frm.doc.quantity_sold),2))
        calculate_totals(frm);
        frm.refresh_field("amount");
    },
    amount(frm){
        calculate_totals(frm);
    }
});

frappe.ui.form.on("Bill Sales Items", {
    quantity(frm, cdt, cdn){
        var row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, "amount", flt(row.quantity*frm.doc.rate,2))
        calculate_totals(frm);
    },
    amount(frm){
        calculate_totals(frm);
    }
});
var calculate_totals = function(frm){
    frappe.call({
        method: "calculate_totals",
        doc: frm.doc,
        callback: function(r){
            if(r.message){
                frm.set_value("bill_sales_quantity", r.message[0]);
                frm.set_value("bill_sales_amount", r.message[1]);
                frm.set_value("total_quantity_sold", flt(r.message[0]+frm.doc.quantity_sold,2));
                frm.set_value("total_amount", flt(r.message[1]+frm.doc.amount,2));
                frm.refresh_field("bill_sales_quantity");
                frm.refresh_field("bill_sales_amount");
                frm.refresh_field("total_quantity_sold");
                frm.refresh_field("total_amount");
            }
        }
    })
}