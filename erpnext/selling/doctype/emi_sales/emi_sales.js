// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// {% include 'erpnext/selling/sales_common.js' %};
// cur_frm.add_fetch('branch','cost_center','cost_center');
frappe.ui.form.on('EMI Sales', {
	set_price_date_manually:(frm)=>{
		frm.set_df_property('pricing_date', 'reqd', frm.doc.set_price_date_manually == 1)
	},
	customer_group:(frm)=>{
		// toggle_views(frm);
		if(cur_frm.doc.sales_order_type!="External Customers"){
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': cur_frm.doc.branch,
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
		else{
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': "",
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
		// frm.fields_dict.items.grid.toggle_reqd("commission_account", frm.doc.required_commission)
		frm.fields_dict.items.grid.toggle_reqd("tds_account", frm.doc.required_commission)
		frm.fields_dict.items.grid.toggle_reqd("discount_account", frm.doc.is_discounted)
		// frm.toggle_display('is_on_credit', frm.doc.sales_order_type == "External Customers" || frm.doc.sales_order_type == "Employee Installment" || frm.doc.customer_type == "Employee");
		frappe.call({
			method:'get_payment_type',
			doc:frm.doc,
			callback:(r)=>{
				if(r.message){
					frm.set_value("payment_type", r.message);
					frm.refresh_fields();
				}

			}
		})
		if (frm.doc.customer_group && frm.doc.sales_order_type){
			frm.set_query('payment_type',(doc)=>{
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.get_payment_type",
					filters: {
						'customer_group': frm.doc.customer_group,
						'sales_order_type': frm.doc.sales_order_type,
						'is_on_credit':frm.doc.is_on_credit
					}
				};
			})
		}
		frm.refresh_fields();
	},
	onload:(frm, cdt, cdn )=>{
		if(frappe.session.user!="Administrator" && frm.doc.outstanding_amount == 0 && frm.doc.status != "Received"){
			frappe.call({
				method:"set_status",
				args: {"update": true},
				doc: frm.doc,
				callback: function(r){
	
				}
			})
		}
		var d = locals[cdt][cdn]
		frm.set_query('debit_account', function(doc) {
			return {
				filters: {
					"is_group": 0,
					"company": doc.company,
					"account_type":'Receivable',
					"disabled":0
				}
			};
		});
		if ( !frm.doc.__islocal || frm.doc.docstatus == 1 || frappe.session.user == 'Administrator') return

		// frappe.call({
		// 	method:'frappe.client.get_value',
		// 	args: {
		// 		doctype: 'Employee',
		// 		filters: {
		// 			'user_id': frappe.session.user
		// 		},
		// 		fieldname: ['branch']
		// 	},
		// 	callback: function(r){
		// 		if(r.message){
		// 			frm.set_value('branch',r.message.branch)
		// 			frm.refresh_field('branch')
		// 		}
		// 	}
		// })
	},
	no_of_installation_external:(frm)=>{
		if(frm.doc.no_of_installation){
			frm.doc.items.forEach(ele => {
				ele.total_data_package = flt(ele.data_package) * frm.doc.no_of_installation_external
			});
		}
		else{
			frm.doc.items.forEach(ele => {
				ele.total_data_package = 0
			});
		}
		frm.refresh_field("items")

	},
	no_of_installation_employee:(frm)=>{
		if(frm.doc.no_of_installation){
			frm.doc.items.forEach(ele => {
				ele.total_data_package = flt(ele.data_package) * frm.doc.no_of_installation
			});
		}
		else{
			frm.doc.items.forEach(ele => {
				ele.total_data_package = 0
			});
		}
		frm.refresh_field("items")

	},
	customer:(frm)=>{
		frm.set_query("sales_order_type", function() {
			return {
				query: "erpnext.selling.doctype.emi_sales.emi_sales.get_sales_order",
				filters: {
					'customer_group': cur_frm.doc.customer_group,
					'customer_type':cur_frm.doc.customer_type,
					'customer': cur_frm.doc.customer,
				}
			};
		});
		frappe.call({
			method:'get_customer_details',
			doc:cur_frm.doc,
			callback:(r)=>{
				frm.set_value("interest_percentage", r.message)
				frm.refresh_field('customer_name')
				frm.refresh_field('customer_group')
				// frm.refresh_field('location_segregation')
				frm.refresh_field('purchase_limit_on_total_amount')
				frm.set_df_property('one_time_customer_name', 'reqd', frm.doc.customer_group == "One Time Customer")
				frm.set_df_property('contact', 'reqd', frm.doc.customer_group == "One Time Customer")
				frm.set_df_property('cid_passort_work_permit_no', 'reqd', frm.doc.customer_group == "One Time Customer")
			}
		})
		// toggle_views(frm);
		frm.set_value('required_commission',null)
	},
	refresh:(frm)=>{
		var customer_group = ''
		var sales_order_type = ''

		if(frm.doc.customer_group){
			customer_group = frm.doc.customer_group
		}
		// frm.toggle_display('is_on_credit', frm.doc.sales_order_type == "External Customers" || frm.doc.sales_order_type == "Employee Installment");
		if(frm.doc.sales_order_type){
			sales_order_type = frm.doc.sales_order_type
		}
		// toggle_views(frm);
		frm.set_query('payment_type',(doc)=>{
			return {
				query: "erpnext.selling.doctype.emi_sales.emi_sales.get_payment_type",
				filters: {
					'customer_group': customer_group,
					'sales_order_type': sales_order_type,
					'is_on_credit':frm.doc.is_on_credit
				}
			};
		})
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Stock Ledger Report'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
				};
				frappe.set_route("query-report", "Stock Ledger Report");
			},
			__("View"));
			if(frm.doc.payment_type == "External Customers"){
				frm.add_custom_button(__('Installment Entries'), function () {
					frappe.route_options = {
						"Journal Entry Account.reference_type": me.frm.doc.doctype,
						"Journal Entry Account.reference_name": me.frm.doc.name,
					};
					frappe.set_route("List", "Journal Entry");
				}, __("View"));
			}
			else if(frm.doc.payment_type == "Employee Installment"){
				frm.add_custom_button(__('Installment Deducted in Salary Slip'), function () {
					frappe.route_options = {
						"Salary Detail.salary_component": frm.doc.doctype,
						"Salary Detail.reference_number": frm.doc.name,
					};
					frappe.set_route("List", "Salary Slip");
				}, __("View"));
			}
			frm.add_custom_button(__('Post Accounting Entry'), function(){
				frappe.call({
					method:'post_accounting_entry',
					doc:cur_frm.doc,
					callback:(r)=>{
						
					}
				})
			},
			__("View"));
			frm.add_custom_button(__('General Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
				};
				frappe.set_route("query-report", "General Ledger");
			},
			__("View"));
			cur_frm.page.set_inner_btn_group_as_primary(__('View'))
			if ((frm.doc.is_on_credit || frm.doc.is_opening_bal)  && frm.doc.status!= 'Received' && frm.doc.docstatus == 1 && frm.doc.payment_type != "External Customers" && frm.doc.sales_order_type != "Employee Installment"){
				frm.add_custom_button(__('Make Payment'), (doc)=>{
					frappe.call({
						method: 'erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry',
						args: {
							"dt": cur_frm.doc.doctype,
							"dn": cur_frm.doc.name
						},
						callback: function(r) {
							var doclist = frappe.model.sync(r.message);
							frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
						}
					});
				},__("Create"))
				if ( frm.doc.credit_type == 'Due Date Payment'){
					frm.add_custom_button(__('Extend Due Date'),(doc)=>{
						let d = frappe.prompt([
							{
								label: 'Cureent Due Date',
								fieldname: 'current_due_date',
								fieldtype: 'Date',
								default:frm.doc.due_date,
								read_only:1
							},
							{
							label: 'Next Due Date',
							fieldname: 'next_due_date',
							fieldtype: 'Date',
							reqd:1
							}
						], (values) => {
							frappe.call({
								method:'erpnext.selling.doctype.emi_sales.emi_sales.extend_due_date',
								args:{
									"next_due_date":values.next_due_date,
									"doc_type":frm.doc.doctype,
									"name":frm.doc.name
								},
								callback:(r)=>{

									if (r.message){
										frappe.msgprint({
											title: __('Notification'),
											indicator: 'green',
											message: __('Due Date extend successful')
										});
										cur_frm.reload_doc();
									}
								},
								freeze: true,
        						freeze_message: "Updating Due Date.... Please Wait",
							})
						})
					},__("Create"))
				}

				// if(frm.doc.credit_type == "Installment Payment" && frm.doc.no_of_installation > 0){

				// }
	
				cur_frm.page.set_inner_btn_group_as_primary(__('Create'))
			}
			else if ((frm.doc.is_on_credit || frm.doc.is_opening_bal)  && frm.doc.status!= 'Received' && frm.doc.docstatus == 1 && frm.doc.payment_type == "External Customers"){
				frappe.call({
					method: "check_balance",
					doc: frm.doc,
					callback: function(r){
						if(r.message[0]==1){
							frm.add_custom_button(__('Installment Journal Entries'),()=> make_installment_je(frm, 0, r.message[2]),__('Create'));
						}
						// if(r.message[1]==1){
						// 	frm.add_custom_button(__('Remaining Full Payment Journal Entries'),()=> make_installment_je(frm, 1),__('Create'));
						// }
					}
				})
			}
			if (frm.doc.sales_order_type == 'Cost Sharing Installment'  && frm.doc.docstatus == 1 && !frm.doc.asset_code){
				cur_frm.add_custom_button(__('Asset Issue Entry'),()=> make_asset_issue_entry(frm), __('Create'));
			}

			// else if ((frm.doc.is_on_credit || frm.doc.is_opening_bal)  && frm.doc.status!= 'Received' && frm.doc.docstatus == 1 && frm.doc.payment_type == "Employee Installment"){
			// 	frappe.call({
			// 		method: "check_balance",
			// 		doc: frm.doc,
			// 		callback: function(r){
			// 			if(r.message[0]==1){
			// 				frm.add_custom_button(__('Installment Payment Entries'),()=> make_installment_pe(frm, 0, r.message[2]),__('Create'));
			// 				// frm.add_custom_button(__('Installment Prepaid Journal Entries'),()=> make_installment_je_prepaid(frm, 0, r.message[2]),__('Create'));
			// 			}
			// 			// if(r.message[1]==1){
			// 			// 	frm.add_custom_button(__('Remaining Full Payment Journal Entries'),()=> make_installment_je(frm, 1),__('Create'));
			// 			// }
			// 		}
			// 	})
			// }
		}
		if ((frm.doc.is_on_credit || frm.doc.is_opening_bal) && frm.doc.docstatus == 1 && frm.doc.payment_type == "External Customers"){
			frappe.call({
				method: "check_balance",
				doc: frm.doc,
				callback: function(r){
					if(r.message[3] == 1){
						frm.add_custom_button(__('Installment Prepaid Journal Entries'),()=> make_installment_je_prepaid(frm, 0, r.message[2]),__('Create'));
					}
					// if(r.message[1]==1){
					// 	frm.add_custom_button(__('Remaining Full Payment Journal Entries'),()=> make_installment_je(frm, 1),__('Create'));
					// }
				}
			})
		}
		if (frm.doc.docstatus == 1 ) frm.set_df_property('due_date','read_only',1)
	},
	branch:(frm)=>{
		frappe.call({
			method:'fetch_warehouse',
			doc:frm.doc,
			callback:(r)=>{
				frm.refresh_field('delivery_warehouse')
			}
		})
		frm.set_query("delivery_warehouse", function() {
			return {
				query: "erpnext.selling.doctype.emi_sales.emi_sales.get_warehouse",
				filters: {
					'branch': frm.doc.branch
				}
			};
		});
		if(cur_frm.doc.sales_order_type!="External Customers"){
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': cur_frm.doc.branch,
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
		else{
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': "",
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
	},
	customer_type:(frm)=>{
		if(cur_frm.doc.sales_order_type!="External Customers"){
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': cur_frm.doc.branch,
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
		else{
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': "",
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
		frm.set_df_property('no_of_installation_employee','reqd', frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && (frm.doc.sales_order_type == "Employee Installment" || frm.doc.sales_order_type == "Cost Sharing Installment") ?1:0)
		// frm.set_df_property('no_of_installation_external','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Customer" ?1:0)
		frm.set_value('customer','')
		frm.set_value('customer_name','')
		frm.set_value('sales_order_type','')
	},
	is_on_credit:(frm, cdt, cdn )=>{
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Company',
				filters: {
					'company_name': frm.doc.company
				},
				fieldname: ['default_expense_account','default_cash_account','default_receivable_account']
			},
			callback: function(r){
				if(r.message){
					if (frm.doc.is_on_credit || frm.doc.is_opening_bal){
						frm.doc.items.map(v=> v.cash_bank_account = r.message.default_receivable_account)
							frm.set_value('debit_to',r.message.default_receivable_account)
						frm.refresh_field("items")
					}
					else {
						frm.doc.items.map(v=> v.cash_bank_account = r.message.default_cash_account)
						frm.refresh_field("items")
					}
				}
			}
		});
		frm.set_df_property('credit_type','reqd',frm.doc.is_on_credit?1:0)
		// if (frm.doc.is_on_credit){
		// 	frm.set_query('mode_of_payment',(doc)=>{
		// 		return {
		// 			filters: {
		// 				'name':'Credit'
		// 			}
		// 		};
		// 	})
		// }else{
		// 	frm.set_query('mode_of_payment',(doc)=>{
		// 		return {
		// 			filters: {
		// 				'name':('!=','Credit')
		// 			}
		// 		};
		// 	})
		// }
		frappe.call({
			method:'get_payment_type',
			doc:frm.doc,
			callback:(r)=>{
				if(r.message){
					frm.set_value("payment_type", r.message);
					frm.refresh_fields();
				}
			}
		})
	},
	credit_type:(frm)=>{
		// frm.set_df_property('no_of_installation','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && frm.doc.sales_order_type!= "Employee Installment" ?1:0)
		frm.set_df_property('no_of_installation_employee','reqd', frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && (frm.doc.sales_order_type == "Employee Installment" || frm.doc.sales_order_type == "Cost Sharing Installment") ?1:0)
		// frm.set_df_property('no_of_installation_external','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Customer" ?1:0)
		frm.set_df_property('due_date','reqd',frm.doc.credit_type == 'Due Date Payment'?1:0)
		frm.set_df_property('due_date','read_only',frm.doc.credit_type == 'Due Date Payment'?0:1)
		frm.set_df_property('payment_type','reqd',frm.doc.credit_type == 'Installment Payment'?1:0)
		filter_payment_type(frm);
	},
	payment_type: (frm)=>{
		// frm.set_df_property('no_of_installation','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && frm.doc.sales_order_type != "Employee Installment" ?1:0)
		frm.set_df_property('no_of_installation_employee','reqd', frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && (frm.doc.sales_order_type == "Employee Installment" || frm.doc.sales_order_type == "Cost Sharing Installment") ?1:0)
		toggle_views(frm);
		// frm.set_df_property('no_of_installation_external','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Customer" ?1:0)
	},
	is_existing: (frm)=>{
		frm.set_df_property('no_of_installation','reqd', frm.doc.is_existing == 1 ? 1:0)
		toggle_views(frm);
	},
	sales_order_type:(frm)=>{
		frappe.call({
			method:'get_payment_type',
			doc:frm.doc,
			callback:(r)=>{
				frm.set_df_property('payment_type','read_only',frm.doc.payment_type!=undefined)
				if(r.message){
					frm.set_value("payment_type", r.message);
					frm.refresh_fields();
				}
			}
		})
		toggle_views(frm);
		// frm.set_df_property('no_of_installation','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && frm.doc.sales_order_type != "Employee Installment" ?1:0)
		frm.set_df_property('no_of_installation_employee','reqd', frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Employee" && (frm.doc.sales_order_type == "Employee Installment" || frm.doc.sales_order_type == "Cost Sharing Installment") ?1:0)
		// frm.set_df_property('no_of_installation_external','reqd',frm.doc.credit_type == 'Installment Payment' && frm.doc.customer_type == "Customer" ?1:0)
		// frm.set_df_property('one_time_customer_name', 'reqd', frm.doc.customer_group=="One Time Customer")
		if(cur_frm.doc.sales_order_type!="External Customers" && cur_frm.doc.sales_order_type!="Employee Installment"){
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': cur_frm.doc.branch,
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
		else{
			frm.set_query("customer", function() {
				return {
					query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_customer_filter",
					filters: {
						'branch': "",
						'customer_type':cur_frm.doc.customer_type,
						'sales_order_type':cur_frm.doc.sales_order_type,
					}
				};
			});
		}
	},
	down_payment_amount: (frm)=>{
		let quota = 0
		if(frm.doc.sales_order_type == "Cost Sharing Installment"){
			frappe.db.get_value("Employee", frm.doc.customer, "grade", (r)=>{
				frappe.db.get_value("Employee Grade", r.grade, "cost_sharing_quotaamount", (m)=>{
					quota = m.cost_sharing_quotaamount
					frm.doc.items.forEach(function(row) {
						// row is the child table row object
						let cdt = row.doctype;  // child doctype
						let cdn = row.name;     // child docname
						if(frm.doc.down_payment_amount<row.rate-quota){
							frappe.throw("Down Payment Amount cannot be less than Nu."+String(row.rate-quota)+" due to Employee "+frm.doc.customer+" quota amount Nu."+String(quota)+".")
						}
						// now you can use cdt and cdn
						calculate_amount(frm, cdt, cdn)
					});
				})
			})
		}
	}
});
frappe.ui.form.on('EMI Sales Payment Mode',{
	mode_of_payment:(frm,cdt,cdn)=>{
		if(frm.doc.mode_of_payment_items.length == 0 ){
			frappe.model.set_value(cdt, cdn, "amount", frm.doc.total_receivable_amount - frm.doc.down_payment_amount)
		}
		else{
			let total = 0
			for(let i = 0; i < frm.doc.mode_of_payment_items.length - 1 ; i++){
				total += flt(frm.doc.mode_of_payment_items[i].amount)
			}
			// frappe.model.set_value(cdt, cdn, "amount", flt(frm.doc.total_receivable_amount) - total)
			if(frm.doc.sales_order_type != "Cost Sharing Installment"){
				frappe.model.set_value(cdt, cdn, "amount", flt(frm.doc.total_receivable_amount) - flt(frm.doc.down_payment_amount))
			}
			else{
				var rate = 0
				var quota = 0
				frm.doc.items.forEach(function(d) {
					rate = d.rate
				});
				frappe.db.get_value("Employee", frm.doc.customer, "grade", (r)=>{
					frappe.db.get_value("Employee Grade", r.grade, "cost_sharing_quotaamount", (m)=>{
						quota = m.cost_sharing_quotaamount
						if(frm.doc.down_payment_amount>rate-quota){
							frappe.model.set_value(cdt, cdn, "amount", flt((quota*frm.doc.cost_sharing_percentage*0.01)-(frm.doc.down_payment_amount - (rate - quota))));
						}
						else{
							frappe.model.set_value(cdt, cdn, "amount", flt(quota*frm.doc.cost_sharing_percentage*0.01))
						}
					})
				})
			}
		}
		frm.refresh_field('mode_of_payment_items')
	}
})
var toggle_views = function(frm){
	console.log("here"+String(frm.doc.customer_type)+" "+String(frm.doc.payment_type))
	frm.toggle_display('is_on_credit', frm.doc.sales_order_type == "External Customers" || frm.doc.sales_order_type == "Employee Installment" || frm.doc.customer_type == "Employee" || frm.doc.customer_type == "Customer");
	frappe.db.get_value("EMI Sales Type", frm.doc.sales_order_type, "enable_cost_sharing", (r) => {
		if(r && r.enable_cost_sharing == 1){
			frm.toggle_display('cost_sharing_percentage', 1);
			frappe.call({
				method: "frappe.client.get",
				args: {
				  doctype: "EMI Sales Type",
				  name: frm.doc.sales_order_type,
				},
				callback(r) {
					if(r.message){
						let rows = r.message.customer_group; // child table fieldname
						var per = 100
						if(rows?.[0]?.customer_group == frm.doc.customer_group){
							per = rows?.[0]?.cost_sharing_percentage;
						}
						frm.set_value('cost_sharing_percentage',per)
					}
	
				}
			});
		}
		else{
			frm.toggle_display('cost_sharing_percentage', 0);
		}
	});
	frm.toggle_display('no_of_installation_external', frm.doc.sales_order_type == "External Customers")
	frm.toggle_display('no_of_installation_employee', frm.doc.sales_order_type == "Employee Installment" || frm.doc.sales_order_type == "Cost Sharing Installment")
	frm.toggle_display('no_of_installation', frm.doc.is_existing==1)
	if(frm.doc.sales_order_type && frm.doc.docstatus == 0){
		if(frm.doc.sales_order_type == "External Customers" || frm.doc.sales_order_type == "Employee Installment" || frm.doc.payment_type == "Staff Installment"){
			frm.set_value("is_on_credit", 1);
			frm.set_value("credit_type", "Installment Payment");
			frm.refresh_field("credit_type")
		}
		else if (frm.doc.credit_type){
			frm.set_value("is_on_credit", 1);
		}
		else{
			frm.set_value("is_on_credit", 0);
			frm.set_value("credit_type", null);
		}
	}
	console.log(frm.doc.credit_type);
	frm.refresh_fields();
}
var make_installment_je = function(frm, remaining, remaining_installment){
	var d = new frappe.ui.Dialog({
    title: __('Create Installment Journal Entries'),
    fields: [
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "reqd": 1,
        },
        {
            "label": "Mode of Payment",
            "fieldname": "mode_of_payment",
            "fieldtype": "Select",
            "options": ["Cheque", "Cash", "Scan and Pay"],
            "reqd": 1,
        },
        {
            "label": "Cheque No./Journal No./Challan No.",
            "fieldname": "cheque_no",
            "fieldtype": "Data",
        },
        {
            "fieldname": "col_break",
            "fieldtype": "Column Break",
        },
        {
            "label": "No of Installment(s)",
            "fieldname": "no_of_installment",
            "fieldtype": "Int",
            "default": 1,
			"read_only": 1,
            "reqd": 1
        },
        {
            "label": "Remaining Installment(s)",
            "fieldname": "remaining_installments",
            "fieldtype": "Int",
            "default": remaining_installment,
            "read_only": 1
        },
    ],
    primary_action: function() {
        var btn = d.get_primary_btn(); // get the Post button
        btn.prop('disabled', true);    // disable it immediately

        var data = d.get_values();
        
        try {
            if(flt(data.no_of_installment) > flt(data.remaining_installments)){
                frappe.throw("No of Installment(s) cannot be greater than Remaining Number of Installment(s)");
            }
            if(flt(data.no_of_installment) <= 0){
                frappe.throw("No of Installment(s) cannot be less than or equal to 0.");
            }
            if(!data.cheque_no){
                frappe.throw("Cheque No./Journal No. is mandatory.");
            }
        } catch (e) {
            btn.prop('disabled', false); // re-enable button if validation fails
            throw e;
        }

        frappe.call({
            method: "make_installment_je",
            doc: frm.doc,
            args: {
                "installment": data.no_of_installment,
                "cheque_no": data.cheque_no,
                "mode_of_payment": data.mode_of_payment,
                "posting_date": data.posting_date
            },
            callback: function(r){
                window.location.reload();
            },
            error: function() {
                btn.prop('disabled', false); // re-enable button if server call fails
            }
        });
    },
    primary_action_label: __('Post')
});

d.show();

}

var filter_payment_type = function(frm){
	var customer_group = ''
	var sales_order_type = ''

	if(frm.doc.customer_group){
		customer_group = frm.doc.customer_group
	}
	// frm.toggle_display('is_on_credit', frm.doc.sales_order_type == "External Customers" || frm.doc.sales_order_type == "Employee Installment");
	if(frm.doc.sales_order_type){
		sales_order_type = frm.doc.sales_order_type
	}
	// toggle_views(frm);
	frm.set_query('payment_type',(doc)=>{
		return {
			query: "erpnext.selling.doctype.emi_sales.emi_sales.get_payment_type",
			filters: {
				'customer_group': customer_group,
				'sales_order_type': sales_order_type,
				'is_on_credit':frm.doc.is_on_credit
			}
		};
	})
}

var make_asset_issue_entry = function(frm){
	var branch = ""
	var asset_rate = 0
	var item_code = ""
	var item_name = ""
	var asset_category = ""
	var asset_sub_category = ""
	var fixed_asset_account = ""
	var credit_account = ""
	var next_depreciation_date = ""
	var exists = 0
	frappe.call({
		method: "get_asset_details",
		doc: cur_frm.doc,
		async: false,
		callback: function(r){
			if(r.message){
				branch = r.message[0];
				asset_rate = r.message[1];
				item_code = r.message[2];
				item_name = r.message[3];
				asset_category = r.message[4];
				asset_sub_category = r.message[5];
				fixed_asset_account = r.message[6];
				credit_account = r.message[7];
				next_depreciation_date = r.message[8];
				exists = r.message[9];
			}
		}
	})
	if(exists == 0){
		var new_doc = frappe.model.get_new_doc('Asset Issue Details');
		new_doc.branch = branch;
		// new_doc.business_activity = business_activity;
		new_doc.entry_date = new Date().toJSON().slice(0,10).replace(/-/g,'-');
		new_doc.item_code = item_code;
		new_doc.emi_sales = cur_frm.doc.name;
		new_doc.asset_rate = asset_rate
		new_doc.purchase_amount = asset_rate
		new_doc.purchase_date = cur_frm.doc.posting_date
		new_doc.issued_date = cur_frm.doc.posting_date
		new_doc.available_for_use_date = cur_frm.doc.posting_date
		new_doc.company = cur_frm.doc.company
		new_doc.asset_account = fixed_asset_account;
		new_doc.credit_account = credit_account;
		new_doc.issued_to = cur_frm.doc.customer;
		new_doc.qty = 1;
		new_doc.calculate_depreciation = 1;
		new_doc.next_depreciation_date = next_depreciation_date;
		new_doc.amount = cur_frm.doc.grand_total
		frappe.set_route('Form', 'Asset Issue Details', new_doc.name);
	}


}
var make_installment_pe = function(frm, remaining, remaining_installment){
	var d = new frappe.ui.Dialog({
		title: __('Create Installment Payment Entry'),
		fields: [
			{
				"label": "Posting Date",
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"reqd": 1,
			},
			{
				"label": "Mode of Payment",
				"fieldname": "mode_of_payment",
				"fieldtype": "Select",
				"options": ["Cheque", "Cash", "Scan and Pay"],
				"reqd": 1,
			},
			{
				"label": "Cheque No./Journal No./Challan No.",
				"fieldname": "cheque_no",
				"fieldtype": "Data",
			},
			{
				"fieldname": "col_break",
				"fieldtype": "Column Break",
			},
			{
				"label": "No of Installment(s)",
				"fieldname": "no_of_installment",
				"fieldtype": "Int",
				"default": 1,
				"read_only": 1,
				"reqd": 1
			},
			{
				"label": "Remaining Installment(s)",
				"fieldname": "remaining_installments",
				"fieldtype": "Int",
				"default": remaining_installment,
				"read_only": 1
			},
		],
		primary_action: function() {
			var btn = d.get_primary_btn(); // Get the Post button
			btn.prop('disabled', true).text(__('Posting...')); // Disable and show loading text
	
			var data = d.get_values();
	
			try {
				if(flt(data.no_of_installment) > flt(data.remaining_installments)){
					frappe.throw("No of Installment(s) cannot be greater than Remaining Number of Installment(s)");
				}
				if(flt(data.no_of_installment) <= 0){
					frappe.throw("No of Installment(s) cannot be less than or equal to 0.");
				}
				if(!data.cheque_no){
					frappe.throw("Cheque No./Journal No. is mandatory.");
				}
			} catch (e) {
				btn.prop('disabled', false).text(__('Post')); // Re-enable if validation fails
				throw e;
			}
	
			frappe.call({
				method: 'erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry_installment',
				args: {
					"dt": cur_frm.doc.doctype,
					"dn": cur_frm.doc.name,
					"emi_amount": data.no_of_installment * cur_frm.doc.monthly_deduction,
					"cheque_no": data.cheque_no,
					"mode_of_payment": data.mode_of_payment
				},
				callback: function(r) {
					var doclist = frappe.model.sync(r.message);
					frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
				},
				error: function() {
					btn.prop('disabled', false).text(__('Post')); // Re-enable button if call fails
				}
			});
		},
		primary_action_label: __('Post')
	});
	
	d.show();	
}

var make_installment_je_prepaid = function(frm, remaining, remaining_installment){
	var d = new frappe.ui.Dialog({
		title: __('Create Prepaid Installment Journal Entries'),
		fields: [
			{
				"label": "Posting Date",
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"reqd": 1,
			},
			{
				"label": "Mode of Payment",
				"fieldname": "mode_of_payment",
				"fieldtype": "Select",
				"options": ["Cheque", "Cash", "Scan and Pay"],
			},
			{
				"label": "Cheque No./Journal No.",
				"fieldname": "cheque_no",
				"fieldtype": "Data",
			},
			{
				"fieldname": "col_break",
				"fieldtype": "Column Break",
			},
			{
				"label": "No of Installment(s)",
				"fieldname": "no_of_installment",
				"fieldtype": "Int",
				"default": 1, 
				"reqd": 1
			},
			{
				"label": "Remaining Installment(s)",
				"fieldname": "remaining_installments",
				"fieldtype": "Int",
				"default": remaining_installment,
				"read_only": 1
			},
		],
		primary_action: function() {
			var btn = d.get_primary_btn(); // Get the Post button
			btn.prop('disabled', true).text(__('Posting...')); // Disable and show loading
	
			var data = d.get_values();
	
			try {
				if(flt(data.no_of_installment) <= 0){
					frappe.throw("No of Installment(s) cannot be less than or equal to 0.");
				}
				// Uncomment below validations if needed
				// if(data.mode_of_payment == "Cheque" && !data.cheque_no){
				//     frappe.throw("Cheque No./Journal No. is mandatory.")
				// }
				// if(data.mode_of_payment == "Scan and Pay" && !data.cheque_no){
				//     frappe.throw("Cheque No./Journal No. is mandatory.")
				// }
			} catch(e) {
				btn.prop('disabled', false).text(__('Post')); // Re-enable button if validation fails
				throw e;
			}
	
			frappe.call({
				method: "make_installment_je_prepaid",
				doc: frm.doc,
				async: false,
				args: {
					"installment": data.no_of_installment,
					"cheque_no": data.cheque_no,
					"mode_of_payment": data.mode_of_payment,
					"posting_date": data.posting_date
				},
				callback: function(r){
					window.location.reload();
				},
				error: function() {
					btn.prop('disabled', false).text(__('Post')); // Re-enable button if call fails
				}
			});
		},
		primary_action_label: __('Post')
	});
	
	d.show();
	
}
frappe.ui.form.on('EMI Sales Item',{
	is_foc_item:(frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		if (row.is_foc_item){
			row.rate = 0
			frm.refresh_field('items')
			// calculate_commission(frm, cdt, cdn)
			calculate_amount(frm, cdt, cdn)
		}
		frappe.meta.get_docfield("EMI Sales Item","rate",cur_frm.doc.name).read_only = row.is_foc_item?0:1
		frm.refresh_field('items')
	},
	qty:(frm,cdt,cdn)=>{
		// calculate_commission(frm, cdt, cdn)
		calculate_amount(frm, cdt, cdn)
	},
	rate:(frm,cdt,cdn)=>{
		// calculate_commission(frm, cdt, cdn)
		calculate_down_payment(frm, cdt, cdn);
		calculate_amount(frm, cdt, cdn)
	},
	discount_percent:(frm,cdt,cdn)=>{
		calculate_amount(frm, cdt, cdn)
	},
	discount_amount:(frm,cdt,cdn)=>{
		calculate_amount(frm, cdt, cdn)
	},
	form_render:(frm,cdt,cdn)=>{
		var row = locals[cdt][cdn]
		var subgroups = ["Voucher", "Sim"]
		frappe.meta.get_docfield("EMI Sales Item","serial_number",cur_frm.doc.name).reqd = subgroups.includes(row.item_subgroup)? 1 : 0
		frappe.meta.get_docfield("EMI Sales Item","ime_number",cur_frm.doc.name).reqd = row.item_subgroup == 'Mobile Handset' ? 1 : 0
		frappe.meta.get_docfield("EMI Sales Item","rate",cur_frm.doc.name).read_only = row.item_group == 'Services' || row.is_foc_item ? 0 : 1
		frappe.meta.get_docfield("EMI Sales Item","commission_account",cur_frm.doc.name).hidden = !frm.doc.required_commission
		frappe.meta.get_docfield("EMI Sales Item","discount_account",cur_frm.doc.name).hidden = !frm.doc.is_discounted
		frappe.meta.get_docfield("EMI Sales Item","tds_account",cur_frm.doc.name).hidden = !frm.doc.required_commission
		frappe.meta.get_docfield("EMI Sales Item","discount_percent",cur_frm.doc.name).hidden = frm.doc.is_discounted ? 0 : 1
		frappe.meta.get_docfield("EMI Sales Item","discount_amount",cur_frm.doc.name).hidden = frm.doc.is_discounted ? 0 : 1
		frappe.meta.get_docfield("EMI Sales Item","tds_deducted_by_customer",cur_frm.doc.name).read_only = (frm.doc.customer_group == 'One Time Customer' || frm.doc.customer_group == "Regular") ? 0 : 1
		if (frm.doc.is_discounted){
			frappe.meta.get_docfield("EMI Sales Item","discount_percent",cur_frm.doc.name).hidden = frm.doc.is_discounted ? 0 : 1
			frappe.meta.get_docfield("EMI Sales Item","discount_amount",cur_frm.doc.name).hidden = frm.doc.is_discounted ? 0 : 1
		}
		frm.refresh_field('items')
	},
	tds_deducted_by_customer:(frm,cdt,cdn)=>{
		let row = locals[cdt][cdn]
		frappe.call({
			method:'frappe.client.get_value',
			args: {
				doctype: "Accounts Settings", 
				fieldname:"tds_deducted",
			},
			callback:(r)=>{
				row.tds_deducted_by_customer_account = r.message.tds_deducted
				frm.refresh_field('items')
			}
		})
		if(flt(row.tds_deducted_by_customer) > 0 ){
			calculate_amount(frm, cdt, cdn)
		}
	},
	items_add:(frm,cdt,cdn)=>{
		if (!frm.doc.customer){
			frappe.throw('Get customer first to fetch items')
		}
		if (!frm.doc.customer_group && frm.doc.cusotmer){
			frappe.throw('Customer Group not set for '+frm.doc.customer_type+" "+frm.doc.customer)
		}
		cur_frm.fields_dict['items'].grid.get_field('item_code').get_query = function(doc, cdt, cdn) {
			return {
				query: "erpnext.selling.doctype.emi_sales.emi_sales.apply_item_filter",
				filters: {
					'customer_type': doc.customer_type,
					'customer_group':doc.customer_group
				}
			}
		}
		frappe.model.set_value(cdt, cdn, "warehouse", frm.doc.delivery_warehouse)
		frappe.model.set_value(cdt, cdn, "cost_center", frm.doc.cost_center)
	},
	uom: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		var no_of_installation = 0
		if(frm.doc.sales_order_type == "External Customers" && frm.doc.credit_type == "Installment Payment"){
			no_of_installation = frm.doc.no_of_installation_external
		}
		else if(frm.doc.sales_order_type == "Employee Installment" && frm.doc.credit_type == "Installment Payment"){
			no_of_installation = frm.doc.no_of_installation_employee
		}
		else if(frm.doc.sales_order_type != "Employee Installment" && frm.doc.sales_order_type != "External Customers" && frm.doc.credit_type == "Installment Payment"){
			no_of_installation = frm.doc.no_of_installation
		}
		if ( frm.doc.company && frm.doc.branch && d.item_code && frm.doc.posting_date ){			
			frappe.call({
				method: "erpnext.production.doctype.selling_price.selling_price.get_emi_selling_rate",
				args: {
						"branch": frm.doc.branch,
						"item_code": d.item_code,
						"transaction_date": cint(frm.doc.set_price_date_manually) == 1 ? frm.doc.pricing_date : frm.doc.posting_date,
						"selling_uom": d.uom,
						"location": ''
						// "payment_type":frm.doc.payment_type,
						// "no_of_installation": no_of_installation,
				},
				callback: function(r) {
					if (r.message){
						frappe.model.set_value(cdt, cdn, "rate", r.message.selling_price)
						// frappe.model.set_value(cdt, cdn, "selling_price", r.message.name)
						// frappe.model.set_value(cdt, cdn, "data_package", r.message.data_package)
						// frappe.model.set_value(cdt, cdn, "total_data_package", r.message.data_package*no_of_installation)
						// frappe.model.set_value(cdt, cdn, "total_data_package", r.message.data_package*frm.doc.no_of_installation_employee)
						frappe.call({
							method: "check_conversion_factor",
							doc: frm.doc,
							args: {"item_code": d.item_code, "uom": d.uom},
							callback: function(m){
								frappe.model.set_value(cdt,cdn,"rate",flt(r.message/flt(m.message),2));
							}
						})
					}
					
				}
			})
			frappe.call({
				method: "erpnext.selling.doctype.emi_sales.emi_sales.get_default_income_account",
				args: {
					"item_code":d.item_code,
					"company": frm.doc.company
				},
				callback(r) {
					if(r.message) {
						d.income_account = r.message.income_account
						d.interest_income_account = r.message.interest_income_account
						if (d.item_group == 'Sales Product') d.expense_account = r.message.expense_account
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Company',
					filters: {
						'company_name': frm.doc.company
					},
					fieldname: ['default_expense_account','default_cash_account','default_receivable_account']
				},
				callback: function(r){
					if(r.message){
						if (d.item_group != 'Sales Product') d.expense_account = r.message.default_expense_account;
						if (frm.doc.is_on_credit || frm.doc.is_opening_bal){
							d.cash_bank_account = r.message.default_receivable_account
							frm.set_value('debit_to',r.message.default_receivable_account)
						}else d.cash_bank_account = r.message.default_cash_account;
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Selling Settings',
					fieldname: ['default_commission_account','default_tds_account','default_discount_account']
				},
				callback: function(r){
					if(r.message){
						d.commission_account = r.message.default_commission_account;
						d.tds_account = r.message.default_tds_account;
						d.discount_account = r.message.default_discount_account
						frm.refresh_field("items")
					}
				}
			});
			frappe.call({
				method:'erpnext.selling.doctype.emi_sales.emi_sales.set_actual_qty',
				args:{
					'item_code':d.item_code,
					'warehouse':frm.doc.delivery_warehouse
				},
				callback:(r)=>{
					frappe.model.set_value(cdt, cdn, "actual_qty", r.message)
				}
			})
		}
		if ( frm.doc.company && frm.doc.branch && d.item_code && frm.doc.posting_date){			
			frappe.call({
				method: "erpnext.production.doctype.selling_price.selling_price.get_emi_selling_rate",
				args: {
						"branch": frm.doc.branch,
						"item_code": d.item_code,
						"transaction_date": cint(frm.doc.set_price_date_manually) == 1 ? frm.doc.pricing_date : frm.doc.posting_date,
						"selling_uom": d.uom,
						"location": ''
						// "payment_type":frm.doc.payment_type,
						// "no_of_installation": no_of_installation,
				},
				callback: function(r) {
					if (r.message){
						frappe.model.set_value(cdt, cdn, "rate", r.message.selling_price)
						// frappe.model.set_value(cdt, cdn, "selling_price", r.message.name)
						// frappe.model.set_value(cdt, cdn, "data_package", r.message.data_package)
						// frappe.model.set_value(cdt, cdn, "total_data_package", r.message.data_package*frm.doc.no_of_installation_external)
						// frappe.model.set_value(cdt, cdn, "total_data_package", r.message.data_package*frm.doc.no_of_installation_employee)
						frappe.call({
							method: "check_conversion_factor",
							doc: frm.doc,
							args: {"item_code": d.item_code, "uom": d.uom},
							callback: function(m){
								frappe.model.set_value(cdt,cdn,"rate",flt(r.message/flt(m.message),2));
							}
						})
					}
					
				}
			})
			frappe.call({
				method: "erpnext.selling.doctype.emi_sales.emi_sales.get_default_income_account",
				args: {
					"item_code":d.item_code,
					"company": frm.doc.company
				},
				callback(r) {
					if(r.message) {
						d.income_account = r.message.income_account
						d.interest_income_account = r.message.interest_income_account
						if (d.item_group == 'Sales Product') d.expense_account = r.message.expense_account
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Company',
					filters: {
						'company_name': frm.doc.company
					},
					fieldname: ['default_expense_account','default_cash_account','default_receivable_account']
				},
				callback: function(r){
					if(r.message){
						if (d.item_group != 'Sales Product') d.expense_account = r.message.default_expense_account;
						if (frm.doc.is_on_credit || frm.doc.is_opening_bal){
							d.cash_bank_account = r.message.default_receivable_account
							frm.set_value('debit_to',r.message.default_receivable_account)
						}else d.cash_bank_account = r.message.default_cash_account;
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Selling Settings',
					fieldname: ['default_commission_account','default_tds_account','default_discount_account']
				},
				callback: function(r){
					if(r.message){
						d.commission_account = r.message.default_commission_account;
						d.tds_account = r.message.default_tds_account;
						d.discount_account = r.message.default_discount_account
						frm.refresh_field("items")
					}
				}
			});
			frappe.call({
				method:'erpnext.selling.doctype.emi_sales.emi_sales.set_actual_qty',
				args:{
					'item_code':d.item_code,
					'warehouse':frm.doc.delivery_warehouse
				},
				callback:(r)=>{
					frappe.model.set_value(cdt, cdn, "actual_qty", r.message)
				}
			})
		}
	},
	item_code: function(frm, cdt, cdn) {
		// on_selection of price_template, auto load the selling price for item
		var d = locals[cdt][cdn]
		var no_of_installation = 0
		if(frm.doc.sales_order_type == "External Customers" && frm.doc.credit_type == "Installment Payment"){
			no_of_installation = frm.doc.no_of_installation_external
		}
		else if(frm.doc.sales_order_type == "Employee Installment" && frm.doc.credit_type == "Installment Payment"){
			no_of_installation = frm.doc.no_of_installation_employee
		}
		else if(frm.doc.sales_order_type != "Employee Installment" && frm.doc.sales_order_type != "External Customers" && frm.doc.credit_type == "Installment Payment"){
			no_of_installation = frm.doc.no_of_installation
		}
		if ( frm.doc.company && frm.doc.branch && d.item_code && frm.doc.posting_date ){			
			frappe.call({
				method: "erpnext.production.doctype.selling_price.selling_price.get_emi_selling_rate",
				args: {
						"branch": frm.doc.branch,
						"item_code": d.item_code,
						"transaction_date": cint(frm.doc.set_price_date_manually) == 1 ? frm.doc.pricing_date : frm.doc.posting_date,
						"selling_uom": d.uom,
						"location": ''
						// "payment_type":frm.doc.payment_type,
						// "no_of_installation": no_of_installation,
				},
				callback: function(r) {
					if (r.message){
						frappe.model.set_value(cdt, cdn, "rate", r.message)
						// frappe.model.set_value(cdt, cdn, "selling_price", r.message.name)
						// frappe.model.set_value(cdt, cdn, "data_package",  r.message.data_package)
						// frappe.model.set_value(cdt, cdn, "total_data_package",  r.message.data_package*frm.doc.no_of_installation_external) 
						// frappe.model.set_value(cdt, cdn, "total_data_package",  r.message.data_package*frm.doc.no_of_installation_employee)
						frappe.call({
							method: "check_conversion_factor",
							doc: frm.doc,
							args: {"item_code": d.item_code, "uom": d.uom},
							callback: function(m){
								frappe.model.set_value(cdt,cdn,"rate",flt(r.message/flt(m.message),2));
							}
						})
					}
					
				}
			})
			frappe.call({
				method: "erpnext.selling.doctype.emi_sales.emi_sales.get_default_income_account",
				args: {
					"item_code":d.item_code,
					"company": frm.doc.company
				},
				callback(r) {
					if(r.message) {
						d.income_account = r.message.income_account
						d.interest_income_account = r.message.interest_income_account
						if (d.item_group == 'Sales Product') d.expense_account = r.message.expense_account
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Company',
					filters: {
						'company_name': frm.doc.company
					},
					fieldname: ['default_expense_account','default_cash_account','default_receivable_account']
				},
				callback: function(r){
					if(r.message){
						if (d.item_group != 'Sales Product') d.expense_account = r.message.default_expense_account;
						if (frm.doc.is_on_credit || frm.doc.is_opening_bal){
							d.cash_bank_account = r.message.default_receivable_account
							frm.set_value('debit_to',r.message.default_receivable_account)
						}else d.cash_bank_account = r.message.default_cash_account;
						console.log("HERE "+String(r.message.default_cash_account))
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Selling Settings',
					fieldname: ['default_commission_account','default_tds_account','default_discount_account']
				},
				callback: function(r){
					if(r.message){
						d.commission_account = r.message.default_commission_account;
						d.tds_account = r.message.default_tds_account;
						d.discount_account = r.message.default_discount_account
						frm.refresh_field("items")
					}
				}
			});
			frappe.call({
				method:'erpnext.selling.doctype.emi_sales.emi_sales.set_actual_qty',
				args:{
					'item_code':d.item_code,
					'warehouse':frm.doc.delivery_warehouse
				},
				callback:(r)=>{
					frappe.model.set_value(cdt, cdn, "actual_qty", r.message)
				}
			})
		}
		if ( frm.doc.company && frm.doc.branch && d.item_code && frm.doc.posting_date && frm.doc.sales_order_type == "Employee Installment" ){			
			frappe.call({
				method: "erpnext.production.doctype.selling_price.selling_price.get_emi_selling_rate",
				args: {
						"branch": frm.doc.branch,
						"item_code": d.item_code,
						"transaction_date": cint(frm.doc.set_price_date_manually) == 1 ? frm.doc.pricing_date : frm.doc.posting_date,
						"selling_uom": d.uom,
						"location": ''
						// "payment_type":frm.doc.payment_type,
						// "no_of_installation": no_of_installation,
				},
				callback: function(r) {
					if (r.message){
						frappe.model.set_value(cdt, cdn, "rate", r.message)
						// frappe.model.set_value(cdt, cdn, "selling_price", r.message.name)
						// frappe.model.set_value(cdt, cdn, "data_package",  r.message.data_package)
						// frappe.model.set_value(cdt, cdn, "total_data_package",  r.message.data_package*frm.doc.no_of_installation_external) 
						// frappe.model.set_value(cdt, cdn, "total_data_package",  r.message.data_package*frm.doc.no_of_installation_employee)
						frappe.call({
							method: "check_conversion_factor",
							doc: frm.doc,
							args: {"item_code": d.item_code, "uom": d.uom},
							callback: function(m){
								frappe.model.set_value(cdt,cdn,"rate",flt(r.message/flt(m.message),2));
							}
						})
					}
					
				}
			})
			frappe.call({
				method: "erpnext.selling.doctype.emi_sales.emi_sales.get_default_income_account",
				args: {
					"item_code":d.item_code,
					"company": frm.doc.company
				},
				callback(r) {
					if(r.message) {
						d.income_account = r.message.income_account
						d.interest_income_account = r.message.interest_income_account
						if (d.item_group == 'Sales Product') d.expense_account = r.message.expense_account
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Company',
					filters: {
						'company_name': frm.doc.company
					},
					fieldname: ['default_expense_account','default_cash_account','default_receivable_account']
				},
				callback: function(r){
					if(r.message){
						if (d.item_group != 'Sales Product') d.expense_account = r.message.default_expense_account;
						if (frm.doc.is_on_credit || frm.doc.is_opening_bal){
							d.cash_bank_account = r.message.default_receivable_account
							frm.set_value('debit_to',r.message.default_receivable_account)
						}else d.cash_bank_account = r.message.default_cash_account;
						console.log("HERE "+String(r.message.default_cash_account))
						frm.refresh_field("items")
					}
				}
			});

			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Selling Settings',
					fieldname: ['default_commission_account','default_tds_account','default_discount_account']
				},
				callback: function(r){
					if(r.message){
						d.commission_account = r.message.default_commission_account;
						d.tds_account = r.message.default_tds_account;
						d.discount_account = r.message.default_discount_account
						frm.refresh_field("items")
					}
				}
			});
			frappe.call({
				method:'erpnext.selling.doctype.emi_sales.emi_sales.set_actual_qty',
				args:{
					'item_code':d.item_code,
					'warehouse':frm.doc.delivery_warehouse
				},
				callback:(r)=>{
					frappe.model.set_value(cdt, cdn, "actual_qty", r.message)
				}
			})
		}

		//pull purchase limit if applicable
		if (d.item_code && frm.doc.customer_type == "Customer"){
			// frappe.call({
			// 	method:'erpnext.selling.doctype.emi_sales.emi_sales.get_purchase_limit',
			// 	args:{
			// 		'customer_group':frm.doc.customer_group,
			// 		'item_code':d.item_code,
			// 		'customer':frm.doc.customer
			// 	},
			// 	callback:(r)=>{
			// 		if(r.message){
			// 			d.purchase_limit = r.message
			// 			frm.refresh_field("items")
			// 		}else{
			// 			d.purchase_limit = 0
			// 			frm.refresh_field("items")
			// 		}
			// 	}
			// })
		}
		//fetch actual qty 
		calculate_down_payment(frm, cdt, cdn)
		var subgroups = ["Voucher", "Sim"]
		frappe.meta.get_docfield("EMI Sales Item","serial_number",cur_frm.doc.name).reqd = subgroups.includes(d.item_subgroup)? 1 : 0
		// frappe.meta.get_docfield("EMI Sales Item","serial_number",cur_frm.doc.name).reqd = d.item_group == 'Services' ? 0 : 1
		frappe.meta.get_docfield("EMI Sales Item","ime_number",cur_frm.doc.name).reqd = d.item_subgroup == 'Mobile Handset' ? 1 : 0
		frappe.meta.get_docfield("EMI Sales Item","rate",cur_frm.doc.name).read_only = d.item_group == 'Services' ? 0 : 1
		frappe.meta.get_docfield("EMI Sales Item","discount_percent",cur_frm.doc.name).hidden = frm.doc.is_discounted ? 0 : 1
		frappe.meta.get_docfield("EMI Sales Item","discount_amount",cur_frm.doc.name).hidden = frm.doc.is_discounted ? 0 : 1
	}
});
cur_frm.fields_dict['items'].grid.get_field('uom').get_query = function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		query: "erpnext.controllers.queries.filter_item_uom",
		filters: {
			"item_code": d.item_code,
		}
	}
}
var calculate_amount=(frm,cdt,cdn)=>{
	var item = locals[cdt][cdn]
	frm.refresh_field('items')
	let total_amount_received = 0
	let rate = 0
	frm.doc.items.forEach(ele => {
		total_amount_received += flt(ele.total_amount_received)
		rate = ele.rate
	});
	if(frm.doc.sales_order_type){
		frappe.call({
			method: "frappe.client.get",
			args: {
			  doctype: "EMI Sales Type",
			  name: frm.doc.sales_order_type,
			},
			callback(r) {
				if(r.message){
					let rows = r.message.customer_group; // child table fieldname
					var per = 100;
					if(rows?.[0]?.customer_group == frm.doc.customer_group){
						per = rows?.[0]?.cost_sharing_percentage;
					}
					if(frm.doc.sales_order_type != "Cost Sharing Installment"){
						frm.set_value("total_receivable_amount", flt(total_amount_received) - flt(frm.doc.down_payment_amount))
					}
					else{
						var quota = 0
						frappe.db.get_value("Employee", frm.doc.customer, "grade", (r)=>{
							frappe.db.get_value("Employee Grade", r.grade, "cost_sharing_quotaamount", (m)=>{
								quota = m.cost_sharing_quotaamount
								let receivable_amount = 0
								if(frm.doc.down_payment_amount>rate-quota){
									 receivable_amount = flt((quota*per*0.01)-(frm.doc.down_payment_amount - (rate - quota)));

								}
								else{
									receivable_amount = flt(quota*per*0.01);
								}
								frm.set_value("total_receivable_amount", receivable_amount)
								frappe.model.set_value(cdt, cdn, "total_amount_received", receivable_amount)
							})
						})
					}
					frm.refresh_fields();
					// cur_frm.refresh_field('total_receivable_amount')
					cur_frm.refresh_field('total_receivable_amount')
				}

			}
		});
		// if(frm.doc.sales_order_type != "Cost Sharing Installment"){
		// 	if (item.qty && item.rate ) item.amount = flt(item.qty) * flt(item.rate)
		// 	else if (flt(item.rate) == 0 ){
		// 		item.amount = flt(item.qty) * flt(item.rate)
		// 	}
		// 	if ( frm.doc.is_discounted && !frm.doc.required_commission){
		// 		if (item.discount_percent){
		// 			item.discount_amount = flt(flt(item.discount_percent) * flt(item.amount)/100)
		// 		}
		// 		item.total_amount_received = flt(item.amount) - flt(item.discount_amount)
		// 	}else{
		// 		item.discount_percent = 0
		// 		item.discount_amount = 0
		// 		item.total_amount_received = flt(item.amount) - flt(item.discount_amount)
		// 	}
		// 	if (flt(item.tds_deducted_by_customer) > 0 ){
		// 		item.total_amount_received = flt(item.total_amount_received) - flt(item.tds_deducted_by_customer)
		// 	}
		// }
	}
	else{
		frm.set_value('total_receivable_amount',total_amount_received)
		cur_frm.refresh_field('total_receivable_amount')
	}
}
var calculate_down_payment = (frm, cdt, cdn)=>{
	var row = locals[cdt][cdn];
	frappe.call({
		method: "calculate_down_payment",
		doc: frm.doc,
		args: {"rate": row.rate},
		callback: function(r){
			if(r.message){
				frm.set_value("down_payment_amount", r.message);
				if(r.message > 0){
					frm.set_value("down_payment", 1)
				}
				else{
					frm.set_value("down_payment", 0)
				}
				frm.refresh_field("down_payment");
				frm.refresh_field("down_payment_amount");

			}
		}
	})
}
var calculate_commission = (frm, cdt, cdn)=>{
	var row = locals[cdt][cdn]
	if ( !frm.doc.required_commission){
		row.total_amount_received = row.amount
		frm.refresh_field('items')
		return
	}
	var row = locals[cdt][cdn]
	if(row.item_subgroup){
		frappe.call({
			method:"erpnext.selling.doctype.commission.commission.get_commission_taxable_tds_percent",
			args:{
				"order_type": frm.doc.sales_order_type,
				"customer_group": frm.doc.customer_group,
				"item_sub_group": row.item_subgroup,
				"posting_date": frm.doc.posting_date,
				"customer":frm.doc.customer,
				"customer_type":frm.doc.customer_type
			},
			callback:(r)=>{ 
				if (r.message.length > 0 ){
					row.commission_percent = flt(r.message[0].commission)
					row.tds_percent = flt(r.message[0].tds)
					row.taxable_percent = flt(r.message[0].tax_payable)
					row.commission_amount = flt(row.amount) * flt(row.commission_percent) / 100
					row.taxable_amount = flt(row.amount) * flt(row.taxable_percent) / 100
					row.tds_amount = flt(row.taxable_amount) * flt(row.tds_percent) / 100
					row.total_amount_received = flt(row.amount) - flt(row.commission_amount) + flt(row.tds_amount)
					frm.refresh_field('items')
					let total_amount_received = 0
					let total_tds = 0
					frm.doc.items.forEach(ele => {
						total_amount_received += flt(ele.total_amount_received)
						total_tds += flt(ele.tds_amount)
					});
					frm.set_value('total_receivable_amount',total_amount_received)
					frm.set_value('total_tds_amount',total_tds)
					frm.refresh_field('total_tds_amount')
					frm.refresh_field('total_receivable_amount')
				}
			}
		})
	}
}

frappe.form.link_formatters['Item'] = function(value, doc) {
	return value
}
