# # Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# # For license information, please see license.txt
# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.utils import flt, getdate, formatdate, cstr
# from erpnext.fleet_management.report.fleet_management_report import get_pol_till, get_pol_consumed_till, get_pol_transfer
# # from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_till, get_pol_tills, get_pol_consumed_till, get_pol_transfer, get_pol_consumed_tills

# def execute(filters=None):
# 	columns = get_columns(filters);
# 	data = get_data(filters);

# 	return columns, data

# def get_data(filters=None):
# 	data = []
# 	query = "select e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type from tabEquipment e, `tabEquipment Type`et where e.equipment_type = et.name"
# 	if not filters.all_equipment:
# 		query += " and et.is_container = 1"
# 	if filters.branch:
# 		query += " and e.branch = \'" + str(filters.branch) + "\'"
		
# 	items = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where is_hsd_item = 1 and disabled = 0", as_dict=True)

# 	query += " order by e.branch"

# 	for eq in frappe.db.sql(query, as_dict=True):
# 		for item in items:
# 			received = issued = transfered = 0
# 			if filters.all_equipment:
# 				if eq.hsd_type == item.item_code:
# 					received = get_pol_till("Receive", eq.name, filters.to_date, item.item_code)
# 					issued = get_pol_consumed_till(eq.name, filters.to_date,)
# 					transfered = get_pol_transfer("Transfer", eq.name, item.item_code)
# 			else:
# 				received = get_pol_till("Stock", eq.name,filters.branch, filters.to_date, item.item_code)
# 				issued = get_pol_till("Issue", eq.name, filters.branch, filters.to_date, item.item_code)

# 			if received or issued or transfered:
# 				row = [eq.name, eq.registration_number, eq.equipment_type, eq.branch, item.item_code, item.item_name, item.stock_uom, received, issued, transfered, (flt(received) - flt(transfered) -flt(issued)) ]
# 				data.append(row)
# 	return data

# def get_columns(filters):
# 	cols = [
# 		{
# 			"fieldname": "equipment",
# 			"label": _("Equipment"),
# 			"fieldtype": "Link",
# 			"options": "Equipment",
# 			"width": 100
# 		},
# 		{
# 			"fieldname": "eq_name",
# 			"label": _("Equipment Name"),
# 			"fieldtype": "Data",
# 			"width": 130
# 		},
# 		{
# 			"fieldname": "eq_cat",
# 			"label": _("Equipment Type"),
# 			"fieldtype": "Data",
# 			"width": 130
#         },
# 		{
# 			"fieldname": "branch",
# 			"label": _("Branch"),
# 			"fieldtype": "Link",
# 			"options": "Branch",
# 			"width": 200
#         },
# 		{
# 			"fieldname": "pol_type",
# 			"label": _("Item Code"),
# 			"fieldtype": "Data",
# 			"width": 100
# 		},
# 		{
# 			"fieldname": "pol_name",
# 			"label": _("Item Name"),
# 			"fieldtype": "Data",
# 			"width": 170
#         },
# 		{
# 			"fieldname": "uom",
# 			"label": _("UOM"),
# 			"fieldtype": "Link",
# 			"options": "UOM",
# 			"width": 60
#         },
# 		{
# 			"fieldname": "received",
# 			"label": _("Received"),
# 			"fieldtype": "Float",
# 			"width": 100
#         },
# 	]

# 	if filters.all_equipment:
# 		cols.append({
# 				"fieldname": "issued",
# 				"label": _("Consumed"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})
# 	else:
# 		cols.append({
# 				"fieldname": "issued",
# 				"label": _("Issued"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})

# 	cols.append({
# 				"fieldname": "transfer",
# 				"label": _("Transfer"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})

# 	cols.append({
# 				"fieldname": "balance",
# 				"label": _("Balance"),
# 				"fieldtype": "Float",
# 				"width": 100
#             })


# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# For license information, please see license.txt
# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.utils import flt, getdate, formatdate, cstr
# # from erpnext.fleet_management.report.fleet_management_report import get_pol_till, get_pol_consumed_till, get_pol_transfer
# from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import get_pol_till,get_pol_tills, get_pol_consumed_till, get_pol_transfer, get_pol_consumed_tills

# def execute(filters=None):
# 	columns = get_columns(filters)
# 	data = get_data(filters)

# 	return columns, data

# def get_data(filters=None):
# 	data = []
# 	query = "select e.name, e.branch, e.registration_number, e.hsd_type, e.equipment_type from tabEquipment e, `tabEquipment Type`et where e.equipment_type = et.name"
# 	if not filters.all_equipment:
# 		query += " and et.is_container = 1"
# 	if filters.branch:
# 		query += " and e.branch = \'" + str(filters.branch) + "\'"
		
# 	items = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where is_hsd_item = 1 and disabled = 0", as_dict=True)

# 	query += " order by e.branch"

# 	for eq in frappe.db.sql(query, as_dict=True):
# 		for item in items:
# 			received = issued = transfered = 0
# 			if filters.all_equipment:
# 				if eq.hsd_type == item.item_code:
# 					received = get_pol_tills("Receive", eq.name,item.item_code,filters.to_date)
# 					issued = get_pol_consumed_till(eq.name, filters.to_date,)
# 					transfered = get_pol_transfer("Transfer", eq.name, item.item_code)
# 			else:
# 				received = get_pol_till("Stock", eq.name,filters.branch, filters.to_date, item.item_code)
# 				issued = get_pol_till("Issue", eq.name, filters.branch, filters.to_date, item.item_code)

# 			if received or issued or transfered:
# 				row = [eq.name, eq.registration_number, eq.equipment_type, eq.branch, item.item_code, item.item_name, item.stock_uom, received, issued, transfered, (flt(received) - flt(transfered) -flt(issued)) ]
# 				data.append(row)
# 	return data

# def get_columns(filters):
# 	cols = [
# 		{
# 			"fieldname": "equipment",
# 			"label": _("Equipment"),
# 			"fieldtype": "Link",
# 			"options": "Equipment",
# 			"width": 100
# 		},
# 		{
# 			"fieldname": "eq_name",
# 			"label": _("Equipment Name"),
# 			"fieldtype": "Data",
# 			"width": 130
# 		},
# 		{
# 			"fieldname": "eq_cat",
# 			"label": _("Equipment Type"),
# 			"fieldtype": "Data",
# 			"width": 130
# 		},
# 		{
# 			"fieldname": "branch",
# 			"label": _("Branch"),
# 			"fieldtype": "Link",
# 			"options": "Branch",
# 			"width": 200
# 		},
# 		{
# 			"fieldname": "pol_type",
# 			"label": _("Item Code"),
# 			"fieldtype": "Data",
# 			"width": 100
# 		},
# 		{
# 			"fieldname": "pol_name",
# 			"label": _("Item Name"),
# 			"fieldtype": "Data",
# 			"width": 170
# 		},
# 		{
# 			"fieldname": "uom",
# 			"label": _("UOM"),
# 			"fieldtype": "Link",
# 			"options": "UOM",
# 			"width": 60
# 		},
# 		{
# 			"fieldname": "received",
# 			"label": _("Received"),
# 			"fieldtype": "Float",
# 			"width": 100
# 		},
# 	]

# 	if filters.all_equipment:
# 		cols.append({
# 				"fieldname": "issued",
# 				"label": _("Consumed"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})
# 	else:
# 		cols.append({
# 				"fieldname": "issued",
# 				"label": _("Issued"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})

# 	cols.append({
# 				"fieldname": "transfer",
# 				"label": _("Transfer"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})
# 	# cols.append({
# 	# 	"fieldname": "adustment",
# 	# 	"label": _("Adjustment"),
# 	# 	"fieldtype": "Float",
# 	# 	"with": 100
# 	# })

# 	cols.append({
# 				"fieldname": "balance",
# 				"label": _("Balance"),
# 				"fieldtype": "Float",
# 				"width": 100
# 			})
# 	return cols




# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import (
    get_pol_till,
)


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_latest_opening(equipment, pol_type, to_date):
    """Return the latest submitted opening entry for equipment and POL item."""

    result = frappe.db.sql(
        """
        SELECT
            name,
            qty,
            posting_date,
            posting_time,
            creation
        FROM `tabPOL Entry`
        WHERE docstatus = 1
          AND is_opening = 1
          AND equipment = %s
          AND pol_type = %s
          AND posting_date <= %s
        ORDER BY
            posting_date DESC,
            posting_time DESC,
            creation DESC
        LIMIT 1
        """,
        (equipment, pol_type, to_date),
        as_dict=True
    )

    return result[0] if result else None


def get_pol_movements_after_opening(
    equipment, pol_type, to_date, opening, movement_types
):
    """
    Sum POL Entry movements up to to_date.

    If an opening exists, only count movements after its date/time.
    Transactions with the same posting date and time are ordered
    using creation as a tie-breaker.
    """

    types = tuple(movement_types)

    if not types:
        return 0

    placeholders = ", ".join(["%s"] * len(types))

    conditions = [
        "docstatus = 1",
        "equipment = %s",
        "pol_type = %s",
        "type IN ({})".format(placeholders),
        "is_opening = 0",
        "posting_date <= %s",
    ]

    params = [equipment, pol_type]
    params.extend(types)
    params.append(to_date)

    if opening:
        conditions.append(
            """
            (
                posting_date > %s
                OR (
                    posting_date = %s
                    AND (
                        posting_time > %s
                        OR (
                            posting_time = %s
                            AND creation > %s
                        )
                    )
                )
            )
            """
        )

        params.extend([
            opening.posting_date,
            opening.posting_date,
            opening.posting_time,
            opening.posting_time,
            opening.creation,
        ])

    sql = """
        SELECT COALESCE(SUM(qty), 0)
        FROM `tabPOL Entry`
        WHERE {}
    """.format(" AND ".join(conditions))

    return flt(frappe.db.sql(sql, tuple(params))[0][0])


def get_consumption_after_opening(equipment, to_date, opening):
    """
    Sum submitted Vehicle Logbook consumption up to to_date.

    Vehicle Logbook uses to_date for its transaction date.
    On the opening date, creation is used as a same-day ordering proxy.
    """

    conditions = [
        "docstatus = 1",
        "equipment = %s",
        "to_date <= %s",
    ]

    params = [equipment, to_date]

    if opening:
        conditions.append(
            """
            (
                to_date > %s
                OR (
                    to_date = %s
                    AND creation > %s
                )
            )
            """
        )

        params.extend([
            opening.posting_date,
            opening.posting_date,
            opening.creation,
        ])

    sql = """
        SELECT COALESCE(SUM(consumption), 0)
        FROM `tabVehicle Logbook`
        WHERE {}
    """.format(" AND ".join(conditions))

    return flt(frappe.db.sql(sql, tuple(params))[0][0])


def get_data(filters=None):
    data = []

    query = """
        SELECT
            e.name,
            e.branch,
            e.registration_number,
            e.hsd_type,
            e.equipment_type
        FROM tabEquipment e
        INNER JOIN `tabEquipment Type` et
            ON e.equipment_type = et.name
        WHERE 1 = 1
    """

    params = []

    if not filters.all_equipment:
        query += " AND et.is_container = 1"

    if filters.branch:
        query += " AND e.branch = %s"
        params.append(filters.branch)

    query += " ORDER BY e.branch"

    equipment_list = frappe.db.sql(
        query, tuple(params), as_dict=True
    )

    items = frappe.db.sql(
        """
        SELECT item_code, item_name, stock_uom
        FROM `tabItem`
        WHERE is_hsd_item = 1
          AND disabled = 0
        """,
        as_dict=True
    )

    for eq in equipment_list:
        for item in items:

            received = 0
            issued = 0
            transfered = 0
            adjustment = 0

            if filters.all_equipment:
                # Only report the HSD item assigned to this equipment.
                if eq.hsd_type != item.item_code:
                    continue

                opening = get_latest_opening(
                    eq.name,
                    item.item_code,
                    filters.to_date
                )

                if opening:
                    adjustment = flt(opening.qty)

                # Receipts after the opening timestamp.
                received = get_pol_movements_after_opening(
                    eq.name,
                    item.item_code,
                    filters.to_date,
                    opening,
                    ("Receive",)
                )

                # Consumption after the opening date/time.
                issued = get_consumption_after_opening(
                    eq.name,
                    filters.to_date,
                    opening
                )

                # Transfers after the opening timestamp.
                transfered = get_pol_movements_after_opening(
                    eq.name,
                    item.item_code,
                    filters.to_date,
                    opening,
                    ("Transfer",)
                )

            else:
                # Preserve the existing container report behavior.
                opening = None

                received = get_pol_till(
                    "Stock",
                    eq.name,
                    filters.branch,
                    filters.to_date,
                    item.item_code
                )

                issued = get_pol_till(
                    "Issue",
                    eq.name,
                    filters.branch,
                    filters.to_date,
                    item.item_code
                )

                # Preserve the existing transfer helper behavior.
                # Adjustment is used only in All Equipment mode.
                transfered = 0
                adjustment = 0

            balance = (
                flt(adjustment)
                + flt(received)
                - flt(issued)
                - flt(transfered)
            )

            if received or issued or transfered or adjustment:
                data.append([
                    eq.name,
                    eq.registration_number,
                    eq.equipment_type,
                    eq.branch,
                    item.item_code,
                    item.item_name,
                    item.stock_uom,
                    received,
                    adjustment,
                    issued,
                    transfered,
                    balance,
                ])

    return data


def get_columns(filters):
    cols = [
        {
            "fieldname": "equipment",
            "label": _("Equipment"),
            "fieldtype": "Link",
            "options": "Equipment",
            "width": 100
        },
        {
            "fieldname": "eq_name",
            "label": _("Equipment Name"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "eq_cat",
            "label": _("Equipment Type"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "branch",
            "label": _("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "width": 200
        },
        {
            "fieldname": "pol_type",
            "label": _("Item Code"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "pol_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 170
        },
        {
            "fieldname": "uom",
            "label": _("UOM"),
            "fieldtype": "Link",
            "options": "UOM",
            "width": 60
        },
        {
            "fieldname": "received",
            "label": _("Received"),
            "fieldtype": "Float",
            "width": 100
        },
        {
            "fieldname": "adjustment",
            "label": _("Adjustment"),
            "fieldtype": "Float",
            "width": 110
        },
    ]

    if filters.all_equipment:
        cols.append({
            "fieldname": "issued",
            "label": _("Consumed"),
            "fieldtype": "Float",
            "width": 100
        })
    else:
        cols.append({
            "fieldname": "issued",
            "label": _("Issued"),
            "fieldtype": "Float",
            "width": 100
        })

    cols.append({
        "fieldname": "transfer",
        "label": _("Transfer"),
        "fieldtype": "Float",
        "width": 100
    })

    cols.append({
        "fieldname": "balance",
        "label": _("Balance"),
        "fieldtype": "Float",
        "width": 100
    })

    return cols
