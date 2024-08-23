# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HallMaster(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.resource_sharing.doctype.notification_resource.notification_resource import NotificationResource
		from frappe.types import DF

		branch: DF.Link | None
		hall_name: DF.Data | None
		location: DF.Data | None
		table_cvno: DF.Table[NotificationResource]
	# end: auto-generated types
	pass
