# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from frappe.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact,
)
from frappe.model.document import Document


class Bank(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.bank_transaction_mapping.bank_transaction_mapping import BankTransactionMapping
		from frappe.types import DF

		abbr: DF.Data
		bank_name: DF.Data
		bank_transaction_mapping: DF.Table[BankTransactionMapping]
		disabled: DF.Check
		plaid_access_token: DF.Data | None
		swift_number: DF.Data | None
	# end: auto-generated types

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def validate_abbr(self):
		if not self.abbr:
			self.abbr = "".join(c[0] for c in self.bank_name.split()).upper()

		self.abbr = self.abbr.strip()

		if not self.abbr.strip():
			frappe.throw(_("Abbreviation is mandatory"))

		if frappe.db.sql("select abbr from tabBank where name!=%s and abbr=%s", (self.name, self.abbr)):
			frappe.throw(_("Abbreviation already used for another bank"))

	def on_trash(self):
		delete_contact_and_address("Bank", self.name)
