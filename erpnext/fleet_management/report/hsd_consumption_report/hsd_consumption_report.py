# # Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.utils.data import get_first_day, get_last_day, add_days
# from frappe.utils import flt, getdate, formatdate, cstr
# from erpnext.fleet_management.report.fleet_management_report import (
#     get_km_till,
#     get_hour_till,
#     get_pol_till,
#     get_pol_between,
#     get_pol_consumed_till,
#     get_ini_km_till,
#     get_ini_hour_till
# )


# def execute(filters=None):
#     columns = get_columns()
#     query = construct_query(filters)
#     data = get_data(query, filters)

#     return columns, data


# def get_data(query, filters=None):
#     data = []
#     datas = frappe.db.sql(query, as_dict=True)
    
#     for d in datas:
#         own_cc = 0
#         if filters.own_cc:
#             own_cc = 1

#         # Fetch and handle None values gracefully
#         d.drawn = flt(get_pol_between("Receive", d.name, filters.from_date, filters.to_date, d.hsd_type, own_cc))
#         received_till = flt(get_pol_till("Receive", d.name, add_days(getdate(filters.from_date), -1), d.hsd_type))
#         consumed_till = flt(get_pol_consumed_till(d.name, add_days(getdate(filters.from_date), -1), filter_dry=own_cc))
#         consumed_till_end = flt(get_pol_consumed_till(d.name, filters.to_date, filter_dry=own_cc))
        
#         # Calculations
#         d.consumed = flt(consumed_till_end) - flt(consumed_till)
#         d.opening = flt(received_till) - flt(consumed_till)
#         # d.open_km = flt(get_km_till(d.name, add_days(getdate(filters.from_date), -1)))
#         # d.open_hr = flt(get_hour_till(d.name, add_days(getdate(filters.from_date), -1)))
#         d.open_km = flt(get_ini_km_till(d.name, getdate(filters.from_date)))
#         d.open_hr = flt(get_ini_hour_till(d.name, getdate(filters.from_date)))
#         d.close_km = flt(get_km_till(d.name, filters.to_date))
#         d.close_hr = flt(get_hour_till(d.name, filters.to_date))
        
#         # Fetch additional values with defaults
#         d.cap = flt(frappe.db.get_value("Equipment", d.equipment, "tank_capacity"), 0.0)
#         d.cap = flt(frappe.db.get_value("Equipment", d.equipment, "kph"), 0.0)
#         d.cap = flt(frappe.db.get_value("Equipment", d.equipment, "lph"), 0.0)
        
#         rate = frappe.db.sql("""
#             SELECT (SUM(pol.qty * pol.rate) / SUM(pol.qty)) AS rate 
#             FROM `tabPOL Receive` pol 
#             WHERE pol.branch = %s AND pol.docstatus = 1 AND pol.pol_type = %s
#         """, (d.branch, d.hsd_type))
#         d.rate = rate and flt(rate[0][0]) or 0.0
        
#         vl_records = frappe.db.sql("""
#             SELECT place , hsd_amount
#             FROM `tabVehicle Logbook` 
#             WHERE equipment = %s AND docstatus = 1 
#             ORDER BY to_date DESC LIMIT 1
#         """, d.name, as_dict=1)
#         d.place = vl_records and vl_records[0].get('place', "") or ""
#         d.hsd_amount = vl_records and vl_records[0].get('hsd_amount', "") or ""
        
#         ys_records = frappe.db.sql("""
#             SELECT hci.yard_hours, hci.yard_distance 
#             FROM `tabHire Charge Item` hci, `tabHire Charge Parameter` hcp 
#             WHERE hcp.name = hci.parent 
#             AND hcp.equipment_type = %s 
#             AND hcp.equipment_model = %s 
#             AND (%s BETWEEN from_date AND IFNULL(to_date, CURDATE()) OR %s BETWEEN from_date AND IFNULL(to_date, CURDATE()))
#         """, (d.equipment_type, d.equipment_model, filters.from_date, filters.to_date), as_dict=1)
#         d.yskm = ys_records and flt(ys_records[0].get('yard_distance'), 0.0) or 0.0
#         d.yshour = ys_records and flt(ys_records[0].get('yard_hours'), 0.0) or 0.0

#         # Calculate HSD Amount safely
#         d.hsd_amount = flt(d.consumed) * flt(d.rate)
        
#         # row = [
#         #     d.name, d.equipment_category, d.equipment_type, d.registration_number, d.place,
#         #     "{0}/{1}".format(d.open_km, d.open_hr), "{0}/{1}".format(d.close_km, d.close_hr),
#         #     round(d.close_km - d.open_km, 2), round(d.close_hr - d.open_hr, 2),
#         #     round(flt(d.drawn), 2), round(flt(d.opening), 2), round(flt(d.drawn + d.opening), 2),
#         #     d.yskm, d.yshour, round(d.consumed, 2), round(flt(d.closing), 2),
#         #     flt(d.cap), round(flt(d.rate), 2), round(flt(d.rate) * flt(d.consumed), 2),
#         #     round(d.hsd_amount, 2),  # HSD Amount
#         # ]
#         consumed_lph = round(round(d.close_hr - d.open_hr, 2) * d.lph, 2)
#         d.closing = flt(d.opening) + flt(d.drawn) - flt(d.consumed) - flt(consumed_lph)
#         row = [
#             d.name, d.equipment_category, d.equipment_type, d.registration_number, d.place,
#             "{0}/{1}".format(d.open_km, d.open_hr), 
#             "{0}/{1}".format(d.close_km, d.close_hr),
#             round(d.close_km - d.open_km, 2), 
#             round(d.close_hr - d.open_hr, 2),
#             round(flt(d.drawn), 2), 
#             round(flt(d.opening), 2), 
#             round(flt(d.drawn + d.opening), 2),
#             d.kph, d.lph, 
#             round(d.consumed, 2), 
#             consumed_lph, 
#             round(consumed_lph + round(d.consumed, 2), 2), 
#             round(flt(d.closing), 2),
#             d.tank_capacity, 
#             round(flt(d.rate), 2), 
#             round(flt(d.rate) * flt(d.consumed), 2),
#             round(d.hsd_amount, 2),  # HSD Amount
#         ]
#         data.append(row)
#     return data




# def construct_query(filters):
#     query = """SELECT e.name, eh.branch, e.equipment_category, e.hsd_type, e.tank_capacity, e.lph, e.kph,
#         e.registration_number, e.equipment_type, e.equipment_model 
#         FROM `tabEquipment History` eh, `tabEquipment` e 
#         WHERE eh.parent = e.name """
#     if filters.get("branch"):
#         query += f" AND eh.branch = '{filters.branch}'"

#     if filters.get("from_date") and filters.get("to_date"):
#         query += f" AND ('{filters.to_date}' >= IFNULL(eh.from_date, CURDATE()) AND '{filters.from_date}' <= IFNULL(eh.to_date, CURDATE()))"

#     if not filters.include_disabled:
#         query += " AND e.is_disabled = 0"

#     if filters.not_cdcl:
#         query += " AND e.not_cdcl = 0"

#     query += " GROUP BY e.name, eh.branch ORDER BY e.equipment_category, e.equipment_type ASC"
#     return query


# def get_columns():
#     columns = [
#         {
#             "label": _("Equipment"),
#             "fieldname": "equipment",
#             "fieldtype": "Link",
#             "options": "Equipment",
#             "width": 120,
#         },
#         {
#             "label": _("Equipment Category"),
#             "fieldname": "equipment_category",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "label": _("Equipment Type"),
#             "fieldname": "equipment_type",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "label": _("Registration No"),
#             "fieldname": "registration_number",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "label": _("Location"),
#             "fieldname": "location",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "label": _("Initial KM/H"),
#             "fieldname": "initial_km_hr",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Final KM/H"),
#             "fieldname": "final_km_hr",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("KM"),
#             "fieldname": "km",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Hour"),
#             "fieldname": "hour",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("HSD Drawn (L)"),
#             "fieldname": "hsd_drawn",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Prev Bal (L)"),
#             "fieldname": "prev_bal",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Total HSD (L)"),
#             "fieldname": "total_hsd",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         # {
#         #     "label": _("Per KM"),
#         #     "fieldname": "per_km",
#         #     "fieldtype": "Data",
#         #     "width": 110,
#         # },
#         # {
#         #     "label": _("Per Hour"),
#         #     "fieldname": "per_hour",
#         #     "fieldtype": "Data",
#         #     "width": 110,
#         # },
#         {
#             "label": _("Per KM"),
#             "fieldname": "kph",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("Per Hour"),
#             "fieldname": "lph",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("HSD Consumption (Km)"),
#             "fieldname": "hsd_consumption_km",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("HSD Consumption (Hr)"),
#             "fieldname": "hsd_consumption_hr",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("HSD Consumption"),
#             "fieldname": "hsd_consumption",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("Closing Bal (L)"),
#             "fieldname": "closing_bal",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("Tank Capacity"),
#             "fieldname": "tank_capacity",
#             "fieldtype": "Data",
#             "width": 110,
#         },
#         {
#             "label": _("Rate (Nu.)"),
#             "fieldname": "rate",
#             "fieldtype": "Currency",
#             "width": 100,
#         },
#         {
#             "label": _("Amount (Nu.)"),
#             "fieldname": "amount",
#             "fieldtype": "Currency",
#             "width": 100,
#         },
#         {
#             "label": _("HSD Amount"),
#             "fieldname": "hsd_amount",
#             "fieldtype": "Data",
#             "width": 120,
#         },
#     ]
#     return columns





# @frappe.whitelist()
# def fetch_tank_balance_from_hsd(equipment):
#     if not equipment:
#         frappe.throw("Equipment is required to fetch Tank Balance.")

#     closing = frappe.db.get_value("HSD Consumption Report", {"equipment": equipment}, "closing")
    
#     if closing is None:
#         frappe.throw(f"No HSD Consumption Report entry found for the selected equipment: {equipment}")

#     return closing



#Copyright (c) 2024

# from __future__ import unicode_literals
# import frappe
# from frappe import _
# from frappe.utils.data import add_days
# from frappe.utils import flt, getdate

# from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import (
#     get_km_till,
#     get_hour_till,
#     get_pol_till,
#     get_pol_between,
#     get_pol_consumed_till,
# )


# def execute(filters=None):
#     columns = get_columns()
#     query = construct_query(filters)
#     data = get_data(query, filters)
#     return columns, data


# def get_data(query, filters=None):
#     data = []
#     datas = frappe.db.sql(query, as_dict=True)

#     for d in datas:

#         # ---------------- SAFE VALUES ----------------
#         d.drawn = flt(get_pol_between(
#             "Receive", d.name, filters.from_date, filters.to_date, d.hsd_type
#         ))

#         received_till = flt(get_pol_till(
#             "Receive",
#             d.name,
#             d.branch,
#             add_days(getdate(filters.from_date), -1),
#             d.hsd_type
#         ))

#         consumed_till = flt(get_pol_consumed_till(
#             d.name,
#             add_days(getdate(filters.from_date), -1)
#         ))

#         consumed_till_end = flt(get_pol_consumed_till(
#             d.name,
#             filters.to_date
#         ))

#         # ---------------- CALCULATIONS ----------------
#         d.consumed = consumed_till_end - consumed_till
#         d.opening = received_till - consumed_till

#         # SAFE KM / HR
#         d.open_km = flt(get_km_till(d.name, add_days(getdate(filters.from_date), -1))) or 0
#         d.open_hr = flt(get_hour_till(d.name, add_days(getdate(filters.from_date), -1))) or 0

#         d.close_km = flt(get_km_till(d.name, filters.to_date)) or 0
#         d.close_hr = flt(get_hour_till(d.name, filters.to_date)) or 0

#         # Equipment values
#         d.tank_capacity = flt(frappe.db.get_value("Equipment", d.name, "tank_capacity")) or 0
#         d.kph = flt(frappe.db.get_value("Equipment", d.name, "kph")) or 0
#         d.lph = flt(frappe.db.get_value("Equipment", d.name, "lph")) or 0

#         # RATE
#         rate = frappe.db.sql("""
#             SELECT (SUM(pol.qty * pol.rate) / SUM(pol.qty))
#             FROM `tabPOL Receive` pol
#             WHERE pol.branch = %s AND pol.docstatus = 1 AND pol.pol_type = %s
#         """, (d.branch, d.hsd_type))

#         d.rate = flt(rate[0][0]) if rate and rate[0][0] else 0

#         # ---------------- FINAL CALC ----------------
#         total_hr = d.close_hr - d.open_hr
#         consumed_lph = round(total_hr * d.lph, 2)

#         d.closing = d.opening + d.drawn - d.consumed - consumed_lph

#         # ---------------- ROW ----------------
#         row = [
#             d.name,
#             d.equipment_category,
#             d.equipment_type,
#             d.registration_number,

#             round(d.close_km - d.open_km, 2),
#             round(total_hr, 2),

#             round(d.drawn, 2),
#             round(d.opening, 2),
#             round(d.drawn + d.opening, 2),

#             d.kph,
#             d.lph,

#             round(d.consumed, 2),
#             consumed_lph,
#             round(consumed_lph + d.consumed, 2),

#             round(d.closing, 2),

#             d.tank_capacity,
#             round(d.rate, 2),
#             round(d.rate * d.consumed, 2),
#         ]

#         data.append(row)

#     return data


# def construct_query(filters):
#     query = """
#         SELECT 
#             e.name, eh.branch, e.equipment_category, e.hsd_type,
#             e.tank_capacity, e.lph, e.kph,
#             e.registration_number, e.equipment_type, e.equipment_model
#         FROM `tabEquipment History` eh, `tabEquipment` e
#         WHERE eh.parent = e.name
#     """

#     if filters.get("branch"):
#         query += f" AND eh.branch = '{filters.branch}'"

#     if filters.get("from_date") and filters.get("to_date"):
#         query += f"""
#             AND ('{filters.to_date}' >= IFNULL(eh.from_date, CURDATE())
#             AND '{filters.from_date}' <= IFNULL(eh.to_date, CURDATE()))
#         """

#     if not filters.get("include_disabled"):
#         query += " AND e.is_disabled = 0"

#     if filters.get("not_cdcl"):
#         query += " AND e.not_cdcl = 0"

#     query += " GROUP BY e.name, eh.branch ORDER BY e.equipment_category, e.equipment_type"

#     return query


# def get_columns():
#     return [
#         {"label": _("Equipment"), "fieldtype": "Data", "width": 140},
#         {"label": _("Category"), "fieldtype": "Data", "width": 120},
#         {"label": _("Type"), "fieldtype": "Data", "width": 120},
#         {"label": _("Reg No"), "fieldtype": "Data", "width": 120},

#         {"label": _("KM"), "fieldtype": "Float", "width": 100},
#         {"label": _("Hour"), "fieldtype": "Float", "width": 100},

#         {"label": _("HSD Drawn"), "fieldtype": "Float", "width": 110},
#         {"label": _("Opening"), "fieldtype": "Float", "width": 110},
#         {"label": _("Total"), "fieldtype": "Float", "width": 110},

#         {"label": _("KPH"), "fieldtype": "Float", "width": 90},
#         {"label": _("LPH"), "fieldtype": "Float", "width": 90},

#         {"label": _("Cons (KM)"), "fieldtype": "Float", "width": 110},
#         {"label": _("Cons (HR)"), "fieldtype": "Float", "width": 110},
#         {"label": _("Total Cons"), "fieldtype": "Float", "width": 110},

#         {"label": _("Closing"), "fieldtype": "Float", "width": 110},

#         {"label": _("Tank Cap"), "fieldtype": "Float", "width": 100},
#         {"label": _("Rate"), "fieldtype": "Currency", "width": 100},
#         {"label": _("Amount"), "fieldtype": "Currency", "width": 120},
#     ]






from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import get_first_day, get_last_day, add_days
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.fleet_management.report.hsd_consumption_report.fleet_management_report import (
    get_km_till,
    get_hour_till,
    get_pol_tills,
    get_pol_between,
    get_pol_consumed_till,
    get_pol_consumed_tills_op,
    get_km_after_opening,
    get_hour_after_opening,
    get_pol_between_opening,
    get_initial_km_hr
    
)


def execute(filters=None):
	columns = get_columns()
	query = construct_query(filters)
	data = get_data(query, filters)

	return columns,data


# def get_data(query, filters=None):
# 	data = []
# 	datas = frappe.db.sql(query, as_dict=True);
# 	for d in datas:
# 		own_cc = 0
# 		if filters.own_cc:
# 			own_cc = 1
# 		#d.drawn = get_pol_between("Receive", d.name, filters.from_date, filters.to_date, d.hsd_type, own_cc)
# 		# HSD received during the selected period
# 		opening_date = add_days(getdate(filters.from_date), -1)

# 		d.drawn = get_pol_between("Receive",d.name,filters.from_date,filters.to_date,d.hsd_type,own_cc)

# 		#received_till = get_pol_tills("Receive", d.name, add_days(getdate(filters.from_date), -1), d.hsd_type)
# 		#received_till = get_pol_tills( "Receive", d.name, opening_date, d.hsd_type )
# 		# Previous HSD Received
# 		# received_till = frappe.db.sql(""" SELECT COALESCE(SUM(pr.qty), 0) FROM `tabPOL Receive` pr WHERE pr.docstatus = 1 AND pr.equipment = %s AND pr.pol_type = %s AND pr.posting_date <= %s
# 		# """, ( d.name, d.hsd_type, opening_date ))[0][0] or 0
# 		received_till = frappe.db.sql(""" SELECT COALESCE(SUM(qty), 0) FROM `tabPOL Entry` WHERE docstatus = 1 AND type = 'Receive' AND equipment = %s AND posting_date <= %s
# 		AND pol_type = %s """, ( d.name, opening_date, d.hsd_type ))[0][0] or 0


# 		#consumed_till = get_pol_consumed_till(d.name, add_days(getdate(filters.from_date), -1), filter_dry=own_cc)
# 		consumed_till = get_pol_consumed_till( d.name, opening_date, filter_dry=own_cc ) 
# 		d.opening = flt(received_till) - flt(consumed_till)
		

# 		# frappe.log_error(	title="Opening Balance Check",	message=f""" Equipment: {d.name} HSD Type: {d.hsd_type} Opening Date: {opening_date} Received Till: {received_till}
# 		# Consumed Till: {consumed_till} Opening Balance: {d.opening} """)


# 		#consumed_till_end = get_pol_consumed_till(d.name, filters.to_date, filter_dry=own_cc)
# 		# HSD consumed during the selected period
# 		consumed_till_end = get_pol_consumed_till(d.name,filters.to_date,filter_dry=own_cc)
# 		d.consumed = flt(consumed_till_end) - flt(consumed_till)

# 		# received_to_date = get_pol_tills("Receive",d.name,filters.to_date,d.hsd_type)
# 		# consumed_to_date = get_pol_consumed_till(d.name,filters.to_date,filter_dry=own_cc)

# 		# Closing balance as of To Date
# 		#d.closing = (flt(d.opening)+ flt(d.drawn) - flt(d.consumed))
		
# 		# Closing balance as of To Date
# 		# # Use POL opening entry only when one exists for this equipment.
# 		opening_entry = frappe.db.sql(
# 			 """
# 			 SELECT name, posting_date, qty
# 			 FROM `tabPOL Entry`
# 			 WHERE docstatus = 1
# 			 AND is_opening = 1
# 			 AND equipment = %s
# 			 AND pol_type = %s
# 			 AND posting_date <= %s
# 			 ORDER BY posting_date DESC, creation DESC
# 			 LIMIT 1
# 			 """,
# 			 (d.name, d.hsd_type, filters.to_date),
# 			 as_dict=True,
# 			 )
# 		if opening_entry:
# 			opening_date = getdate(opening_entry[0].posting_date)
# 			opening_qty = flt(opening_entry[0].qty)
# 			# Receipts after the opening date
# 			received_after_opening = frappe.db.sql(
# 				"""
# 				SELECT COALESCE(SUM(qty), 0)
# 				FROM `tabPOL Entry`
# 				WHERE docstatus = 1
# 				AND type = 'Receive'
# 				AND equipment = %s
# 				AND pol_type = %s
# 				AND posting_date > %s
# 				AND posting_date <= %s
# 				AND IFNULL(is_opening, 0) = 0
# 				""",
# 				(d.name, d.hsd_type, opening_date, filters.to_date),
# 				)[0][0] or 0
# 			# Consumption after the opening date
# 			consumed_after_opening = frappe.db.sql(
# 				"""
# 				SELECT COALESCE(SUM(consumption), 0)
# 				FROM `tabVehicle Logbook`
# 				WHERE docstatus = 1
# 				AND equipment = %s
# 				AND to_date > %s
# 				AND to_date <= %s
# 				""",
# 				(d.name, opening_date, filters.to_date),
# 				)[0][0] or 0
# 			d.closing = (
# 				opening_qty
# 				+ flt(received_after_opening)
# 				- flt(consumed_after_opening)
# 				)
# 		else:
# 			d.closing = (
# 				flt(d.opening)
# 				+ flt(d.drawn)
# 				- flt(d.consumed)
# 			)

		





# 		#d.consumed = flt(consumed_till_end) - flt(consumed_till)
# 		#d.opening = flt(received_till) - flt(consumed_till)
# 		#d.closing = flt(d.opening) + flt(d.drawn) - flt(d.consumed)
# 		d.open_km = get_km_till(d.name, add_days(getdate(filters.from_date), -1))
# 		d.open_hr = get_hour_till(d.name, add_days(getdate(filters.from_date), -1))
# 		#d.tank_capacity = flt(frappe.db.get_value("Equipment", d.name, "tank_capacity")) or 0

# 		d.close_km = get_km_till(d.name, filters.to_date)
# 		d.close_hr = get_hour_till(d.name, filters.to_date)

# 		d.cap = frappe.db.get_value("Equipment", d.name, "tank_capacity")
# 		# rate = frappe.db.sql("select (sum(pol.qty*pol.rate)/sum(pol.qty)) as rate from tabPOL Receive pol where pol.branch = %s and pol.docstatus = 1 and pol.pol_type = %s", (d.branch, d.hsd_type))
# 		rate = frappe.db.sql("""SELECT (SUM(pol.qty * pol.rate) / SUM(pol.qty)) AS rate FROM `tabPOL Receive` pol WHERE pol.branch = %s AND pol.docstatus = 1 AND pol.pol_type = %s""", (d.branch, d.hsd_type))
# 		d.rate = rate and flt(rate[0][0]) or 0.0
	
# 		vl_records = frappe.db.sql("select place from `tabVehicle Logbook` where equipment = %s and docstatus = 1 order by to_date desc limit 1", d.name, as_dict=1)
# 		d.place = vl_records and flt(vl_records[0].place) or ""
# 		d.yskm = frappe.db.get_value("Equipment", d.name, "kph")	
# 		d.yshour = frappe.db.get_value("Equipment", d.name, "lph")
# 		# ys_records = frappe.db.sql("select hci.yard_hours, hci.yard_distance from `tabHire Charge Item` hci, `tabHire Charge Parameter` hcp where hcp.name = hci.parent and hcp.equipment_type = %s and hcp.equipment_model = %s and (%s between from_date and ifnull(to_date, curdate()) or %s between from_date and ifnull(to_date, curdate()))", (d.equipment_type, d.equipment_model, filters.from_date, filters.to_date), as_dict=1)
# 		# d.yskm = ys_records and flt(ys_records[0].yard_distance) or 0
# 		# d.yshour = ys_records and flt(ys_records[0].yard_hours) or 0
	
# 		row = [d.name, d.equipment_category, d.equipment_type, d.registration_number,  ("{0}" '/' "{1}".format(d.open_km, d.open_hr)), ("{0}" '/' "{1}".format(d.close_km,d.close_hr)), round(d.close_km-d.open_km,2), round(d.close_hr-d.open_hr,2),
# 		round(flt(d.drawn),2), round(flt(d.opening),2), round((flt(d.drawn)+flt(d.opening)),2),
# 		d.yskm, d.yshour, round(d.consumed,2), round(flt(d.closing),2), flt(d.cap), round(flt(d.rate),2), round((flt(d.rate)*flt(d.consumed)),2)]
# 		data.append(row);
# 	return data

# added by kinzag. 

def get_data(query, filters=None):
    data = []
    datas = frappe.db.sql(query, as_dict=True)

    previous_date = add_days(getdate(filters.from_date), -1)
    own_cc = 1 if filters.get("own_cc") else 0

    for d in datas:
        # --------------------------------------------------
        # Find the latest submitted opening POL Entry
        # --------------------------------------------------
        opening_entries = frappe.db.sql(
            """
            SELECT name, posting_date, posting_time, qty
            FROM `tabPOL Entry`
            WHERE docstatus = 1
              AND IFNULL(is_opening, 0) = 1
              AND equipment = %s
              AND pol_type = %s
              AND posting_date <= %s
            ORDER BY posting_date DESC, posting_time DESC, creation DESC
            LIMIT 1
            """,
            (d.name, d.hsd_type, filters.to_date),
            as_dict=True,
        )

        opening_entry = opening_entries[0] if opening_entries else None

        # --------------------------------------------------
        # Opening-entry equipment
        # --------------------------------------------------
        if opening_entry:
            baseline_date = getdate(opening_entry.posting_date)
            baseline_time = str(
                opening_entry.posting_time or "00:00:00"
            )
            opening_qty = flt(opening_entry.qty)

            # Receipts after the opening timestamp and up to
            # the day before the report starts.
            received_before_period = frappe.db.sql(
                """
                SELECT COALESCE(SUM(qty), 0)
                FROM `tabPOL Entry`
                WHERE docstatus = 1
                  AND type = 'Receive'
                  AND IFNULL(is_opening, 0) = 0
                  AND equipment = %s
                  AND pol_type = %s
                  AND (
                        posting_date > %s
                        OR (
                            posting_date = %s
                            AND posting_time > %s
                        )
                  )
                  AND posting_date <= %s
                """,
                (
                    d.name,
                    d.hsd_type,
                    baseline_date,
                    baseline_date,
                    baseline_time,
                    previous_date,
                ),
            )[0][0] or 0

            # Consumption after the opening date, through
            # the previous date.
            if previous_date >= baseline_date:
                consumed_before_period = flt(
                    get_pol_consumed_tills_op(
                        d.name, baseline_date, previous_date
                    )
                )

                d.opening = (
                    opening_qty
                    + flt(received_before_period)
                    - consumed_before_period
                )
            else:
                # The opening entry is within the selected
                # report period, so start from its quantity.
                d.opening = opening_qty

            # HSD receipts during the selected period,
            # excluding receipts before the opening timestamp.
            d.drawn = flt(
                get_pol_between_opening(
                    "Receive",
                    d.name,
                    d.hsd_type,
                    baseline_date,
                    baseline_time,
                    filters.from_date,
                    filters.to_date,
                )
            )
            initial_reading = get_initial_km_hr(
                d.name,
                filters.from_date,
                filters.to_date,
            )
            d.open_km = flt(initial_reading.final_km) if initial_reading else 0
            d.open_hr = flt(initial_reading.final_hour) if initial_reading else 0
            # d.open_km = (
            #     flt(initial_reading.final_km)
            #     if initial_reading else 0
                   
			# )
            # d.open_hr = (
			# 	flt(initial_reading.final_hour)
            #     if initial_reading else 0
                   
			# )
            d.close_km = flt(
				get_km_after_opening(
                    d.name, baseline_date, baseline_time, filters.to_date
    			)
			)
            d.close_hr = flt(
                get_hour_after_opening(
                    d.name, baseline_date, baseline_time, filters.to_date
    			)   
                   
			)
                   
			

            # Keep the opening-aware KM/hour functions.
            # d.open_km = flt(
            #     get_km_after_opening(
            #         d.name, baseline_date, baseline_time, previous_date
            #     )
            # )
            # d.close_km = flt(
            #     get_km_after_opening(
            #         d.name, baseline_date, baseline_time, filters.to_date
            #     )
            # )
            # d.open_hr = flt(
            #     get_hour_after_opening(
            #         d.name, baseline_date, baseline_time, previous_date
            #     )
            # )
            # d.close_hr = flt(
            #     get_hour_after_opening(
            #         d.name, baseline_date, baseline_time, filters.to_date
            #     )
            # )

            # Consumption in the selected period, measured
            # from the opening date onward.
            consumed_to_date = flt(
                get_pol_consumed_tills_op(
                    d.name, baseline_date, filters.to_date
                )
            )

            if previous_date >= baseline_date:
                consumed_to_previous = flt(
                    get_pol_consumed_tills_op(
                        d.name, baseline_date, previous_date
                    )
                )
            else:
                consumed_to_previous = 0

            d.consumed = max(
                0, consumed_to_date - consumed_to_previous
            )

        # --------------------------------------------------
        # Equipment without an opening entry:
        # retain the original calculation
        # --------------------------------------------------
        else:
            received_before_period = frappe.db.sql(
                """
                SELECT COALESCE(SUM(qty), 0)
                FROM `tabPOL Entry`
                WHERE docstatus = 1
                  AND type = 'Receive'
                  AND equipment = %s
                  AND pol_type = %s
                  AND posting_date <= %s
                """,
                (d.name, d.hsd_type, previous_date),
            )[0][0] or 0

            consumed_before_period = flt(
                get_pol_consumed_till(
                    d.name, previous_date, filter_dry=own_cc
                )
            )
            consumed_to_date = flt(
                get_pol_consumed_till(
                    d.name, filters.to_date, filter_dry=own_cc
                )
            )

            d.opening = (
                flt(received_before_period) - consumed_before_period
            )
            d.drawn = flt(
                get_pol_between(
                    "Receive",
                    d.name,
                    filters.from_date,
                    filters.to_date,
                    d.hsd_type,
                    own_cc,
                )
            )
            d.consumed = consumed_to_date - consumed_before_period

            d.open_km = flt(get_km_till(d.name, previous_date))
            d.close_km = flt(get_km_till(d.name, filters.to_date))
            d.open_hr = flt(get_hour_till(d.name, previous_date))
            d.close_hr = flt(get_hour_till(d.name, filters.to_date))

        # --------------------------------------------------
        # Equipment details
        # --------------------------------------------------
        d.tank_capacity = flt(
            frappe.db.get_value("Equipment", d.name, "tank_capacity")
        )
        d.kph = flt(
            frappe.db.get_value("Equipment", d.name, "kph")
        )
        d.lph = flt(
            frappe.db.get_value("Equipment", d.name, "lph")
        )

        rate = frappe.db.sql(
            """
            SELECT SUM(pol.qty * pol.rate) / NULLIF(SUM(pol.qty), 0)
            FROM `tabPOL Receive` pol
            WHERE pol.branch = %s
              AND pol.docstatus = 1
              AND pol.pol_type = %s
            """,
            (d.branch, d.hsd_type),
        )
        d.rate = flt(rate[0][0]) if rate and rate[0][0] else 0

        vl_records = frappe.db.sql(
            """
            SELECT place
            FROM `tabVehicle Logbook`
            WHERE equipment = %s
              AND docstatus = 1
            ORDER BY to_date DESC
            LIMIT 1
            """,
            (d.name,),
            as_dict=True,
        )
        d.place = vl_records[0].place or "" if vl_records else ""

        # --------------------------------------------------
        # Final balance and report row
        # --------------------------------------------------
        d.closing = flt(d.opening) + flt(d.drawn) - flt(d.consumed)

        row = [
            d.name,
            d.equipment_category,
            d.equipment_type,
            d.registration_number,
            "{0}/{1}".format(d.open_km, d.open_hr),
            "{0}/{1}".format(d.close_km, d.close_hr),
            round(flt(d.close_km) - flt(d.open_km), 2),
            round(flt(d.close_hr) - flt(d.open_hr), 2),
            round(flt(d.drawn), 2),
            round(flt(d.opening), 2),
            round(flt(d.drawn) + flt(d.opening), 2),
            d.kph,
            d.lph,
            round(flt(d.consumed), 2),
            round(flt(d.closing), 2),
            d.tank_capacity,
            round(flt(d.rate), 2),
            round(flt(d.rate) * flt(d.consumed), 2),
        ]
        data.append(row)

    return data


#till here



	#KM and Hour value is changed from consumption_km and consumption_hours to diference between the final and initial after discussing with Project Lead
def construct_query(filters):
	#(select (sum(pol.qty*pol.rate)/sum(pol.qty)) from tabPOL pol where pol.branch = vl.branch and pol.docstatus = 1 and pol.pol_type = e.hsd_type) as rate, e.hsd_type,
	query = """select e.name, eh.branch, e.equipment_category, e.hsd_type, e.registration_number, e.equipment_type, e.equipment_model 
		from `tabEquipment History` eh, tabEquipment e 
		where eh.parent = e.name """
	if filters.get("branch"):
		query += " and eh.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		# query += " and (eh.from_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' or ifnull(eh.to_date, curdate()) between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\')"
		query += " and ('{0}' >= ifnull(eh.from_date, curdate()) and '{1}' <= ifnull(eh.to_date, curdate()))".format(filters.to_date, filters.from_date)
		

	if not filters.include_disabled:
		query += " and e.is_disabled = 0"

	if filters.not_cdcl:
				query += " and e.not_cdcl = 0"

	'''if filters.category:
		query += " and e.equipment_category = \'" + str(filters.category) + "\'"'''	

	query += " GROUP BY e.name, eh.branch order by e.equipment_category, e.equipment_type ASC"
	return query

def get_columns():
	cols = [
		("Equipment") + ":Link/Equipment:120",
		("Equipment Category") + ":data:120",
		("Equipment Type.") + ":data:120",
		("Registration No") + ":data:120",
		("Initial KM/H")+":data:100",
		("Final KM/H")+":data:100",
		("KM")+":Data:100",
		("Hour")+":Data:100",
		("HSD Drawn(L)")+":data:100",
		("Prev Bal(L)")+":data:100",
		("Total HSD(L)")+":data:100",
		("Yardstick(Per KM)")+":data:110",
		("Yardstick(Per Hour)")+":data:110",
		("HSD Consumption(L)")+":data:110",
		("Closing Bal(L)")+":data:110",
		("Tank Capacity")+":data:110",
		("Rate(Nu.)")+":currency:100",
		("Amount(Nu.)")+":Currency:100",

	]
	return cols
