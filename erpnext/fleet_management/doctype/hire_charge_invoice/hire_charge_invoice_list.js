
// render
frappe.listview_settings['Hire Charge Invoice'] = {
	add_fields: ["invoice_jv", "owned_by", "docstatus", "payment_jv", "outstanding_amount"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
				return ["Invoice Created", "grey", "docstatus,=,0"];
		}

		if(doc.docstatus == 1) {
			if (doc.owned_by == "Natural Resources Development Corporation Limited") {
				return ["Journal Adjusted", "yellow", "docstatus,=,1|outstanding_amount,=,0|owned_by,=,Natural Resources Development Corporation Limited"];
			}
			else if(doc.outstanding_amount == 0) {
				return ["Payment Received", "green", "docstatus,=,1|outstanding_amount,=,0|owned_by,!=,Natural Resources Development Corporation Limited"];
			}
			else if(doc.outstanding_amount != 0 && doc.outstanding_amount < doc.balance_amount) {
                                return ["Partially Received", "blue", "docstatus,=,1|outstanding_amount,!=,0|outstanding_amount,>,0|owned_by,=,Others"];
                        }
			else {
				return ["Invoice Raised", "blue", "docstatus,=,1|outstanding_amount,>,0|owned_by,!=,Natural Resources Development Corporation Limited"];
			}
		}
		
		if(doc.docstatus == 2) {
			return ["Invoice Cancelled", "red", "docstatus,=,2"]
		}
	}
};
