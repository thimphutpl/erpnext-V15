// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gift Register", {
	refresh(frm) {
        make(frm);
	},
});


var make = (frm)=>{
	// if (cint(frm.doc.is_opening) == 1) return
	
		
       
        
        // frm.add_custom_button(
		// 	__("Sale"),
		// 	function () {
        //     frm.set_value('gift_status', 'Sold');
        //     frm.save()
		// 	},
		// 	__("Make")
		// );
		frm.add_custom_button(
			__("Return"),
			function () {
				// Define the dialog
				let d = new frappe.ui.Dialog({
					title: 'New Dialog Box',
					fields: [
						{
							label: 'Date of Return',
							fieldname: 'date_of_return',
							fieldtype: 'Date',
							reqd: 1
						},
						{
							label: 'Reason',
							fieldname: 'reason',
							fieldtype: 'Data',
							reqd: 1
						},
						
					],
					primary_action_label: 'Submit',
					primary_action(values) {
						// What happens when the submit button is clicked
						console.log(values);
						// You can do something with the values here, like setting them in the form
						frm.set_value('date', values.date_of_return);
						frm.set_value('remarks_gift', values.reason);
						// frm.set_value('age', values.age);
						frm.set_value('gift_status', 'Returned');
            			frm.save();
						// Close the dialog
						d.hide();
						
					}
				});
	
				// Show the dialog
				d.show();
			},
			__("Make")
		);
		frm.add_custom_button(
			__("Dispose"),
			function () {
				// Define the dialog
				let d = new frappe.ui.Dialog({
					title: 'New Dialog Box',
					fields: [
						{
							label: 'Date of Deposit',
							fieldname: 'date_of_deposit',
							fieldtype: 'Date',
							reqd: 1
						},
						{
							label: 'Name of organization',
							fieldname: 'organisation',
							fieldtype: 'Data',
							reqd: 1
						},
						{
							label: 'Receipt/Acknowledgement',
							fieldname: 'receipt',
							fieldtype: 'Attach',
							reqd: 1
						},

						
					],
					primary_action_label: 'Submit',
					primary_action(values) {
						// What happens when the submit button is clicked
						// console.log(values);
						// You can do something with the values here, like setting them in the form
						frm.set_value('date', values.date_of_deposit);
						frm.set_value('name_of_organisation', values.organisation);
						frm.set_value('receiptacknowledgement', values.receipt);
						frm.set_value('gift_status', 'Disposed');
            			frm.save();
						// Close the dialog
						d.hide();
						
					}
				});
	
				// Show the dialog
				d.show();
			},
			__("Make")
		);
	
}