frappe.listview_settings['Mechanical Payment'] = {
	add_fields: ["docstatus"],
	get_indicator: function(doc) {
		if(doc.docstatus == 1) {
			return ["Payment Received", "green", "docstatus,=,1"];
		}
	}
};