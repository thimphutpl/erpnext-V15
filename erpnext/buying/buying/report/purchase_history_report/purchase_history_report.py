import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "mr_name", "label": "Material Request Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "mr_transation", "label": "Material Request Transaction Date", "fieldtype": "Date", "width": 200},
        {"fieldname": "mr_cost_center", "label": "Material Cost Center", "fieldtype": "Data", "width": 200},
        {"fieldname": "mr_status", "label": "Material Request Status", "fieldtype": "Data", "width": 200},
        {"fieldname": "mr_date", "label": "Forward to Procurement", "fieldtype": "Date", "width": 200},
        {"fieldname": "mri_code", "label": "Item Code", "fieldtype": "Data", "width": 200},
        {"fieldname": "mri_name", "label": "Material Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "mri_quantity", "label": "Material Quantity", "fieldtype": "Float", "width": 200},
        {"fieldname": "po_name", "label": "Purchase Order Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "po_date", "label": "Purchase Order Date", "fieldtype": "Date", "width": 200},
        {"fieldname": "po_schedule_date", "label": "Delivery Date", "fieldtype": "Date", "width": 200},
        {"fieldname": "po_supplier", "label": "Vendor", "fieldtype": "Data", "width": 200},
        {"fieldname": "po_status", "label": "Purchase Order Status", "fieldtype": "Data", "width": 200},
        {"fieldname": "pr_name", "label": "Purchase Receipt Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "pr_date", "label": "Purchase Receipt Date", "fieldtype": "Date", "width": 200},
        {"fieldname": "pri_received_qty", "label": "Received Quantity", "fieldtype": "Float", "width": 200},  # Fixed field name
        {"fieldname": "pr_status", "label": "Purchase Receipt Status", "fieldtype": "Data", "width": 200},
        {"fieldname": "pi_name", "label": "Purchase Invoice Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "pi_date", "label": "Purchase Invoice Date", "fieldtype": "Date", "width": 200},
        {"fieldname": "pi_status", "label": "Purchase Invoice Status", "fieldtype": "Data", "width": 200},
        
    ]

    conditions = []
    values = []

    if filters.get("mr_name"):
        conditions.append("mr.name = %s")
        values.append(filters["mr_name"])
    if filters.get("po_name"):
        conditions.append("po.name = %s")
        values.append(filters["po_name"])
    if filters.get("pr_name"):
        conditions.append("pr.name = %s")
        values.append(filters["pr_name"])
    if filters.get("pi_name"):
        conditions.append("pi.name = %s")
        values.append(filters["pi_name"])

    condition_string = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
    SELECT 
        mr.name AS mr_name, 
        mr.transaction_date AS mr_transation,
        mr.cost_center AS mr_cost_center,  
        mr.status AS mr_status,
        mr.date AS mr_date,  
        po.name AS po_name,
        po.transaction_date AS po_date,
        po.schedule_date AS po_schedule_date,
        po.supplier AS po_supplier,
        po.status AS po_status,
        pr.name AS pr_name,
        pr.posting_date AS pr_date,
        pri.received_qty AS pri_received_qty,  -- Fixed alias
        pr.status AS pr_status,
        pi.name AS pi_name,
        pi.posting_date AS pi_date,
        pi.status AS pi_status,
        mri.item_code AS mri_code,
        mri.item_name AS mri_name,
        mri.qty AS mri_quantity
    FROM `tabMaterial Request` AS mr
    INNER JOIN `tabMaterial Request Item` AS mri ON mr.name = mri.parent
    LEFT JOIN `tabPurchase Order` AS po ON po.material_request = mr.name
    LEFT JOIN `tabPurchase Receipt` AS pr ON pr.purchase_order = po.name
    LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name  -- Correct join
    LEFT JOIN `tabPurchase Invoice` AS pi ON pi.purchase_receipt = pr.name
    WHERE {condition_string}
    """

    data = frappe.db.sql(query, tuple(values), as_dict=True)

    return columns, data
