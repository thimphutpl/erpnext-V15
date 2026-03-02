# Copyright (c) 2013, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers

# -------------------- EXECUTE --------------------
def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

# -------------------- COLUMNS --------------------
def get_columns(filters=None):
    if filters.aggregate:
        if filters.report_by == "Sales Order":
            return [
                _("Branch") + ":Link/Branch:150",
                _("Sub Item Group") + ":Data:150",
                _("Sales Qty") + ":Float:120",
                _("Delivered Qty") + ":Float:120",
                _("Amount") + ":Currency:120"
            ]
        else:  # Sales Invoice / Delivery Note
            return [
                _("Branch") + ":Link/Branch:150",
                _("Sub Item Group") + ":Data:150",
                _("Delivered Qty") + ":Float:120",
                _("Amount") + ":Currency:120",
                _("Net Total") + ":Currency:120"
            ]

    elif filters.summary:
        if filters.report_by == "Sales Order":
            return [
                _("Posting Date") + ":Date:100",
                _("Sales Order") + ":Link/Sales Order:100",
                _("Cost Center") + ":Link/Cost Center:150",
                _("Branch") + ":Link/Branch:120",
                _("Customer") + ":Link/Customer:150",
                _("Customer Number") + ":Data:100",
                _("Customer Group") + ":Data:200",
                _("Sub Group") + ":Data:100",
                _("Qty Ordered") + ":Float:90",
                _("Qty Delivered") + ":Float:90",
                _("Amount") + ":Currency:100",
            ]
        elif filters.report_by == "Sales Invoice":
            return [
                _("Posting Date") + ":Date:100",
                _("Sales Invoice") + ":Link/Sales Invoice:100",
                _("Sales Order") + ":Link/Sales Order:100",
                _("Delivery Note") + ":Link/Delivery Note:100",
                _("Cost Center") + ":Link/Cost Center:150",
                _("Branch") + ":Link/Branch:120",
                _("Customer") + ":Link/Customer:150",
                _("Customer Number") + ":Data:100",
                _("Customer Group") + ":Data:200",
                _("Sub Group") + ":Data:100",
                _("Qty Delivered") + ":Float:90",
                _("GST Amount") + ":Currency:100", 
                _("Cash Discount Amount") + ":Currency:100",
                _("Transportation Charges") + ":Currency:100",
                _("Amount") + ":Currency:100",
                _("Net Total") + ":Currency:120",
                _("Grand Total") + ":Currency:120",
            ]
        else:  # Delivery Note
            return [
                _("Posting Date") + ":Date:100",
                _("Delivery Note") + ":Link/Delivery Note:100",
                _("Sales Order") + ":Link/Sales Order:100",
                _("Cost Center") + ":Link/Cost Center:150",
                _("Branch") + ":Link/Branch:120",
                _("Customer") + ":Link/Customer:150",
                _("Customer Number") + ":Data:100",
                _("Customer Group") + ":Data:200",
                _("Sub Group") + ":Data:100",
                _("Qty Delivered") + ":Float:90",
                _("Amount") + ":Currency:100",
            ]
    else:  # Detailed
        if filters.report_by == "Sales Order":
            return [
                _("Posting Date") + ":Date:100",
                _("Sales Order") + ":Link/Sales Order:100",
                _("Cost Center") + ":Link/Cost Center:150",
                _("Branch") + ":Link/Branch:120",
                _("Customer") + ":Link/Customer:150",
                _("Customer Group") + ":Data:200",
                _("Shipping Address") + ":Data:200",
                _("Item Code") + ":Link/Item:80",
                _("Item Name") + ":Data:150",
                _("Sub Group") + ":Data:100",
                _("Actual Qty") + ":Float:100",
                _("Qty Delivered") + ":Float:90",
                _("Rate") + ":Float:90",
                _("Amount") + ":Currency:100",
                _("Net Total") + ":Currency:120",
            ]
        elif filters.report_by == "Sales Invoice":
            return [
                _("Posting Date") + ":Date:100",
                _("Sales Invoice") + ":Link/Sales Invoice:100",
                _("Sales Order") + ":Link/Sales Order:100",
                _("Delivery Note") + ":Link/Delivery Note:100",
                _("Cost Center") + ":Link/Cost Center:150",
                _("Branch") + ":Link/Branch:120",
                _("Customer") + ":Link/Customer:150",
                _("Customer Group") + ":Data:200",
                _("Destination") + ":Data:200",
                _("Item Code") + ":Link/Item:80",
                _("Item Name") + ":Data:150",
                _("Sub Group") + ":Data:100",
                _("Qty Delivered") + ":Float:90",
                _("Rate") + ":Float:90",
                _("Amount") + ":Currency:100",
                _("Net Total") + ":Currency:120",
            ]
        else:  # Delivery Note
            return [
                _("Posting Date") + ":Date:100",
                _("Delivery Note") + ":Link/Delivery Note:100",
                _("Sales Order") + ":Link/Sales Order:100",
                _("Cost Center") + ":Link/Cost Center:150",
                _("Branch") + ":Link/Branch:120",
                _("Customer") + ":Link/Customer:150",
                _("Customer Group") + ":Data:200",
                _("Destination") + ":Data:200",
                _("Item Code") + ":Link/Item:80",
                _("Item Name") + ":Data:150",
                _("Sub Group") + ":Data:100",
                _("Qty Delivered") + ":Float:90",
                _("Rate") + ":Float:90",
                _("Amount") + ":Currency:100",
                _("Net Total") + ":Currency:120",
            ]

# -------------------- DATA --------------------
def get_data(filters=None):
    cond = get_conditions(filters)
    outer_cond = get_outer_cond(filters)

    if filters.report_by == "Sales Order":
        return get_sales_order_data(filters, cond, outer_cond)
    elif filters.report_by == "Sales Invoice":
        return get_sales_invoice_data(filters, cond, outer_cond)
    else:
        return get_delivery_note_data(filters, cond, outer_cond)

# -------------------- SALES ORDER --------------------
def get_sales_order_data(filters, cond, outer_cond):
    if filters.aggregate:
        cols = "so.branch, i.item_sub_group, sum(soi.qty) as qty, sum(soi.delivered_qty) as delivered_qty, sum(soi.amount) as amount"
        group_by = " GROUP BY so.branch, i.item_sub_group"
        order_by = ""
    elif filters.summary:
        cols = """
            so.transaction_date, so.name,
            (SELECT cc.parent_cost_center FROM `tabCost Center` cc WHERE cc.name = 
                (SELECT b.cost_center FROM `tabBranch` b WHERE b.name = so.branch)) AS region,
            so.branch, so.customer,
            (SELECT mobile_no FROM `tabCustomer` WHERE name=so.customer) AS customer_number,
            so.customer_group, i.item_sub_group,
            SUM(soi.qty) AS qty, SUM(soi.delivered_qty) AS delivered_qty,
            SUM(soi.amount) AS amount
        """
        group_by = " GROUP BY so.name"
        order_by = " ORDER BY so.transaction_date"

    else:
        cols = """
            so.transaction_date, so.name,
            (SELECT cc.parent_cost_center FROM `tabCost Center` cc WHERE cc.name = 
                (SELECT b.cost_center FROM `tabBranch` b WHERE b.name = so.branch)) AS region,
            so.branch, so.customer, 
            (SELECT customer_group FROM `tabCustomer` WHERE name = so.customer) AS customer_group,
            so.shipping_address_name,
            soi.item_code, soi.item_name, i.item_sub_group,
            soi.qty AS actual_qty, soi.delivered_qty, soi.rate, soi.amount, soi.amount AS net_total
        """
        group_by = " GROUP BY so.name, soi.item_code"
        order_by = " ORDER BY so.transaction_date"

    query = f"""
        SELECT * FROM (
            SELECT {cols}
            FROM `tabSales Order` so
            INNER JOIN `tabSales Order Item` soi ON so.name = soi.parent
            INNER JOIN `tabItem` i ON soi.item_code = i.name
            WHERE so.docstatus = 1 {cond}
            {group_by} {order_by}
        ) AS data WHERE 1=1 {outer_cond}
    """
    return frappe.db.sql(query)

# -------------------- SALES INVOICE --------------------
def get_sales_invoice_data(filters, cond, outer_cond):
    if filters.aggregate:
        cols = "si.branch, i.item_sub_group, SUM(sii.qty) AS delivered_qty, SUM(sii.amount) AS amount, SUM(si.net_total) AS net_total"
        group_by = " GROUP BY si.branch, i.item_sub_group"
        order_by = ""
    elif filters.summary:
        cols = """
            si.posting_date, si.name, sii.sales_order, sii.delivery_note,
            (SELECT cc.parent_cost_center FROM `tabCost Center` cc WHERE cc.name = 
                (SELECT b.cost_center FROM `tabBranch` b WHERE b.name = si.branch)) AS region,
            si.branch, si.customer,
            (SELECT mobile_no FROM `tabCustomer` WHERE name=si.customer) AS customer_number,
            si.customer_group, i.item_sub_group,
            SUM(sii.qty) AS delivered_qty,
            (SELECT SUM(st.tax_amount_after_discount_amount)
                FROM `tabSales Taxes and Charges` st
            WHERE st.parent = si.name 
                AND st.is_gst = 1 ) AS gst_amount,
            (SELECT SUM(st.tax_amount_after_discount_amount)
                FROM `tabSales Taxes and Charges` st
            WHERE st.parent = si.name 
                AND st.charge_type = 'On Total' AND st.is_gst = 0) AS cash_discount_amount,
            (SELECT SUM(st.tax_amount_after_discount_amount)
                FROM `tabSales Taxes and Charges` st
            WHERE st.parent = si.name 
                AND st.charge_type = 'Actual' AND st.is_gst = 0) AS transportation_charges,
            SUM(sii.amount) AS amount,
            si.net_total AS net_total,
            si.grand_total AS grand_total
        """
        group_by = " GROUP BY si.name"
        order_by = " ORDER BY si.posting_date"
    else:
        cols = """
            si.posting_date, si.name, sii.sales_order, sii.delivery_note,
            (SELECT cc.parent_cost_center FROM `tabCost Center` cc WHERE cc.name = 
                (SELECT b.cost_center FROM `tabBranch` b WHERE b.name = si.branch)) AS region,
            si.branch, si.customer, si.customer_group, si.shipping_address_name,
            sii.item_code, sii.item_name, i.item_sub_group,
            sii.qty AS delivered_qty, sii.rate, sii.amount, sii.net_amount
        """
        group_by = " GROUP BY si.name, sii.item_code"
        order_by = " ORDER BY si.posting_date"

    query = f"""
        SELECT * FROM (
            SELECT {cols}
            FROM `tabSales Invoice` si
            INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
            INNER JOIN `tabItem` i ON sii.item_code = i.name
            WHERE si.docstatus = 1 {cond}
            {group_by} {order_by}
        ) AS data WHERE 1=1 {outer_cond}
    """
    return frappe.db.sql(query)

# -------------------- DELIVERY NOTE --------------------
def get_delivery_note_data(filters, cond, outer_cond):
    if filters.aggregate:
        cols = "dn.branch, i.item_sub_group, SUM(dni.qty) AS delivered_qty, SUM(dni.amount) AS amount, SUM(dni.net_amount) AS net_total"
        group_by = " GROUP BY dn.branch, i.item_sub_group"
        order_by = ""
    elif filters.summary:
        cols = """
            dn.posting_date, dn.name, dni.against_sales_order,
            (SELECT cc.parent_cost_center FROM `tabCost Center` cc WHERE cc.name = 
                (SELECT b.cost_center FROM `tabBranch` b WHERE b.name = dn.branch)) AS region,
            dn.branch, dn.customer,
            (SELECT mobile_no FROM `tabCustomer` WHERE name=dn.customer) AS customer_number,
            dn.customer_group, i.item_sub_group,
            SUM(dni.qty) AS delivered_qty, SUM(dni.amount) AS amount
        """
        group_by = " GROUP BY dn.name"
        order_by = " ORDER BY dn.posting_date"
    else:
        cols = """
            dn.posting_date, dn.name, dni.against_sales_order,
            (SELECT cc.parent_cost_center FROM `tabCost Center` cc WHERE cc.name = 
                (SELECT b.cost_center FROM `tabBranch` b WHERE b.name = dn.branch)) AS region,
            dn.branch, dn.customer, dn.customer_group, dn.shipping_address_name,
            dni.item_code, dni.item_name, i.item_sub_group,
            dni.qty AS delivered_qty, dni.rate, dni.amount, dni.discount_amount AS discount,
            0 AS additional_cost, dni.net_amount AS net_total
        """
        group_by = " GROUP BY dn.name, dni.item_code"
        order_by = " ORDER BY dn.posting_date"

    query = f"""
        SELECT * FROM (
            SELECT {cols}
            FROM `tabDelivery Note` dn
            INNER JOIN `tabDelivery Note Item` dni ON dn.name = dni.parent
            INNER JOIN `tabItem` i ON dni.item_code = i.name
            WHERE dn.docstatus = 1 {cond}
            {group_by} {order_by}
        ) AS data WHERE 1=1 {outer_cond}
    """
    return frappe.db.sql(query)

# -------------------- CONDITIONS --------------------
def get_outer_cond(filters=None):
    outer_cond = ""
    if filters.get("volume"):
        outer_cond += " AND data.qty = {0}".format(filters.get("volume"))
    return outer_cond

def get_conditions(filters=None):
    cond = ""
    all_ccs = []

    if filters.from_date and filters.to_date:
        if filters.report_by == "Sales Order":
            cond += f" AND so.transaction_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND si.posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'"
        else:
            cond += f" AND dn.posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'"

    if filters.transaction_id:
        if filters.report_by == "Sales Order":
            cond += f" AND so.name='{filters.transaction_id}'"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND si.name='{filters.transaction_id}'"
        else:
            cond += f" AND dn.name='{filters.transaction_id}'"

    if filters.cost_center:
        all_ccs = get_child_cost_centers(filters.cost_center)
        tuple_cc = tuple(all_ccs)
        if filters.report_by == "Sales Order":
            cond += f" AND so.branch IN (SELECT name FROM `tabBranch` b WHERE b.cost_center IN {tuple_cc})"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND si.branch IN (SELECT name FROM `tabBranch` b WHERE b.cost_center IN {tuple_cc})"
        else:
            cond += f" AND dn.branch IN (SELECT name FROM `tabBranch` b WHERE b.cost_center IN {tuple_cc})"

    if filters.item_group:
        cond += f" AND i.item_group='{filters.item_group}'"
    if filters.customer:
        if filters.report_by == "Sales Order":
            cond += f" AND so.customer='{filters.customer}'"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND si.customer='{filters.customer}'"
        else:
            cond += f" AND dn.customer='{filters.customer}'"
    if filters.customer_group:
        if filters.report_by == "Sales Order":
            cond += f" AND so.customer_group='{filters.customer_group}'"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND si.customer_group='{filters.customer_group}'"
        else:
            cond += f" AND dn.customer_group='{filters.customer_group}'"
    if filters.item_sub_group:
        cond += f" AND i.item_sub_group='{filters.item_sub_group}'"
    if filters.item:
        cond += f" AND i.item_code='{filters.item}'"
    if filters.warehouse:
        if filters.report_by == "Sales Order":
            cond += f" AND soi.warehouse='{filters.warehouse}'"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND sii.warehouse='{filters.warehouse}'"
        else:
            cond += f" AND dni.warehouse='{filters.warehouse}'"
    if filters.branch:
        branch = str(filters.branch).replace(' - NRDCL', '')
        if filters.report_by == "Sales Order":
            cond += f" AND so.branch='{branch}'"
        elif filters.report_by == "Sales Invoice":
            cond += f" AND si.branch='{branch}'"
        else:
            cond += f" AND dn.branch='{branch}'"

    return cond
