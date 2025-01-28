// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
erpnext.buying.setup_buying_controller();
frappe.ui.form.on('Imprest Recoup', {
	onload: function(frm){
		frm.set_query('item_code', 'items', function() {
			return {
				filters: [
					["is_fixed_asset", "=", 0]
				]
			};
		});
	},
	refresh: function(frm) {
		// enable_disable(frm);
		if(frm.doc.docstatus===1){
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company
				};
				frappe.set_route("query-report", "Stock Ledger Report");
			}, __("View"));
			frm.add_custom_button(__('Accounting Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					company: frm.doc.company,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					group_by_voucher: false
				};
			frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		}
	},
});

frappe.ui.form.on("Imprest Recoup Item", {
	quantity: function (frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		frappe.model.set_value(cdt, cdn, "amount", flt(row.quantity)*flt(row.rate));
	},
	rate: function (frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		frappe.model.set_value(cdt, cdn, "amount", flt(row.quantity)*flt(row.rate));
	},
})



