# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from frappe.utils import cstr, flt, getdate, today, nowdate, now_datetime


class BOQ(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.projects.doctype.boq_history_item.boq_history_item import BOQHistoryItem
		from erpnext.projects.doctype.boq_item.boq_item import BOQItem
		from frappe.types import DF

		amended_from: DF.Link | None
		balance_amount: DF.Currency
		boq_date: DF.Date
		boq_history_item: DF.Table[BOQHistoryItem]
		boq_item: DF.Table[BOQItem]
		boq_type: DF.Literal["Item Based", "Milestone Based", "Piece Rate Work Based(PRW)"]
		branch: DF.Link | None
		claimed_amount: DF.Currency
		company: DF.Link | None
		cost_center: DF.Link | None
		latest_amount: DF.Currency
		notes: DF.TextEditor | None
		paid_amount: DF.Currency
		party: DF.DynamicLink | None
		party_type: DF.Link | None
		price_adjustment: DF.Currency
		project: DF.Link
		received_amount: DF.Currency
		remarks: DF.Data | None
		total_amount: DF.Currency
	# end: auto-generated types
	
	def validate(self):
		self.update_defaults()
		self.validate_defaults()
		self.update_boq_history()
		self.update_project_value()

	def on_submit(self):
		self.project_boq_item_entry()

	def on_cancel(self):
		self.update_project_value()
		self.project_boq_item_entry()

	def on_update_after_submit(self):
		self.project_boq_item_entry()

	def project_boq_item_entry(self):
		if self.docstatus == 2:
			frappe.db.sql("delete from `tabProject BOQ Item` where parent='{project}' and boq_name = '{boq_name}'".format(project=self.project, boq_name=self.name))
		else:
			if not frappe.db.exists("Project BOQ Item", {"parent": self.project, "boq_name": self.name}):
				doc = frappe.get_doc("Project", self.project)
				row = doc.append("project_boq_item", {})
				row.boq_name            = self.name
				row.boq_date            = self.boq_date
				row.amount              = flt(self.total_amount)
				row.price_adjustment    = flt(self.price_adjustment)
				row.total_amount        = flt(self.total_amount)+flt(self.price_adjustment)
				row.received_amount     = flt(self.received_amount)
				row.paid_amount         = flt(self.paid_amount)
				row.balance_amount      = flt(self.balance_amount)
				row.save(ignore_permissions=True)
			else:
				row = frappe.get_doc("Project BOQ Item", {"parent": self.project, "boq_name": self.name})
				row.boq_date            = self.boq_date
				row.amount              = flt(self.total_amount)
				row.price_adjustment    = flt(self.price_adjustment)
				row.total_amount        = flt(self.total_amount)+flt(self.price_adjustment)
				row.received_amount     = flt(self.received_amount)
				row.paid_amount         = flt(self.paid_amount)
				row.balance_amount      = flt(self.balance_amount)
				row.save(ignore_permissions=True)

	def update_boq_history(self):
		# removing entries which are copied via "Duplicate" option
		for i in self.boq_history_item:
			if i.transaction_type != self.doctype or (i.transaction_name and i.transaction_name != self.name):
				self.remove(i)

		# make entry in history for the current BOQ if it doesn't already exist, else update the details
		if not self.boq_history_item:
			self.append("boq_history_item",{
				"transaction_type": self.doctype,
				"transaction_date": self.boq_date,
				"initial_amount": flt(self.total_amount),
				"adjustment_amount": 0,
				"final_amount": flt(self.total_amount),
				"owner": frappe.session.user,
				"creation": now_datetime(),
				"modified_by": frappe.session.user,
				"modified": now_datetime()
			})
		else:
			for i in self.boq_history_item:
				if i.transaction_type == self.doctype:
					i.transaction_name  = self.name
					i.transaction_date  = self.boq_date
					i.initial_amount    = flt(self.total_amount)
					i.adjustment_amount = 0
					i.final_amount      = flt(self.total_amount)

	def validate_defaults(self):
		if not self.project:
			frappe.throw("`Project` cannot be null.")
				
		if not self.branch:
			frappe.throw("`Branch` cannot be null.")

		if not self.cost_center:
			frappe.throw("`Cost Center` cannot be null.")

		if flt(self.total_amount,0) <= 0:
			frappe.throw(_("Invalid total amount."), title="Invalid Data")

	def update_defaults(self):
		item_group = ""
		self.total_amount     = 0.0
		self.price_adjustment = 0.0
		self.claimed_amount   = 0.0
		self.received_amount  = 0.0
		self.balance_amount   = 0.0
		

		for item in self.boq_item:
			if item.is_group:
				item_group              = item.item
				item.quantity           = 0.0
				item.rate               = 0.0
				item.amount             = 0.0
				item.claimed_quantity   = 0.0
				item.claimed_amount     = 0.0
				item.booked_quantity    = 0.0
				item.booked_amount      = 0.0
				item.balance_quantity   = 0.0
				item.balance_amount     = 0.0
			else:
				item.amount           = flt(flt(item.quantity) * flt(item.rate), 2)
				item.claimed_quantity = 0.0
				item.claimed_amount   = 0.0
				item.booked_quantity  = 0.0
				item.booked_amount    = 0.0
				item.balance_quantity = flt(item.quantity)
				item.balance_rate     = flt(item.rate)
				item.balance_amount   = flt(item.amount,2)

				'''
				self.total_amount    += flt(item.amount)
				self.claimed_amount  += flt(item.claimed_amount)
				self.received_amount += flt(item.received_amount)
				self.balance_amount  += (flt(item.amount)-flt(item.received_amount))
				'''
		
				self.total_amount    += flt(item.amount)
				self.balance_amount  += flt(item.amount)

			item.parent_item = item_group
			if flt(item.amount) < 0:
				frappe.throw(_("Row#{0} : Invalid amount."),title="Invalid Data")
						
		# Defaults
		base_project = frappe.get_doc("Project", self.project)
		self.party_type = base_project.party_type
		self.party      = base_project.party
		
		if base_project.status in ('Completed','Cancelled'):
			frappe.throw(_("Operation not permitted on already {0} Project.").format(base_project.status),title="BOQ: Invalid Operation")
						
		if not self.branch:
			self.branch = base_project.branch

		if not self.cost_center:
			self.cost_center = base_project.cost_center

		if not self.boq_date:
			self.boq_date = today()
		
	def update_project_value(self):
		if self.total_amount:
			pro_doc = frappe.get_doc("Project", self.project)
			pro_doc.flags.dont_sync_tasks = True
			if not self.latest_amount or self.docstatus == 2 :
				self.latest_amount = self.total_amount
				pro_doc.project_value = flt(pro_doc.project_value)+(-1*(self.latest_amount) if self.docstatus==2 else flt(self.latest_amount))
			if self.docstatus == 2:
				self.latest_amount = 0
			elif flt(self.latest_amount) < flt(self.total_amount):
				pro_doc.project_value = flt(pro_doc.project_value) - flt(self.latest_amount)
				pro_doc.project_value = flt(pro_doc.project_value) + flt(self.total_amount)
				self.latest_amount = self.total_amount
			elif flt(self.latest_amount) > flt(self.total_amount):
				pro_doc.project_value = flt(pro_doc.project_value) - flt(self.latest_amount)
				pro_doc.project_value = flt(pro_doc.project_value) + flt(self.total_amount)
				self.latest_amount = self.total_amount
			pro_doc.save(ignore_permissions = True)

@frappe.whitelist()
def make_boq_adjustment(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.total_amount = 0.0
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.balance_rate         = flt(source_doc.balance_rate) if flt(source_doc.balance_rate) else flt(source_doc.rate)
		target_doc.balance_quantity_adj = flt(target_doc.balance_quantity)
		target_doc.balance_rate_adj     = flt(target_doc.balance_rate)
		target_doc.balance_amount_adj   = flt(target_doc.balance_amount)
		target_doc.adjustment_quantity  = 0
		target_doc.adjustment_rate      = 0
		target_doc.adjustment_amount    = 0
			
	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "BOQ Adjustment",
			"field_map": {
					"name": "boq"
			},
			"postprocess": update_master
		},

		"BOQ Item": {
			"doctype": "BOQ Adjustment Item",
			"field_map": {
					"name": "boq_item_name",
					"balance_rate": "balance_rate",
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def get_boq_items(boq, company, qty=1, fetch_exploded=1):
	items = get_boq_items_as_dict(boq, company, qty, fetch_exploded, include_non_stock_items=True).values()
	items = list(items)
	items.sort(key=functools.cmp_to_key(lambda a, b: a.item_code > b.item_code and 1 or -1))
	return items

def get_boq_items_as_dict(
	boq,
	company,
	qty=1,
	fetch_exploded=1,
	fetch_scrap_items=0,
	include_non_stock_items=False,
	fetch_qty_in_stock_uom=True,
):
	item_dict = {}

	# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
	query = """select
				bom_item.item_code,
				bom_item.idx,
				item.item_name,
				sum(bom_item.{qty_field}/ifnull(bom.quantity, 1)) * %(qty)s as qty,
				item.image,
				bom.project,
				bom_item.rate,
				sum(bom_item.{qty_field}/ifnull(bom.quantity, 1)) * bom_item.rate * %(qty)s as amount,
				item.stock_uom,
				item.item_group,
				item.allow_alternative_item,
				item_default.default_warehouse,
				item_default.expense_account as expense_account,
				item_default.buying_cost_center as cost_center
				{select_columns}
			from
				`tab{table}` bom_item
				JOIN `tabBOM` bom ON bom_item.parent = bom.name
				JOIN `tabItem` item ON item.name = bom_item.item_code
				LEFT JOIN `tabItem Default` item_default
					ON item_default.parent = item.name and item_default.company = %(company)s
			where
				bom_item.docstatus < 2
				and bom.name = %(bom)s
				and item.is_stock_item in (1, {is_stock_item})
				{where_conditions}
				group by item_code, stock_uom
				order by idx"""

	is_stock_item = 0 if include_non_stock_items else 1
	if cint(fetch_exploded):
		query = query.format(
			table="BOM Explosion Item",
			where_conditions="",
			is_stock_item=is_stock_item,
			qty_field="stock_qty",
			select_columns=""", bom_item.source_warehouse, bom_item.operation,
				bom_item.include_item_in_manufacturing, bom_item.description, bom_item.rate, bom_item.sourced_by_supplier,
				(Select idx from `tabBOM Item` where item_code = bom_item.item_code and parent = %(parent)s limit 1) as idx""",
		)

		items = frappe.db.sql(
			query, {"parent": bom, "qty": qty, "bom": bom, "company": company}, as_dict=True
		)
	elif fetch_scrap_items:
		query = query.format(
			table="BOM Scrap Item",
			where_conditions="",
			select_columns=", item.description",
			is_stock_item=is_stock_item,
			qty_field="stock_qty",
		)

		items = frappe.db.sql(query, {"qty": qty, "bom": bom, "company": company}, as_dict=True)
	else:
		query = query.format(
			table="BOM Item",
			where_conditions="",
			is_stock_item=is_stock_item,
			qty_field="stock_qty" if fetch_qty_in_stock_uom else "qty",
			select_columns=""", bom_item.uom, bom_item.conversion_factor, bom_item.source_warehouse,
				bom_item.operation, bom_item.include_item_in_manufacturing, bom_item.sourced_by_supplier,
				bom_item.description, bom_item.base_rate as rate """,
		)
		items = frappe.db.sql(query, {"qty": qty, "bom": bom, "company": company}, as_dict=True)

	for item in items:
		if item.item_code in item_dict:
			item_dict[item.item_code]["qty"] += flt(item.qty)
		else:
			item_dict[item.item_code] = item

	for item, item_details in item_dict.items():
		for d in [
			["Account", "expense_account", "stock_adjustment_account"],
			["Cost Center", "cost_center", "cost_center"],
			["Warehouse", "default_warehouse", ""],
		]:
			company_in_record = frappe.db.get_value(d[0], item_details.get(d[1]), "company")
			if not item_details.get(d[1]) or (company_in_record and company != company_in_record):
				item_dict[item][d[1]] = frappe.get_cached_value("Company", company, d[2]) if d[2] else None

	return item_dict

@frappe.whitelist()
def make_direct_invoice(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.invoice_title = str(target_doc.project) + "(Project Invoice)"
		target_doc.invoice_type = "Direct Invoice"
		target_doc.check_all = 1
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.invoice_rate = flt(source_doc.balance_rate) if flt(source_doc.balance_rate) else flt(source_doc.rate)
		target_doc.act_quantity = flt(target_doc.invoice_quantity)
		target_doc.act_rate     = flt(target_doc.invoice_rate)
		target_doc.act_amount   = flt(target_doc.invoice_amount)
		target_doc.original_rate= flt(target_doc.invoice_rate)
			
	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "Project Invoice",
			"field_map": {
				"project": "project"
			},
			"postprocess": update_master
		},

		"BOQ Item": {
			"doctype": "Project Invoice BOQ",
			"field_map": {
				"name": "boq_item_name",
				"balance_quantity": "invoice_quantity",
				"balance_rate": "invoice_rate",
				"balance_amount": "invoice_amount",
				"quantity": "original_quantity",
				"amount": "original_amount"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_boq_subcontract(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.boq          = source_doc.name
		target_doc.party_type   = "Supplier" if source_doc.party_type == "Customer" else None
		target_doc.party        = None
		target_doc.total_amount = 0
		target_doc.price_adjustment = 0
		target_doc.paid_amount = 0
		target_doc.received_amount = 0
		target_doc.claimed_amount = 0
		target_doc.balance_amount = 0
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.boq_quantity = target_doc.quantity = source_doc.balance_quantity
		target_doc.boq_rate     = target_doc.rate     = source_doc.balance_rate
		target_doc.boq_amount   = target_doc.amount   = source_doc.balance_amount
		
		target_doc.claimed_quantity    = target_doc.claimed_amount    = 0
		target_doc.booked_quantity     = target_doc.booked_amount     = 0
		target_doc.adjustment_quantity = target_doc.adjustment_amount = 0
			
	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "Subcontract",
			"field_map": {
				"project": "project"
			},
			"postprocess": update_master
		},
		"BOQ Item": {
			"doctype": "Subcontract Item",
			"field_map": {
				"name": "boq_item_name",
			},
			"postprocess": update_item
		},
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_mb_invoice(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.invoice_title = str(target_doc.project) + "(Project Invoice)"
		target_doc.invoice_type = "MB Based Invoice"
		target_doc.check_all_mb = 1
			
	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "Project Invoice",
			"field_map": {
				"project": "project"
			},
			"postprocess": update_master
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_book_entry(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_parent):
		target_doc.check_all = 1
			
	def update_item(source_doc, target_doc, source_parent):
		target_doc.entry_rate   = flt(source_doc.balance_rate) if flt(source_doc.balance_rate) else flt(source_doc.rate)
		target_doc.act_quantity = flt(target_doc.entry_quantity)
		target_doc.act_rate     = flt(target_doc.entry_rate)
		target_doc.act_amount   = flt(target_doc.entry_amount)
		target_doc.original_rate= flt(target_doc.entry_rate)
			
	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "MB Entry",
			"field_map": {
				"project": "project"
			},
			"postprocess": update_master
		},

		"BOQ Item": {
			"doctype": "MB Entry BOQ",
			"field_map": {
				"name": "boq_item_name",
				"balance_quantity": "entry_quantity",
				"balance_rate": "entry_rate",
				"balance_amount": "entry_amount",
				"quantity": "original_quantity",
				"amount": "original_amount"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_boq_advance(source_name, target_doc=None):
	def update_master(source_doc, target_doc, source_partent):
		#target_doc.customer = source_doc.customer
		pass
	
	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "Project Advance",
			"field_map":{
				"project": "project",
				"party_type": "party_type",
				"party": "party",
				"party_address": "party_address"
			},
			"postprocess": update_master
		}
	}, target_doc)
	
	return doclist