# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils.nestedset import NestedSet
class CustomerGroup(NestedSet):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
		from erpnext.selling.doctype.customer_credit_limit.customer_credit_limit import CustomerCreditLimit
		from frappe.types import DF

		accounts: DF.Table[PartyAccount]
		credit_limits: DF.Table[CustomerCreditLimit]
		customer_group_name: DF.Data
		default_price_list: DF.Link | None
		document_type: DF.Literal["", "Citizenship ID", "License Number", "Reference Number", "License/Reference Number"]
		is_group: DF.Check
		lft: DF.Int
		old_parent: DF.Link | None
		parent_customer_group: DF.Link | None
		payment_terms: DF.Link | None
		rgt: DF.Int
	# end: auto-generated types
	nsm_parent_field = 'parent_customer_group'

	def on_update(self):
		self.validate_name_with_customer()
		super(CustomerGroup, self).on_update()
		self.validate_one_root()

	def validate_name_with_customer(self):
		if frappe.db.exists("Customer", self.name):
			frappe.msgprint(_("An Customer exists with same name"), raise_exception=1)
