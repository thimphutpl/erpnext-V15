# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns =get_columns()
	data =get_data(filters)
	return columns, data

def get_columns():
	return [
		("Equipment") + ":Link/Equipment:120",
		("Equipment Type") + ":data:120",
		("Equipment No")+":data:100",
		("Hire Form Name")+":Link/Equipment Hiring Form:150",
		("Customer Name") + ":data:120",
		("Customer Type") + ":data:120",
		("Hour W Fuel (Internal)")+":data:80",
		("Rate W Fuel (Internal)")+":Currency:150",
		("Amount W Fuel (Internal)")+":Currency:150",
		("Hour W/O Fuel (Internal)")+":data:80",
		("Rate W/O Fuel (Internal)")+":Currency:150",
		("Amount W/O Fuel (Internal)")+":Currency:150",
		("Hour Cft-Broadleaf (Internal)")+":data:80",
		("Rate Cft-Broadleaf (Internal)")+":Currency:150",
		("Amount Cft-Broadleaf (Internal)")+":Currency:150",
		("Hour Cft-Conifer (Internal)")+":data:80",
		("Rate Cft-Conifer (Internal)")+":Currency:150",
		("Amount Cft-Conifer (Internal)")+":Currency:150",
		("Hour W Fuel (External)")+":data:80",
		("Rate W Fuel (External)")+":Currency:150",
		("Amount W Fuel (External)")+":Currency:150",
		("Hour W/O Fuel (External)")+":data:80",
		("Rate W/O Fuel (External)")+":Currency:150",
		("Amount W/O Fuel (External)")+":Currency:150",
		("Hour Cft-Broadleaf (External)")+":data:80",
		("Rate Cft-Broadleaf (External)")+":Currency:150",
		("Amount Cft-Broadleaf (External)")+":Currency:150",
		("Hour Cft-Conifer (External)")+":data:80",
		("Rate Cft-Conifer (External)")+":Currency:150",
		("Amount Cft-Conifer (External)")+":Currency:150",
		("Idle Hour")+ ":data:80",
       	("Idle Rate")+":Currency:150",
		("Idle Amount") + ":Currency:150",
		("Own Company")+":Currency:150",
		("Private")+":Currency:150",
		("Others")+":Currency:150",
		("Total Hire Charge")+":Currency:150",
	]

def get_data(filters):
	query ="""select hid.equipment, (select e.equipment_type FROM tabEquipment e WHERE e.name = hid.equipment), hid.equipment_name, hci.ehf_name, hci.customer, (select c.customer_group FROM tabCustomer AS c WHERE hci.customer = c.name),
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'With Fuel (Internal)' THEN vl.total_work_time END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'With Fuel (Internal)' THEN vl.work_rate END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'With Fuel (Internal)' THEN vl.hire_charge_amount END,

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Without Fuel (Internal)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Without Fuel (Internal)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Without Fuel (Internal)' THEN vl.hire_charge_amount END,

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Conifer - Cft (Internal)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Conifer - Cft (Internal)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Conifer - Cft (Internal)' THEN vl.hire_charge_amount END,

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Broadleaf - Cft (Internal)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Broadleaf - Cft (Internal)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Broadleaf - Cft (Internal)' THEN vl.hire_charge_amount END,\

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'With Fuel (External)' THEN vl.total_work_time END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'With Fuel (External)' THEN vl.work_rate END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'With Fuel (External)' THEN vl.hire_charge_amount END,

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Without Fuel (External)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Without Fuel (External)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Without Fuel (External)' THEN vl.hire_charge_amount END,

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Conifer - Cft (External)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Conifer - Cft (External)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Conifer - Cft (External)' THEN vl.hire_charge_amount END,

        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Broadleaf - Cft (External)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Broadleaf - Cft (External)' THEN vl.hire_charge_amount END,
        CASE WHEN had.rate_type = 'Hourly' AND had.hourly = 'Broadleaf - Cft (External)' THEN vl.hire_charge_amount END,

       
        vl.total_idle_time, hid.idle_rate, sum(hid.amount_idle),
        CASE hci.owned_by
        WHEN 'Own Company' THEN (select sum(hid.total_amount))
        END,
        CASE hci.owned_by
        WHEN 'Private' THEN (select sum(hid.total_amount))
        END,
        CASE hci.owned_by
        WHEN 'Others' THEN (select sum(hid.total_amount))
        END,sum(hid.total_amount) FROM `tabHire Invoice Details` AS hid, `tabHire Charge Invoice` AS hci, `tabEquipment` e,  
	`tabEquipment History` eh,`tabVehicle Logbook` vl, `tabEquipment Hiring Form` ehf, `tabHiring Approval Details` had
	WHERE hid.parent = hci.name AND hid.vehicle_logbook = vl.name and hid.equipment = e.name  and e.name = eh.parent and eh.branch = hci.branch
	and ehf.name = hci.ehf_name and had.parent = ehf.name
	and hci.docstatus = 1 and ((vl.from_date between '{0}' and '{1}') or (vl.to_date between '{0}' and '{1}'))""".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("branch"):
		query += " and hci.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += """ and (('{0}' between eh.from_date and ifnull(eh.to_date, now())) or
		('{1}' between eh.from_date and ifnull(eh.to_date, now())))""".format(filters.get("from_date"), filters.get("to_date"))
	if filters.get("not_cdcl"):
		query += " and e.not_cdcl = 0"

	if filters.get("include_disabled"):
		query += " "
	else:
		query += " and e.is_disabled = 0"

	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	query += " group by hid.equipment, hci.ehf_name"
	#frappe.msgprint(query)
	return frappe.db.sql(query)
