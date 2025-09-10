# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.stock_ledger import make_sl_entries



class CSR(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounts.doctype.csr_detail_items.csr_detail_items import CSRDetailItems
		from frappe.types import DF

		address_display: DF.SmallText | None
		amended_from: DF.Link | None
		company: DF.Link
		company_address: DF.Link | None
		company_address_display: DF.SmallText | None
		company_contact_person: DF.Link | None
		contact_display: DF.SmallText | None
		contact_email: DF.Data | None
		contact_mobile: DF.SmallText | None
		contact_person: DF.Link | None
		cost_center: DF.Link | None
		customer: DF.Link | None
		customer_address: DF.Link | None
		customer_name: DF.SmallText | None
		dispatch_address: DF.SmallText | None
		dispatch_address_name: DF.Link | None
		items: DF.Table[CSRDetailItems]
		naming_series: DF.Literal["ACC-SINV-.YYYY.-", "ACC-SINV-RET-.YYYY.-"]
		posting_date: DF.Date
		posting_time: DF.Time | None
		project: DF.Link | None
		set_posting_time: DF.Check
		set_target_warehouse: DF.Link | None
		set_warehouse: DF.Link | None
		shipping_address: DF.SmallText | None
		shipping_address_name: DF.Link | None
		stock_entrys: DF.Data | None
		tc_name: DF.Link | None
		terms: DF.TextEditor | None
		territory: DF.Link | None
		title: DF.Data | None
		total: DF.Currency
		total_qty: DF.Float
	# end: auto-generated types
	def on_submit(self):
		self.make_stock_entry()
		# self.make_gl_entry()
	def on_cancel(self):
		# Check if there's an associated stock entry
		if self.stock_entrys:
			# Cancel the related Stock Entry document
			stock_entry = frappe.get_doc("Stock Entry", self.stock_entrys)
			if stock_entry.docstatus != 2:
				stock_entry.cancel()
				frappe.msgprint(f"Stock Entry {stock_entry.name} has been cancelled.")

			# Reset the stock_entrys field in CSR
			# frappe.db.set_value('CSR', self.name, 'stock_entrys', None)
			# frappe.db.commit()
		else:
			frappe.msgprint("No Stock Entry associated with this CSR.")
			
	def make_stock_entry(self):
		if not self.items:
			frappe.throw("No items found in CSR. Add items before submitting.")

		# Create a new Stock Entry document
		stock_entry = frappe.get_doc({
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Issue",  # Use "Material Issue" for releasing stock
			"posting_date": self.posting_date,
			"company": self.company,
			"csr":self.name,
			"items": []
		})

		# Add items to the Stock Entry
		for item in self.items:
			if not item.item_code or not item.source_warehouse or not item.qty:
				frappe.throw(f"Missing required fields in item {item.idx}: Ensure Item Code, Warehouse, and Qty are set.")

			stock_entry.append("items", {
				"item_code": item.item_code,
				"s_warehouse": item.source_warehouse,  # Source warehouse (stock will be reduced here)
				"qty": item.qty,  # Quantity to be deducted (no negative value)
				"basic_rate": item.rate,  # Optional: Include rate if needed
				"cost_center": self.cost_center  # Optional: Include cost center if needed
			})

		# Insert and submit the Stock Entry
		
		stock_entry.insert()
		stock_entry.submit()
		frappe.db.set_value('CSR', self.name, 'stock_entrys', stock_entry.name)
		frappe.db.commit()
		self.reload()
		
		
		

		  
		

	# You can also perform additional logic, like saving or updating the CSR document if needed
		
		frappe.msgprint(f"Stock Entry {stock_entry.name} created and submitted successfully.")
