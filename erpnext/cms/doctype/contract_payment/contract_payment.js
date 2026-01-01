// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract Payment", {
	refresh(frm) {		
	},
	exchange_rate: function (frm) {
		calc_payable_btn(frm);
		calc_deductions_and_net(frm);
	},
	bill_amount_in_currency: function (frm) {
		calc_payable_btn(frm);
		calc_deductions_and_net(frm);
	},
	payable_amount: calc_deductions_and_net,
	advance: calc_deductions_and_net,
	tds: calc_deductions_and_net,
	retention_money: calc_deductions_and_net,
	ld: calc_deductions_and_net,
});

function calc_deductions_and_net(frm) {
	const payable = flt(frm.doc.payable_amount);
	const advance = flt(frm.doc.advance);
	const tds = flt(frm.doc.tds);
	const retention = flt(frm.doc.retention_money);
	const ld = flt(frm.doc.ld);

	const total_deduction = advance + tds + retention + ld;
	frm.set_value("total_deduction", total_deduction);

	const net_amount = payable - total_deduction;
	frm.set_value("net_amount_payable", net_amount);
}

function calc_payable_btn(frm) {
	const rate = flt(frm.doc.exchange_rate);
	const bill_ccy = flt(frm.doc.bill_amount_in_currency);
	const payable_btn = rate && bill_ccy ? (rate * bill_ccy) : 0;
	frm.set_value("payable_amount", payable_btn);
}
