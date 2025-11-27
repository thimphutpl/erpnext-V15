frappe.listview_settings['EMI Sales'] = {
	add_fields: ["customer", "outstanding_amount", "due_date", "company",
		"currency", "is_return"],
	get_indicator: function(doc) {
		var status_color = {
			"Draft": "red",
			"Not Received": "orange",
			"Received": "green",
			"Return": "darkgrey",
			"Credit Note Issued": "darkgrey",
			"Unpaid and Discounted": "orange",
			"Overdue and Discounted": "red",
			"Overdue": "red",
			"Partially Received":"yellow",
			"Subbmitted":"Blue"

		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	},
	right_column: "grand_total"
};