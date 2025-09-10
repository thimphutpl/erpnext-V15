// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transporter Invoice", {
	refresh(frm) {
        if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Ledger'), function(){
				frappe.route_options = {
						voucher_no: frm.doc.name,
						from_date: frm.doc.posting_date,
						to_date: frm.doc.posting_date,
						company: frm.doc.company,
						group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			},__('View'));
			if (!frm.doc.journal_entry){
				cur_frm.add_custom_button(__('Make Journal Entry'), function(doc) {
					frm.events.make_journal_entry(frm)
				},__('Create'))
			}
			// cur_frm.page.set_inner_btn_group_as_primary(__('Create'));
			// cur_frm.page.set_inner_btn_group_as_primary(__('View'));
		}
	},
    make_journal_entry:function(frm){
		frappe.call({
			method:"post_journal_entry",
			doc : frm.doc,
			callback: function (r) {
				
			},
		});
	},
});
