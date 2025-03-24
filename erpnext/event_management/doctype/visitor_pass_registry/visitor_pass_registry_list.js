// render
frappe.listview_settings["Visitor Pass Registry"] = {
	get_indicator: function (doc) {
		var status_color = {
			Draft: "red",
			Submitted: "blue",
			Open: "orange",
			Close: "red",
			Cancelled: "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=," + doc.status];
	},
};