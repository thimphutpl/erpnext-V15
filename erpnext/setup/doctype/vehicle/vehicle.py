# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
#rom __future__ import unicode_literals
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Vehicle(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		acquisition_date: DF.Date | None
		amended_from: DF.Link | None
		carbon_check_date: DF.Date | None
		chassis_no: DF.Data | None
		color: DF.Data | None
		doors: DF.Int
		employee: DF.Link | None
		end_date: DF.Date | None
		fuel_type: DF.Literal["Petrol", "Diesel", "Natural Gas", "Electric"]
		insurance_company: DF.Data | None
		last_odometer: DF.Int
		license_plate: DF.Data
		location: DF.Data | None
		make: DF.Data
		model: DF.Data
		policy_no: DF.Data | None
		start_date: DF.Date | None
		uom: DF.Link
		vehicle_value: DF.Currency
		wheels: DF.Int
	# end: auto-generated types

	# def autoname(self):
	# 	self.name = self.license_plate.replace(" ", "").upper()

	def validate(self):
		pass

	def on_update_after_submit(self):
		self.update_transport_request()
		if self.common_pool == 0 and frappe.db.exists("Load Request", {"load_status":"Queued", "vehicle":self.name}):
			frappe.throw("Not allow to uncheck Common Pool as the vehicle is already registered in Queue")

	def update_transport_request(self):
		self.vehicle_no = self.vehicle_no.upper()
		vehicle = self.vehicle_no
		cond = "upper(vehicle_no)"
		for x in [' ', '+', '-', '(', ')', '/', '#']:
			vehicle = vehicle.replace(x, '')
			cond = "replace({},'{}','')".format(cond, x)
		cond += " like '%{}%'".format(vehicle)

		for a in frappe.db.sql("""select name from `tabTransport Request` 
				       where {}
                                       and approval_status in ('Pending', 'Approved') 
                                       and docstatus != 2
                		      """.format(cond, self.name), as_dict = True):
			frappe.db.sql("Update `tabTransport Request` set common_pool = '{0}', self_arranged = '{1}', vehicle_capacity = '{2}' where name = '{3}'".format(self.common_pool, self.self_arranged, self.vehicle_capacity, a.name))