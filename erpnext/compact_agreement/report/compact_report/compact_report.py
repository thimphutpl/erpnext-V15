# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _

# def execute(filters=None):
#     if not filters:
#         filters = {}
    
#     columns = get_columns()
#     data = get_data(filters)
    
#     return columns, data
    
# def get_columns():
#     columns = [
#         {
#             "label": _("Fiscal Year"),
#             "fieldname": "fiscal_year",
#             "fieldtype": "Link",
#             "options": "Fiscal Year",
#             "width": 120,
#         },
#         {
#             "label": _("Agency"),
#             "fieldname": "agency",
#             "fieldtype": "Link",
#             "options": "Department",
#             "width": 120,
#         },
#         {
#             "label": _("Company"),
#             "fieldname": "company",
#             "fieldtype": "Link",
#             "options": "Company",
#             "width": 120,
#         },
#         {
#             "label": _("Object"),
#             "fieldname": "target",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Deliverables"),
#             "fieldname": "deliverables",
#             "fieldtype": "Data",
#             "width": 170,
#         },
#         {
#             "label": _("Date Line"),
#             "fieldname": "datelines",
#             "fieldtype": "Date",
#             "width": 120,
#         },
#         {
#             "label": _("Weightage"),
#             "fieldname": "weighted",
#             "fieldtype": "Percent",
#             "width": 120,
#         },
#         {
#             "label": _("Achieved"),
#             "fieldname": "achieved",
#             "fieldtype": "Percent",
#             "width": 120,
#         },
#         {
#             "label": _("Remarks"),
#             "fieldname": "remarks",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "label": _("Total Weightage"),
#             "fieldname": "total_weighted_percent",
#             "fieldtype": "Percent",
#             "width": 120,
#         },
#         {
#             "label": _("Total Achieved"),
#             "fieldname": "total_achieved_percent",
#             "fieldtype": "Percent",
#             "width": 120,
#         },
#     ]
#     return columns

# def get_data(filters):
#     conditions = get_conditions(filters)
    
#     query = """
#         SELECT 
#             ce.fiscal_year,
#             ce.agency,
#             ce.company,
#             ca.target,
#             ca.deliverables,
#             ca.datelines,
#             ca.weighted,
#             ca.achieved,
#             ca.remarks,
#             ce.total_weighted_percent,
#             ce.total_achieved_percent
#         FROM 
#             `tabCompact Evaluation` ce
#         JOIN 
#             `tabCompact Agreement Items Evaluation` ca
#         ON 
#             ce.name = ca.parent
#         WHERE
#             ce.docstatus = 1
#             {conditions}
#         ORDER BY
#             ce.fiscal_year, ce.agency, ca.idx
#     """.format(conditions=conditions)
    
#     data = frappe.db.sql(query, filters, as_dict=True)
    
#     return data

# def get_conditions(filters):
#     conditions = ""
    
#     if filters.get("fiscal_year"):
#         conditions += " AND ce.fiscal_year = %(fiscal_year)s"
#     if filters.get("agency"):
#         conditions += " AND ce.agency = %(agency)s"
#     if filters.get("company"):
#         conditions += " AND ce.company = %(company)s"
    
#     return conditions

# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data
    
def get_columns():
    columns = [
        {
            "label": _("Fiscal Year"),
            "fieldname": "fiscal_year",
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "width": 120,
        },
        {
            "label": _("Agency"),
            "fieldname": "agency",
            "fieldtype": "Link",
            "options": "Department",
            "width": 120,
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 120,
        },
        {
            "label": _("Objective"),
            "fieldname": "objective",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Deliverables"),
            "fieldname": "deliverables",
            "fieldtype": "Data",
            "width": 170,
        },
        {
            "label": _("Deadline"),
            "fieldname": "deadline",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Weightage"),
            "fieldname": "weightage",
            "fieldtype": "Percent",
            "width": 120,
        },
        {
            "label": _("Achieved"),
            "fieldname": "achieved",
            "fieldtype": "Percent",
            "width": 120,
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Total Weightage"),
            "fieldname": "total_weighted_percent",
            "fieldtype": "Percent",
            "width": 120,
        },
        {
            "label": _("Total Achieved"),
            "fieldname": "total_achieved_percent",
            "fieldtype": "Percent",
            "width": 120,
        },
    ]
    return columns

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            ce.fiscal_year,
            ce.agency,
            ce.company,
            ca.objective,
            ca.deliverables,
            ca.deadline,
            ca.weightage,
            ca.achieved,
            ca.remarks,
            ce.total_weighted_percent,
            ce.total_achieved_percent
        FROM 
            `tabCompact Evaluation` ce
        JOIN 
            `tabCompact Agreement Items Evaluation` ca
        ON 
            ce.name = ca.parent
        WHERE
            ce.docstatus = 1
            {conditions}
        ORDER BY
            ce.fiscal_year, ce.agency, ca.idx
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filters, as_dict=True)
    
    return data

def get_conditions(filters):
    conditions = ""
    
    if filters.get("fiscal_year"):
        conditions += " AND ce.fiscal_year = %(fiscal_year)s"
    if filters.get("agency"):
        conditions += " AND ce.agency = %(agency)s"
    if filters.get("company"):
        conditions += " AND ce.company = %(company)s"
    
    return conditions