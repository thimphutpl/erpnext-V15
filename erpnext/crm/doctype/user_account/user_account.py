# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.core.doctype.user.user import validate_mobile_no, update_mobile_no

class UserAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account_number: DF.Data | None
		alternate_mobile_no: DF.Data | None
		amended_from: DF.Link | None
		billing_address_line1: DF.Data | None
		billing_address_line2: DF.Data | None
		billing_dzongkhag: DF.Link | None
		billing_gewog: DF.Link | None
		billing_pincode: DF.Data | None
		blacklisted: DF.Check
		cid: DF.Data | None
		cid_file_back: DF.AttachImage | None
		cid_file_front: DF.AttachImage | None
		date_of_expiry: DF.Date | None
		date_of_issue: DF.Date | None
		email_id: DF.Data | None
		enabled: DF.Check
		financial_institution: DF.Link | None
		financial_institution_branch: DF.Link | None
		first_name: DF.Data | None
		full_name: DF.Data | None
		last_name: DF.Data | None
		mobile_no: DF.Data | None
		perm_address_line1: DF.Data | None
		perm_address_line2: DF.Data | None
		perm_dzongkhag: DF.Link | None
		perm_gewog: DF.Link | None
		perm_pincode: DF.Data | None
		user: DF.Link
	# end: auto-generated types
	def validate(self):
		self.default_validations()
		self.update_mobile_no()

	def on_update(self):
		#self.update_customer()
		pass
		
	def default_validations(self):
		if not self.mobile_no:
			frappe.throw(_("Mobile No. is mandatory"))

		self.mobile_no = validate_mobile_no(self.mobile_no)
		if self.alternate_mobile_no:		
			self.alternate_mobile_no = validate_mobile_no(self.alternate_mobile_no)

	def update_mobile_no(self):
		full_name = ""
		old_mobile_no = self.get_db_value("mobile_no")
		if old_mobile_no and self.mobile_no and old_mobile_no[-8:] != self.mobile_no[-8:]:
			update_mobile_no(self.full_name, self.name, self.mobile_no)
			frappe.msgprint(_("Mobile number updated successfully and PIN details are sent via SMS"))

	def update_customer(self):
		""" create/update Customer based on CID """
		if frappe.db.exists("Customer", {"customer_id": self.user}):
			doc = frappe.get_doc("Customer", {"customer_id": self.user})
		else:
			return

		customer_address = [self.full_name, self.billing_address_line1, self.billing_address_line2,
					self.billing_dzongkhag, self.billing_gewog, self.billing_pincode]
		customer_address = [i for i in customer_address if i]
		customer_address = "\n".join(customer_address) if customer_address else doc.customer_details
		doc.customer_name = self.full_name	
		doc.customer_group= "Domestic"
		doc.territory	  = "Bhutan"
		doc.customer_type = "Domestic Customer"
		doc.customer_id	  = self.user
		doc.dzongkhag	  = self.billing_dzongkhag if self.billing_dzongkhag else doc.dzongkhag
		doc.mobile_no	  = self.mobile_no if self.mobile_no else doc.mobile_no
		doc.customer_details = customer_address
		doc.save(ignore_permissions=True)

@frappe.whitelist()
def has_pending_transactions(user):
	return 0

@frappe.whitelist()
def change_mobile_no(login_id, mobile_no):
	doc = frappe.get_doc("User Account", login_id)
	doc.mobile_no = mobile_no
	doc.save(ignore_permissions=True)
		
