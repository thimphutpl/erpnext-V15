// frappe.query_reports["GST Report"] = {
// 	"filters": [
// 		{
// 			fieldname: "account_type",
// 			label: __("Account Type"),
// 			fieldtype: "Select",
// 			options: ["", "GST 5% Paid - CDCL", "GST 5% Received - CDCL"],
// 		},
// 		{
// 			fieldname: "voucher_type",
// 			label: __("Voucher Type"),
// 			fieldtype: "Select",
// 			options: [
// 				"",
// 				"Purchase Invoice",
// 				"POL Receive",
// 				"Imprest Recoup",
// 				"Utility Bill",
// 				"Sales Invoice",
// 				"Hire Charge Invoice",
// 				"Mechanical Payment",
// 				"Project Invoice",
// 				"Rental"
// 			]
// 		},
// 		{
// 			fieldname: "month",
// 			label: __("Month"),
// 			fieldtype: "Select",
// 			options: [
// 				"",
// 				"January",
// 				"February",
// 				"March",
// 				"April",
// 				"May",
// 				"June",
// 				"July",
// 				"August",
// 				"September",
// 				"October",
// 				"November",
// 				"December"
// 			]
// 		}
// 	]
// };

frappe.query_reports["GST Report"] = {
	filters: [
		{
			fieldname: "account_type",
			label: __("Account Type"),
			fieldtype: "Select",
			options: [
				"",
				"GST 5% Paid - CDCL",
				"GST 5% Received - CDCL"
			]
		},
		{
			fieldname: "voucher_type",
			label: __("Voucher Type"),
			fieldtype: "Select",
			options: [""]
		},
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: [
				"",
				"January",
				"February",
				"March",
				"April",
				"May",
				"June",
				"July",
				"August",
				"September",
				"October",
				"November",
				"December"
			]
		}
	],

	onload: function (report) {

		function update_voucher_type() {
			let account_type = report.get_filter_value("account_type");

			let options = [""];

			if (account_type === "GST 5% Paid - CDCL") {
				options = options.concat([
					"Purchase Invoice",
					"POL Receive",
					"Imprest Recoup",
					"Utility Bill"
				]);
			}

			if (account_type === "GST 5% Received - CDCL") {
				options = options.concat([
					"Sales Invoice",
					"Hire Charge Invoice",
					"Mechanical Payment",
					"Project Invoice",
					"Rental"
				]);
			}

			let voucher_filter = report.get_filter("voucher_type");
			voucher_filter.df.options = options;
			voucher_filter.refresh();
		}

		// run once on load
		update_voucher_type();

		// 🔥 correct way: listen to filter changes
		report.page.fields_dict.account_type.$input.on("change", function () {
			update_voucher_type();
		});
	}
};


// function update_voucher_type(report) {
// 	let account_type = report.get_filter_value("account_type");

// 	let options = [""];

// 	if (account_type === "GST 5% Paid - CDCL") {
// 		options = options.concat([
// 			"Purchase Invoice",
// 			"POL Receive",
// 			"Imprest Recoup",
// 			"Utility Bill"
// 		]);
// 	}

// 	if (account_type === "GST 5% Received - CDCL") {
// 		options = options.concat([
// 			"Sales Invoice",
// 			"Hire Charge Invoice",
// 			"Mechanical Payment",
// 			"Project Invoice",
// 			"Rental"
// 		]);
// 	}

// 	let voucher_filter = report.get_filter("voucher_type");
// 	voucher_filter.df.options = options;
// 	voucher_filter.refresh();
// }