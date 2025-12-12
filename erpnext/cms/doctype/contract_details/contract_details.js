// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract Details", {
    start_date(frm) {
        validate_dates(frm);
    },
    end_date(frm) {
        validate_dates(frm);
    },
    initial_amount(frm) {
        calculate_final_amount(frm);
    },
    discount(frm) {
        calculate_final_amount(frm);
    },
    additional(frm) {
        calculate_final_amount(frm);
    }
});

function validate_dates(frm) {
    const start = frm.doc.start_date;
    const end = frm.doc.end_date;

    if (start && end) {
        if (moment(start).isAfter(end)) {
            frappe.msgprint("Start Date cannot be greater than End Date.");
            frm.set_value("start_date", "");
        }
    }
}
function calculate_final_amount(frm) {
    const initial = flt(frm.doc.initial_amount);
    const discount = flt(frm.doc.discount);
    const additional = flt(frm.doc.additional);

    let final = initial;
    if (discount) {
        final = initial - discount;
    }
    if (additional) {
        final = final + additional;
    }
    frm.set_value("final_amount", final);
}




