// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Performance Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Link",
 			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label": ("Parent Branch"),
			"fieldtype": "Link",
 			"options": "Cost Center",
			"get_query": function() {
				var company = frappe.query_report.get_filter_value("company");
				return {
					'doctype': "Cost Center",
					'filters': [
						['disabled', '!=', '1'], 
						['is_group', '=', '1'],
						['company', '=', company]
					]
				}
			},
			// "on_change": function(query_report) {
			// 	var cost_center = query_report.get_values().cost_center;
			// 	query_report.filters_by_name.branch.set_input(null);
			// 	query_report.trigger_refresh();
			// 	if (!cost_center) {
			// 		return;
			// 	}
			// 	frappe.call({
			// 		method: "erpnext.custom_utils.get_branch_from_cost_center",
			// 		args: {
			// 			"cost_center": cost_center,
			// 		},
			// 		callback: function(r) {
			// 			query_report.filters_by_name.branch.set_input(r.message)
			// 			query_report.trigger_refresh();
			// 		}
			// 	})
			// },
			"reqd": 1,
		},
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
                                var cost_center = frappe.query_report.get_filter_value("cost_center")
                                var company = frappe.query_report.get_filter_value("company")
                                if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
                                {
                                                return {"doctype": "Cost Center", "filters": {"company": company, "disabled": 0, "parent_cost_center": cost_center}}
                                }
                                else
                                {
                                                return {"doctype": "Cost Center", "filters": {"company": company, "disabled": 0, "is_group": 0}}
                                }
			}
		},
		{
			"fieldname": "fy",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1,
		},
		{
			"fieldname": "period",
			"label": __("Period"),
			"fieldtype": "Select",
			"options": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"],
			"default": "",
		},
		{
			"fieldtype": "Break"
		},
		{
            "fieldname": "not_cdcl",
            "label": ("Own Equipments"),
            "fieldtype": "Check",
            "default": 1
                },
		{
            "fieldname": "include_disabled",
            "label": ("Include Disbaled Equipments"),
            "fieldtype": "Check",
            "default": 0
        },
		{
			"fieldname": "equipment_category",
			"label": ("Equipment Category"),
			"fieldtype": "Link",
 			"options": "Equipment Category",
		},
	]
}