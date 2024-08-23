# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class ResourceBooking(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        approver_email: DF.Data | None
        approver_name: DF.Data | None
        contact_number: DF.Data | None
        cost_center: DF.Link | None
        from_date_time: DF.Datetime | None
        reason: DF.Data | None
        requesting_by: DF.Data | None
        resource: DF.Link | None
        resource_name: DF.Data | None
        resource_type: DF.Link | None
        to_date_time: DF.Datetime | None
    # end: auto-generated types
    def validate(self):
        self.date_check()
        self.resource_booking()
        self.check_approver()
        
    
    def check_approver(self):
        action = frappe.request.form.get('action')
        if action == 'Apply':
            approve = frappe.db.get_value("Employee", frappe.db.get_value("Resource Directory", self.resource, "custodian"), ["employee_name","personal_email","cell_number"])
            # frappe.throw(str(approve[0]))
            self.approver_name = approve[0]
            self.approver_email = approve[1]
            self.contact_number = approve[2]
        
        
    def resource_booking(self):
        from_date_time = frappe.db.escape(self.from_date_time)
        to_date_time = frappe.db.escape(self.to_date_time)
        
        query = f"""
        SELECT name 
        FROM `tabResource Booking` 
        WHERE resource = %s AND
        (%s between from_date_time and to_date_time
        OR %s between from_date_time and to_date_time)
        AND name != %s
        """

    
        result = frappe.db.sql(query, (self.resource,self.from_date_time, self.to_date_time, self.name), as_dict=True)
        if len(result)>0:
            frappe.throw("A resource booking already exists during this time period.")
            
    def date_check(self):
        if self.from_date_time > self.to_date_time:
            frappe.throw("To Date Time should be greater then from date")
		

		
	