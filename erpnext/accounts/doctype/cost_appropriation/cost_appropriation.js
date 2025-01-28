// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cost Appropriation", {
	get_details: function(frm) {
		return frappe.call({
			method: "get_details",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
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

	cost_type: function(frm){
		switch(frm.doc.cost_type){
			case "Hire Charge": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'hire_charge',
					function(d) {
						frm.set_value("account",d.hire_charge);
					});
				break;
			case "HSD": frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'hsd',
				function(d) {
					frm.set_value("account",d.hsd);
				});
				break;
			case "Lubricant": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'lubricant',
				function(d) {
						frm.set_value("account",d.lubricant);
				});
				break;
			case "Operator Allowance": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'operator_allowance',
				function(d) {
					frm.set_value("account",d.operator_allowance);
				});
				break;
			case "OAP Salary": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'oap_salary',
				function(d) {
					frm.set_value("account",d.oap_salary);
				});
				break;
			case "GCE": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'gce',
				function(d) {
					frm.set_value("account",d.gce);
				});
				break;
			case "Overtime Payment": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'overtime_payment',
				function(d) {
					frm.set_value("account",d.overtime_payment);
				});
				break;
			case "Muster Roll Employee": 
				frappe.model.get_single_value('Company','muster_roll_employee',
				function(d) {
					frm.set_value("account",d.muster_roll_employee);
				});
				break;
			case "Thai Salary": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'thai_salary',
					function(d) {
						frm.set_value("account",d.thai_salary);
					});
				break;
			case "DFG Soelra": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'dfg_soelra',
				function(d) {
					frm.set_value("account",d.dfg_soelra);
				});
				break;
			case "Indian Operators Salary": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'indian_operators_salary',
				function(d) {
					frm.set_value("account",d.indian_operators_salary);
				});
				break;
			case "Repair and Maintenance": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'repair_and_maintenance',
				function(d) {
					frm.set_value("account",d.repair_and_maintenance);
				});
				break;
			case "OJT": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'ojt',
				function(d) {
					 frm.set_value("account",d.ojt);
				});
				break;
			case "Contract Employee": 
				frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'contract_employee',
				function(d) {
					frm.set_value("account",d.contract_employee);
				});
				break;
			default:
				break;
		}
	}
});