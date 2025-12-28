frappe.query_reports["Initial Budget Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "default": frappe.defaults.get_user_default("fiscal_year"),
            "reqd": 1,
            "on_change": function(query_report) {
                const fiscal_year = query_report.get_values().fiscal_year;
                if (!fiscal_year) return;

                frappe.model.with_doc("Fiscal Year", fiscal_year, function() {
                    const fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
                    if (query_report.filters_by_name.from_date)
                        query_report.filters_by_name.from_date.set_input(fy.year_start_date);
                    if (query_report.filters_by_name.to_date)
                        query_report.filters_by_name.to_date.set_input(fy.year_end_date);
                    query_report.trigger_refresh();
                });
            }
        },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "get_query": function() {
                const company = frappe.query_report.get_filter_value('company');
                return {
                    "doctype": "Cost Center",
                    "filters": {
                        "company": company
                    }
                };
            }
        }
    ]
};