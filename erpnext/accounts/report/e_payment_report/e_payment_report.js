// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["e-Payment Report"] = {
	"onload": function (query_report) {
    	query_report.filters_by_name.party.toggle(false);
    },
	"filters": [
		{
            fieldname: "payment_type",
            label: "Payment Type",
            fieldtype: "Select",
            options: ["Bank Payment", "Utility Bill Payment"],
            default: "Bank Payment",
            on_change: function(query_report){
                var payment_type = query_report.get_values().payment_type;
                var transaction_type = query_report.filters_by_name["transaction_type"];
                var supplier = query_report.filters_by_name["supplier"];
                var status = query_report.filters_by_name["status"];
                var party = query_report.filters_by_name['party'];

                if (payment_type == 'Utility Bill Payment'){
                    transaction_type.toggle(false);
                    supplier.toggle(false);
                    status.toggle(false);
                    party.toggle(true);
                }
                else{
                    transaction_type.toggle(true);
                    supplier.toggle(true);
                    status.toggle(true);
                    party.toggle(false);
                }
                query_report.refresh()
                transaction_type.refresh()
                supplier.refresh()
                status.refresh()
                party.refresh()
            }
        },
        {
            fieldname: "transaction_type",
            label: "Transaction Type",
            fieldtype: "Select",
            options: ["","Direct Payment", "Journal Entry", "Payment Entry", "Transporter Payment", "Salary Slip", "Employee Loan Payment", "LTC", "Bonus", "PBVA"]
        },
        {
            fieldname: "party_type",
            label: __("Party Type"),
            fieldtype: "Autocomplete",
            options: Object.keys(frappe.boot.party_account_types),
            on_change: function () {
                frappe.query_report.set_filter_value("party", "");
            },
        },
        {
            fieldname: "party",
            label: __("Party"),
            fieldtype: "MultiSelectList",
            get_data: function (txt) {
                if (!frappe.query_report.filters) return;

                let party_type = frappe.query_report.get_filter_value("party_type");
                if (!party_type) return;

                return frappe.db.get_link_options(party_type, txt);
            },
            on_change: function () {
                var party_type = frappe.query_report.get_filter_value("party_type");
                var parties = frappe.query_report.get_filter_value("party");

                if (!party_type || parties.length === 0 || parties.length > 1) {
                    frappe.query_report.set_filter_value("party_name", "");
                    frappe.query_report.set_filter_value("tax_id", "");
                    return;
                } else {
                    var party = parties[0];
                    var fieldname = erpnext.utils.get_party_name(party_type) || "name";
                    frappe.db.get_value(party_type, party, fieldname, function (value) {
                        frappe.query_report.set_filter_value("party_name", value[fieldname]);
                    });

                    if (party_type === "Customer" || party_type === "Supplier") {
                        frappe.db.get_value(party_type, party, "tax_id", function (value) {
                            frappe.query_report.set_filter_value("tax_id", value["tax_id"]);
                        });
                    }
                }
            },
        },
        {
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options:["","Completed", "Pending", "Draft", "Waiting for Verification", "Waiting Approval", "Approved", "Rejected", "Failed", "Partial Payment", "Cancelled", "In progress", "Upload Failed", "Waiting Acknowledgement", "Processing Acknowledgement"]
        }
	]
};
