# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class GiftRegister(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.Data | None
		agency: DF.Data | None
		amended_from: DF.Link | None
		contact_number: DF.Phone | None
		currency: DF.Link | None
		current_deposition_of_location: DF.Data | None
		date: DF.Date | None
		date_of_deposit: DF.Date | None
		date_of_receipt: DF.Date | None
		description_of_gift: DF.Data | None
		designation: DF.Data | None
		designation_of_the_recipient: DF.Data | None
		divisiondepartment: DF.Data | None
		estimated_fair_market_value: DF.Currency
		estimated_fair_market_valuenu: DF.Currency
		exchange_rate: DF.Float
		gift_acceptance_circumstanes: DF.Text | None
		gift_image: DF.AttachImage | None
		gift_name: DF.Data | None
		gift_recipient_name: DF.Data | None
		gift_status: DF.Literal["", "Received", "Returned", "Disposed", "Sold"]
		mode_of_disposal: DF.Data | None
		name_of_organisation: DF.Data | None
		name_of_the_gift_giver: DF.Data | None
		organization: DF.Data | None
		phone_no: DF.Phone | None
		receiptacknowledgement: DF.Attach | None
		received_from: DF.Data | None
		relationship_to_the_public_servant: DF.Data | None
		relationship_with_the_giver: DF.Data | None
		remarks: DF.Data | None
		remarks_gift: DF.Data | None
		source_of_gift_name: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.calculateAmount()
    
	def calculateAmount(self):
		if self.exchange_rate and self.estimated_fair_market_value:
			self.estimated_fair_market_valuenu = self.exchange_rate * self.estimated_fair_market_value