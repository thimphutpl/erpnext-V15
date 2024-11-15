frappe.ui.form.on('Fund Requisition', {

	refresh: function(frm){
		/*cur_frm.set_df_property("issuing_cost_center", "hidden", 1)
		cur_frm.set_df_property("bank_account", "hidden", 1)
		cur_frm.set_df_property("issuing_branch", "hidden", 1)
	
		if (in_list(user_roles, "Accounts User") && (frm.doc.workflow_state == "Approved")){
			cur_frm.set_df_property("issuing_cost_center", "hidden",  0)
			cur_frm.set_df_property("issuing_branch", "hidden", 0)
			cur_frm.set_df_property("bank_account", "hidden", 0)
			}	*/
		if (frm.doc.docstatus == 1){
			/*cur_frm.set_df_property("issuing_cost_center", "hidden", 0)
			cur_frm.set_df_property("issuing_branch", "hidden", 0)  
			cur_frm.set_df_property("bank_account", "hidden", 0)
			*/	
			
				 if (frappe.model.can_read("Journal Entry")){
        	                        cur_frm.add_custom_button(__('Bank Entries'), function(){
                	                frappe.route_options = {
                        	                "name": me.frm.doc.reference,
                                	};
                                frappe.set_route("List", "Journal Entry");
                }, __("View"));
        }
			}
		
		//frm.toggle_reqd("bank_account", 1)
         },
	
	"posting_date" : function(frm){
		if (frm.doc.posting_date > get_today()){
			frappe.msgprint("Future dates not allowed");
			frm.set_value("posting_date", get_today());
		}
	},

	"issuing_cost_center": function(frm){
		frm.toggle_reqd("issuing_cost_center", 1)
	},

	"bank_account" : function(frm){
		frm.toggle_reqd("bank_account", 1)	
	},
	
	"branch": function(frm) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Branch", 
				fieldname:"expense_bank_account",
				filters: {
					"branch": frm.doc.branch
				}
			},
			callback: function(r) {
				console.log(r.message);
				if(r.message.expense_bank_account) {
					cur_frm.set_value("bank", r.message.expense_bank_account)
					console.log(r.message.expense_bank_account)
				}
				else {
					frappe.throw("Setup an Expense Bank Account in the Branch")
				}
			}
		});
	},
	
});