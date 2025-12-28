# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = [], []

    # Validate that the necessary filter is provided
    if not filters or not filters.get("request_for_quotation"):
        frappe.throw("Please select a Request for Quotation.")

    # Fetch supplier quotations and items dynamically based on the selected RFQ
    supplier_quotations = get_supplier_quotations(filters)

    # Dynamically generate columns
    columns = generate_columns(supplier_quotations)

    # Generate data rows
    data = generate_data_rows(supplier_quotations)

    return columns, data


def get_supplier_quotations(filters):
    """
    Fetch Supplier Quotations and related items based on the selected Request for Quotation.
    """
    if not filters.get("request_for_quotation"):
        frappe.throw(_("Please select a Request for Quotation."))

    rfq_name = filters.get("request_for_quotation")
    
    quotations = frappe.db.sql(
        """
        SELECT 
            sq.supplier AS supplier,
            sqi.item_code,
            sqi.qty,
            sqi.rate
        FROM 
            `tabSupplier Quotation` AS sq
        INNER JOIN 
            `tabSupplier Quotation Item` AS sqi
            ON sq.name = sqi.parent
        WHERE 
            sq.docstatus = 1
            AND EXISTS (
                SELECT 
                    1 
                FROM 
                    `tabRequest for Quotation` AS rfq
                INNER JOIN
                    `tabRequest for Quotation Supplier` AS rfq_supplier
                    ON rfq.name = rfq_supplier.parent
                WHERE 
                    rfq_supplier.supplier = sq.supplier
                    AND rfq.name = %s
            )
        ORDER BY 
            sq.supplier, sqi.item_code;
        """,
        (rfq_name,),
        as_dict=True
    )

    # Process the fetched data
    grouped_data = {}
    for row in quotations:
        item_code = row['item_code']
        qty = row['qty']
        rate = row['rate']
        supplier = row['supplier']
        if item_code not in grouped_data:
            grouped_data[item_code] = {"qty": qty, "suppliers": {}, "lowest": {"supplier": "", "rate": None, "amount": 0}}
        grouped_data[item_code]["suppliers"][supplier] = {"rate": rate}
        
        # Update lowest quotation details
        if grouped_data[item_code]["lowest"]["rate"] is None or rate < grouped_data[item_code]["lowest"]["rate"]:
            grouped_data[item_code]["lowest"]["supplier"] = supplier
            grouped_data[item_code]["lowest"]["rate"] = rate
            grouped_data[item_code]["lowest"]["amount"] = qty * rate

    return grouped_data


def generate_columns(supplier_quotations):
    """
    Generate dynamic columns based on suppliers.
    """
    columns = [
        {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 150},
        {"fieldname": "qty", "label": "Quantity", "fieldtype": "Float", "width": 100},
        {"fieldname": "lowest_supplier", "label": "Lowest Quotation Supplier", "fieldtype": "Data", "width": 200},
        {"fieldname": "lowest_rate", "label": "Lowest Quotation Rate", "fieldtype": "Currency", "width": 120},
        {"fieldname": "quotation_amount", "label": "Quotation Amount", "fieldtype": "Currency", "width": 120},
    ]

    # Add columns dynamically for each supplier
    supplier_names = set()
    for item_data in supplier_quotations.values():
        supplier_names.update(item_data["suppliers"].keys())

    for supplier in sorted(supplier_names):
        columns.append({
            "fieldname": f"{supplier}_rate",
            "label": f"{supplier} Rate",
            "fieldtype": "Currency",
            "width": 120
        })

    return columns


def generate_data_rows(supplier_quotations):
    """
    Generate data rows dynamically based on suppliers and their items.
    """
    data = []

    for item_code, item_data in supplier_quotations.items():
        row = {
            "item_code": item_code,
            "qty": item_data["qty"],
            "lowest_supplier": item_data["lowest"]["supplier"],
            "lowest_rate": item_data["lowest"]["rate"],
            "quotation_amount": item_data["lowest"]["amount"],
        }

        for supplier, values in item_data["suppliers"].items():
            row[f"{supplier}_rate"] = values.get("rate", 0)

        data.append(row)

    return data


