frappe.query_reports["Purchase History Report"] = {
    "filters": [
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
