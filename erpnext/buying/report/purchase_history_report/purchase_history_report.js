frappe.query_reports["Purchase History Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",

        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",

        },
        {
            "fieldname": "mr_name",
            "label": __("Material Request Name"),
            "fieldtype": "Link",
            "options": "Material Request",
            "default": "" 
        },
        {
            "fieldname": "po_name",
            "label": __("Purchase Order Name"),
            "fieldtype": "Link",
            "options": "Purchase Order",
            "default": "" 
        },
        {
            "fieldname": "pr_name",
            "label": __("Purchase Receipt Name"),
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "default": "" 
        },
        {
            "fieldname": "pi_name",
            "label": __("Purchase Invoice Name"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "default": "" 
        }
    ]
};
