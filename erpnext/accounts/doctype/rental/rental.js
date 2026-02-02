frappe.ui.form.on("Rental", {
    refresh: function (frm) {

        if (frm.doc.docstatus == 1) {
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

});
frappe.ui.form.on("Rental Details", {
    night_halt: function (frm, cdt, cdn) {
        calculate_rental_row(frm, cdt, cdn);
        update_total_amount(frm);
    },
    rate: function (frm, cdt, cdn) {
        calculate_rental_row(frm, cdt, cdn);
        update_total_amount(frm);
    },

});

function calculate_rental_row(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);

    let nights = row.night_halt || 0;
    let rate = row.rate || 0;

    let total = nights * rate;

    frappe.model.set_value(cdt, cdn, "amount", total);
    frm.refresh_field("rental_details");
}
function update_total_amount(frm) {
    let total = 0;
    frm.doc.rental_details.forEach(row => {
        total += row.amount || 0;
    });

    frm.set_value("total_amount", total);
    frm.refresh_field("total_amount");
    calculate_gst_amount(frm);
}
