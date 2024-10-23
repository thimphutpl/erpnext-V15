// render

frappe.listview_settings['Break Down Report'] = {
	add_fields: ["docstatus", "job_cards"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
			return ["Report Created", "grey", "docstatus,=,0"];
		}

		if(doc.docstatus == 1) {
			if(doc.job_cards) {
				return ["Job Card Created", "green", "docstatus,=,1|job_card,>,0"];
			}
			else {
				return ["Report Completed", "blue", "docstatus,=,1|job_card,<=,0"];
			}
		}
	}
};