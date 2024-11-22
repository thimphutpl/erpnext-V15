frappe.ui.form.on('Risk Assessment', {
	refresh: function(frm) {

		frm.set_query("risk_factor", "items", function(doc, cdt, cdn) {
			let row = locals[cdt][cdn]
			if(!row.branch){
				return {
					filters: {
						audit_subject: row.audit_subject,
						posting_date: row.posting_date
					}
				};
			} else if(!row.audit_subject){
				return {
					filters: {
						branch: row.branch,
						posting_date: row.posting_date
					}
				};
			} else if(!row.posting_date){
				return {
					filters: {
						branch: row.branch,
						audit_subject: row.audit_subject
					}
				};
			} else {
				return {
					filters: {
						branch: row.branch,
						audit_subject: row.audit_subject,
						posting_date: row.posting_date
					}
				};
			}
			
		});
	}
});