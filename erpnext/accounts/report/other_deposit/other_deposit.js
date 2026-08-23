// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Other Deposit"] = {
	 filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
        },
        {
            fieldname: "account",
            label: __("Account"),
            fieldtype: "Link",
            options: "Account",
            reqd: 1,
            get_query: function() {
                return {
                    filters: {
                        company: frappe.query_report.get_filter_value("company"),
                        is_group: 0
                    }
                };
            }
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
    ],
    formatter: function(value, row, column, data, default_formatter) {

        value = default_formatter(
            value,
            row,
            column,
            data
        );

        if (
            column.fieldname === "total_outstanding" &&
            data &&
            flt(data.total_outstanding) < 0
        ) {
            value =
                '<span style="color:red;font-weight:bold;">' +
                value +
                '</span>';
        }
        return value;
    }
};
