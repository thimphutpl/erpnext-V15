# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff, get_datetime
from frappe.utils import get_datetime, nowdate
from datetime import datetime

# #
# Both recieved and issued pols can be queried with this
# #
def get_pol_till(purpose, equipment,branch, date, pol_type=None, additional_type=None):
	if not equipment or not date:
		frappe.throw(_("Equipment and Till Date are Mandatory"))

	total = 0
	query = """
		SELECT SUM(qty) AS total 
		FROM `tabPOL Entry` 
		WHERE docstatus = 1 
			AND type = %s 
			AND equipment = %s 
			AND branch = %s
			AND posting_date <= %s
	"""
	args = [purpose, equipment,branch, date]
	if pol_type:
		query += " AND pol_type = %s"
		args.append(pol_type)

	if additional_type:
		query += " AND type = %s"
		args.append(additional_type)

	quantity = frappe.db.sql(query, args, as_dict=True)
	if quantity and quantity[0].total:
		total = quantity[0].total

	return total


#added by kinzang from here
# def get_pol_till(purpose, equipment, branch, date,
#                  pol_type=None, additional_type=None):

#     if not equipment or not date:
#         frappe.throw(_("Equipment and Till Date are Mandatory"))

#     # Find the latest submitted opening entry
#     opening_query = """
#         SELECT name, posting_date, qty
#         FROM `tabPOL Entry`
#         WHERE docstatus = 1
#           AND is_opening = 1
#           AND equipment = %s
#           AND branch = %s
#           AND posting_date <= %s
#     """
#     opening_args = [equipment, branch, date]

#     if pol_type:
#         opening_query += " AND pol_type = %s"
#         opening_args.append(pol_type)

#     opening_query += """
#         ORDER BY posting_date DESC, creation DESC
#         LIMIT 1
#     """

#     opening = frappe.db.sql(
#         opening_query, opening_args, as_dict=True
#     )

#     if opening:
#         opening_entry = opening[0]
#         opening_date = opening_entry.posting_date
#         opening_name = opening_entry.name

#         # Sum the requested transaction type from opening date onward.
#         # Exclude the opening entry itself to avoid double-counting it.
#         query = """
#             SELECT COALESCE(SUM(qty), 0) AS total
#             FROM `tabPOL Entry`
#             WHERE docstatus = 1
#               AND type = %s
#               AND equipment = %s
#               AND branch = %s
#               AND posting_date >= %s
#               AND posting_date <= %s
#               AND name != %s
#         """

#         args = [
#             purpose, equipment, branch,
#             opening_date, date, opening_name
#         ]

#         if pol_type:
#             query += " AND pol_type = %s"
#             args.append(pol_type)

#         if additional_type:
#             query += " AND type = %s"
#             args.append(additional_type)

#         result = frappe.db.sql(query, args, as_dict=True)
#         movement_total = flt(result[0].total) if result else 0

#         # Include the opening quantity only when calculating
#         # the starting balance. The caller must not add it again.
#         return flt(opening_entry.qty) + movement_total

#     # No opening entry: retain the original calculation
#     query = """
#         SELECT COALESCE(SUM(qty), 0) AS total
#         FROM `tabPOL Entry`
#         WHERE docstatus = 1
#           AND type = %s
#           AND equipment = %s
#           AND branch = %s
#           AND posting_date <= %s
#     """

#     args = [purpose, equipment, branch, date]

#     if pol_type:
#         query += " AND pol_type = %s"
#         args.append(pol_type)

#     if additional_type:
#         query += " AND type = %s"
#         args.append(additional_type)

#     result = frappe.db.sql(query, args, as_dict=True)
#     return flt(result[0].total) if result else 0


#till here







def get_pol_tills(purpose, equipment, pol_type=None, posting_date=None, branch=None):
    if not equipment or not posting_date:
        frappe.throw(_("Equipment and Till Date are Mandatory"))

    # Check whether this equipment and POL type has an opening entry
    opening_query = """
        SELECT posting_date
        FROM `tabPOL Entry`
        WHERE docstatus = 1
          AND is_opening = 1
          AND equipment = %s
          AND pol_type = %s
          AND posting_date <= %s
    """
    opening_args = [equipment, pol_type, posting_date]

    if branch:
        opening_query += " AND branch = %s"
        opening_args.append(branch)

    opening_query += """
        ORDER BY posting_date DESC, creation DESC
        LIMIT 1
    """

    opening = frappe.db.sql(
        opening_query, opening_args, as_dict=True
    )

    # If an opening entry exists, count only movements after its date.
    if opening:
        opening_date = getdate(opening[0].posting_date)

        query = """
            SELECT COALESCE(SUM(qty), 0) AS total
            FROM `tabPOL Entry`
            WHERE docstatus = 1
              AND type = %s
              AND equipment = %s
              AND pol_type = %s
              AND posting_date > %s
              AND posting_date <= %s
              AND IFNULL(is_opening, 0) = 0
        """
        args = [
            purpose, equipment, pol_type,
            opening_date, posting_date
        ]

        if branch:
            query += " AND branch = %s"
            args.append(branch)

        result = frappe.db.sql(query, args, as_dict=True)
        return flt(result[0].total) if result else 0

    # No opening entry: use the normal calculation
    query = """
        SELECT COALESCE(SUM(qty), 0) AS total
        FROM `tabPOL Entry`
        WHERE docstatus = 1
          AND type = %s
          AND equipment = %s
          AND posting_date <= %s
    """
    args = [purpose, equipment, posting_date]

    if pol_type:
        query += " AND pol_type = %s"
        args.append(pol_type)

    if branch:
        query += " AND branch = %s"
        args.append(branch)

    result = frappe.db.sql(query, args, as_dict=True)
    return flt(result[0].total) if result else 0




# def get_pol_tills(purpose, equipment,pol_type=None,posting_date=None,):
# 	if not equipment:
# 		frappe.throw("Equipment and Till Date are Mandatory")
# 	total = 0
# 	# query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\' and posting_date<=\'"+str(posting_date)
# 	query = """
# 		SELECT SUM(qty) AS total,posting_date
# 		FROM `tabPOL Entry`
# 		WHERE docstatus = 1
# 		AND type = %s
# 		AND equipment = %s

# 	"""
	
# 	args= [purpose, equipment]

# 	if pol_type:
# 		query += " AND pol_type =%s"
# 		args.append(pol_type)
# 	if posting_date:
# 		query+="AND posting_date<=%s"
# 		args.append(posting_date)
# 	# frappe.throw(str(args))
		
# 	# frappe.throw(str(query))
# 	quantity = frappe.db.sql(query,args, as_dict=True)
# 	if quantity:
# 		total = quantity[0].total
# 	return total





def get_pol_transfer(purpose, equipment, date, pol_type=None):
	if not equipment:
		frappe.throw("Equipment and Till Date are Mandatory")
	total = 0
	query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\'"
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
	

	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

##
# Both recieved and issued pols can be queried with this
##
def get_pol_between(purpose, equipment, from_date, to_date, pol_type=None,own_cc=None):
	if not equipment or not from_date or not to_date:
		frappe.throw("Equipment and From/To Date are Mandatory")
	total = 0
	query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\' and posting_date between \'" + str(from_date) + "\' and \'" + str(to_date) + "\'"
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
		
	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

##
# Get consumed POl as per yardstick
##
def get_pol_consumed_till(equipment, date,filter_dry=None):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	pol = frappe.db.sql("select sum(consumption) as total from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s", (equipment, date), as_dict=True)
	if pol:
		return pol[0].total
	else:
		return 0	

def get_pol_consumed_tills(equipment):
	if not equipment:
		frappe.throw("Equipment are Mandatory")	
	pol = frappe.db.sql("select sum(consumption) as total from `tabVehicle Logbook` where docstatus = 1 and equipment = %s", (equipment, ), as_dict=True)
	if pol:
		return pol[0].total
	else:
		return 0


def get_pol_consumed_tills_op(
    equipment,
    opening_date,
    posting_date=None,
):
    if not equipment:
        frappe.throw("Equipment are Mandatory")

    if not opening_date:
        frappe.throw("Opening Date is Mandatory")

    query = """
        SELECT COALESCE(SUM(consumption), 0) AS total
        FROM `tabVehicle Logbook`
        WHERE docstatus = 1
          AND equipment = %s
          AND to_date >= %s
    """

    args = [equipment, opening_date]

    if posting_date:
        query += " AND to_date <= %s"
        args.append(posting_date)

    result = frappe.db.sql(query, args, as_dict=True)

    return flt(result[0].total) if result else 0
	
			

def get_km_till(equipment, date):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	km = frappe.db.sql("select final_km from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by final_km desc limit 1", (equipment, date), as_dict=True)
	if km:
		return km[0].final_km
	else:
		return 0	

def get_hour_till(equipment, date):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	hr = frappe.db.sql("select final_hour from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by final_hour desc limit 1", (equipment, date), as_dict=True)
	if hr:
		return hr[0].final_hour
	else:
		return 0	



#added by kinzang from here. To get creating with opening function

def get_km_after_opening(equipment, opening_date, opening_time, end_date):
    result = frappe.db.sql(
        """
        SELECT final_km
        FROM `tabVehicle Logbook`
        WHERE docstatus = 1
          AND equipment = %s
          AND (
                to_date > %s
                OR (
                    to_date = %s
                    AND IFNULL(to_time, '00:00:00') > %s
                )
          )
          AND to_date <= %s
        ORDER BY to_date DESC,
                 IFNULL(to_time, '00:00:00') DESC,
                 creation DESC
        LIMIT 1
        """,
        (
            equipment,
            opening_date,
            opening_date,
            opening_time or "00:00:00",
            end_date,
        ),
        as_dict=True,
    )
    return flt(result[0].final_km) if result else 0


def get_hour_after_opening(equipment, opening_date, opening_time, end_date):
    result = frappe.db.sql(
        """
        SELECT final_hour
        FROM `tabVehicle Logbook`
        WHERE docstatus = 1
          AND equipment = %s
          AND (
                to_date > %s
                OR (
                    to_date = %s
                    AND IFNULL(to_time, '00:00:00') > %s
                )
          )
          AND to_date <= %s
        ORDER BY to_date DESC,
                 IFNULL(to_time, '00:00:00') DESC,
                 creation DESC
        LIMIT 1
        """,
        (
            equipment,
            opening_date,
            opening_date,
            opening_time or "00:00:00",
            end_date,
        ),
        as_dict=True,
    )
    return flt(result[0].final_hour) if result else 0


def get_pol_between_opening(
    purpose,
    equipment,
    pol_type,
    opening_date,
    opening_time,
    from_date,
    to_date,
):
    result = frappe.db.sql(
        """
        SELECT COALESCE(SUM(qty), 0) AS total
        FROM `tabPOL Entry`
        WHERE docstatus = 1
          AND type = %s
          AND equipment = %s
          AND pol_type = %s
          AND IFNULL(is_opening, 0) = 0
          AND posting_date >= %s
          AND posting_date <= %s
          AND (
                posting_date > %s
                OR (
                    posting_date = %s
                    AND IFNULL(posting_time, '00:00:00') > %s
                )
          )
        """,
        (
            purpose,
            equipment,
            pol_type,
            from_date,
            to_date,
            opening_date,
            opening_date,
            opening_time or "00:00:00",
        ),
        as_dict=True,
    )
    return flt(result[0].total) if result else 0


def get_initial_km_hr(equipment, from_date, to_date):
    records = frappe.db.sql(
        """
        SELECT final_km, final_hour
        FROM `tabVehicle Logbook`
        WHERE equipment = %s
          AND docstatus = 1
          AND to_date >= %s
          AND to_date <= %s
        ORDER BY to_date ASC, to_time ASC, creation ASC
        LIMIT 1
        """,
        (equipment, getdate(from_date), getdate(to_date)),
        as_dict=True,
    )

    return records[0] if records else None


# def get_initial_km_hr(equipment, from_date, to_date, opening_date=None, opening_time=None):
#     conditions = [
#         "equipment = %s",
#         "docstatus = 1",
#         "to_date >= %s",
#         "to_date <= %s",
#     ]
#     values = [equipment, getdate(from_date), getdate(to_date)]

#     if opening_date:
#         conditions.append("""
#             (
#                 to_date > %s
#                 OR (
#                     to_date = %s
#                     AND IFNULL(to_time, '00:00:00') > %s
#                 )
#             )
#         """)
#         values.extend([
#             getdate(opening_date),
#             getdate(opening_date),
#             opening_time or "00:00:00",
#         ])

#     records = frappe.db.sql(
#         """
#         SELECT final_km, final_hour
#         FROM `tabVehicle Logbook`
#         WHERE {conditions}
#         ORDER BY to_date ASC, to_time ASC, creation ASC
#         LIMIT 1
#         """.format(conditions=" AND ".join(conditions)),
#         tuple(values),
#         as_dict=True,
#     )

#     return records[0] if records else None
#till here.



def get_employee_expense(equipment, f_date, t_date):
	if not equipment or not f_date or not t_date:
		frappe.throw("Equipment and From/Till Date are Mandatory")

	operators = frappe.db.sql("""
			select operator, employee_type, start_date, end_date
			from `tabEquipment Operator`
			where parent = '{0}' 
			and   docstatus < 2
			and   (start_date between {1} and {2} OR end_date between {3} and {4})
		""".format(equipment, f_date, t_date, f_date, t_date), as_dict=1)

	for a in operators:
		prorate_fraction = 1
		if getdate(f_date) < getdate(a.start_date) and getdate(t_date) > getdate(a.end_date):
		# Pay

		# Bonus

		# PBVA

		# Travel

		#Leave Encashment
			pass