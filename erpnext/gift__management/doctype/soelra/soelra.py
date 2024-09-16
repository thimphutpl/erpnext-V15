# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Soelra(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.gift__management.doctype.soelra_details.soelra_details import SoelraDetails
		from frappe.types import DF

		amended_from: DF.Link | None
		branch: DF.Link | None
		company: DF.Link | None
		date: DF.Date | None
		items: DF.Table[SoelraDetails]
		remarks: DF.Data | None
		vip_name: DF.Data | None
	# end: auto-generated types
	def validate(self):
		self.calculateAmount()
		
	def on_submit(self):
		self.create_stock_entry()
	
	def calculateAmount(self):
		for i in self.items:
			if i.quantity and i.rate:
				i.estimated_fair_market_value = i.quantity * i.rate
			if i.exchange_rate and i.estimated_fair_market_value:
				i.estimated_fair_market_valuenu = i.exchange_rate * i.estimated_fair_market_value
   
	def create_stock_entry(self):
		stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "branch":self.branch,
        "stock_entry_type": "Material Issue",  # or "Material Receipt" / "Material Transfer" depending on the type
        "company": self.company,  # Assuming your document has a company field
        "purpose": "Material Issue",  # Set the purpose of the stock entry
        "reference_doctype": self.doctype,
        "reference_name": self.name,
        "items": []
    })
    
		# Add items to the Stock Entry
		
		for item in self.items:  # Assuming 'self.items' contains the items you want to transfer/issue/receive
			stock_entry.append("items", {
				"item_code": item.particulars,
				"transfer_qty": item.quantity,
				"s_warehouse": item.warehouse,  # or use t_warehouse for 'Material Receipt'
				"qty":item.quantity,
				"uom":item.uom,
				"stock_uom":item.uom
				# "uom": item.uom,
				# "conversion_factor": item.conversion_factor,  # if applicable
				# "basic_rate": item.rate  # Set rate if needed
			})
		
		# Insert and submit the Stock Entry
		stock_entry.insert(ignore_permissions=True)
		stock_entry.submit()

		frappe.msgprint(f"Stock Entry {stock_entry.name} has been created and submitted.")
		