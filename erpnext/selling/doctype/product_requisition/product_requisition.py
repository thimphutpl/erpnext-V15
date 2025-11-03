# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

class ProductRequisition(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.selling.doctype.product_requisition_item.product_requisition_item import ProductRequisitionItem
		from frappe.types import DF

		allotment_date: DF.Date | None
		amended_from: DF.Link | None
		applicant_contact: DF.Data
		applicant_name: DF.Data
		branch: DF.Link
		company: DF.Link
		construction_type: DF.Link
		currency: DF.Link
		current_dzongkha: DF.Link
		current_resident: DF.Data
		customer: DF.Link
		customer_type: DF.Data | None
		delivered: DF.Check
		destination: DF.Data | None
		destination_dzongkha: DF.Link | None
		end_date: DF.Date | None
		is_allotment: DF.Check
		is_new_customer: DF.Check
		items: DF.Table[ProductRequisitionItem]
		location: DF.Data
		no_of_story: DF.Data | None
		others: DF.Text | None
		posting_date: DF.Date | None
		remarks: DF.Text | None
		so_reference: DF.Link | None
		start_date: DF.Date
		supply_rate: DF.Literal["", "NRPC Rate", "Concessional Royalty", "Negotiation Rate"]
		tharm: DF.Data | None
	# end: auto-generated types
	def validate(self):
		if self.end_date:
			if self.start_date > self.end_date:
				frappe.throw("To Date Cannot Be Greater Then From Date")

		for i in self.items:
			if not i.balance:
				i.balance = i.qty	
		
@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
    def update_so(source, target):
        target.price_list_currency = source.currency
        target.currency = source.currency
        target.plc_conversion_rate = 1
        target.ignore_pricing_rule = 1
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doclist = get_mapped_doc("Product Requisition", source_name, {
        "Product Requisition": {
            "doctype": "Sales Order",
            "field_map": {
                "branch": "branch",
                "customer": "customer",
                "name": "po_no",
                "posting_date": "po_date",
                "currency": "price_list_currency"
            },
            "validation": {
                "docstatus": ["=", 1]
            }
        },
        "Product Requisition Item": {
            "doctype": "Sales Order Item",
            "field_map": {
                "item_code": "item_code",
                "balance": "qty"
            }
        }
    }, target_doc, update_so)

    return doclist
