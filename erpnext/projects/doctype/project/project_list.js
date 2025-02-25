frappe.listview_settings["Project"] = {
	add_fields: ["status", "priority", "is_active", "percent_complete", "tot_wq_percent_complete", "tot_wq_percent", "expected_end_date", "project_name"],
	filters: [["status", "=", "Open"]],
	get_indicator: function (doc) {
		if (doc.status == "Open") {
			return [__(doc.status), "orange", "status,=,Open"];
		}
		else if (doc.status == "Ongoing") {
			return [__(doc.status), "orange", "status,=,Ongoing"];
		}
		else if (doc.status == "Completed") {
			return [__(doc.status), "green", "status,=,Completed"];
		}
		else if (doc.status == "Cancelled") {
			return [__(doc.status), "red", "status,=,Cancelled"];
		}
		// else {
		// if(parseFloat(doc.tot_wq_percent_complete) < parseFloat(doc.tot_wq_percent)){
		// 	return [__("{0}%", [Math.round(doc.tot_wq_percent_complete)]), "orange", "percent,>=,0|status,=,Ongoing"];
		// } else if(parseFloat(doc.tot_wq_percent_complete) >= parseFloat(doc.tot_wq_percent)){
		// 	return [__("{0}%", [Math.round(doc.tot_wq_percent_complete)]), "green", "tot_wq_percent_complete,>=,"+doc.tot_wq_percent+"|status,=,"+doc.status];
		// } else {
		// 	return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		// }
		// }
	},
};
