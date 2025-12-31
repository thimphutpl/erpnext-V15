# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from erpnext.custom_autoname import get_auto_name
from frappe.utils import flt, cint
from frappe.utils import nowdate

class SellingPrice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.production.doctype.selling_price_branch.selling_price_branch import SellingPriceBranch
		from erpnext.production.doctype.selling_price_rate.selling_price_rate import SellingPriceRate
		from frappe.types import DF

		company: DF.Link
		from_date: DF.Date
		item_branch: DF.Table[SellingPriceBranch]
		item_rates: DF.Table[SellingPriceRate]
		naming_series: DF.Literal["", "Selling Price", "Selling Price Rate"]
		to_date: DF.Date
	# end: auto-generated types
	def validate(self):
		self.check_sp_rate()
		# self.make_null_value_empty()


	def check_sp_rate(self):
		for a in self.item_rates:
			if not flt(a.selling_price) > 0:
				frappe.throw("Selling Rate should be greater than 0 for <b>" + str(a.particular) + "</b>")

			if a.price_based_on == "Item":
				a.item_name = frappe.db.get_value("Item", a.particular, "item_name")
				a.timber_type = None
				a.item_sub_group = None
			else:
				a.item_name = None
	
	def check_duplicate_entries(self):
		branches = frappe.db.sql("select branch, count(branch) as num from `tabSelling Price Branch` where parent = %s group by branch having num > 1", self.name, as_dict=1)
		for a in branches:
			frappe.throw("Branch <b>" + str(a.branch) + "</b> has been defined more than once")

		sps = frappe.db.sql("""	select particular, timber_type, item_sub_group, selling_uom, count(particular) as num 
				from `tabSelling Price Rate` where parent = '{0}' 
				group by particular, timber_type, item_sub_group, selling_uom having num > 1
			""".format(self.name), as_dict=1)

		for a in sps:
			if a.timber_type and a.item_sub_group:
				frappe.throw("<b>" + str(a.particular) + "/" + str(a.timber_type) +  "/" + str(a.item_sub_group) + "</b> has been defined more than once")
			elif a.selling_uom:
				frappe.throw("<b>" + str(a.particular) + "/" + str(a.selling_uom) + "<b> has been defined more than once")
			else:
				frappe.throw("<b>" + str(a.particular) + "</b> has been defined more than once")
		
	def check_duplicate_settings(self):
		#Check branch duplicate
		item_list = []
		for a in self.item_rates:
			item_list.append(str(str(a.particular) + "/" + str(a.timber_type) + "/" + str(a.item_sub_group)))
		
		branch_list = [str(d.branch) for d in self.get("item_branch")]
		branch_list.append(str("DUMMY"))
	
		for a in frappe.db.sql("select a.branch, b.name from `tabSelling Price Branch` a, `tabSelling Price` b where a.parent = b.name and b.name != %s and a.branch in {0} and (%s between b.from_date and b.to_date or %s between b.from_date and b.to_date or (%s > b.from_date and %s < b.to_date) or (%s < b.from_date and %s > b.to_date))".format(tuple(branch_list)), (self.name, self.from_date, self.to_date, self.from_date, self.to_date, self.from_date, self.to_date), as_dict=1):
			#check for Item duplicate
			doc = frappe.get_doc("Selling Price", a.name)
			for b in doc.item_rates:
				if str(b.particular) + "/" + str(b.timber_type) + "/" + str(b.item_sub_group) in item_list:
					if b.timber_type and b.item_sub_group:
						frappe.throw("<b>"+str(b.particular) + "/" + str(b.timber_type) + "/" + str(b.item_sub_group)+ "</b> already defined for the same period in <b>"+str(frappe.get_desk_link(self.doctype, a.name))+"</b>")
					else:
						frappe.throw("<b>"+str(b.particular) + "</b> already defined for the same period in <b>"+str(frappe.get_desk_link(self.doctype, a.name))+"</b>")


@frappe.whitelist()
def get_cop_amount(cop, branch, posting_date, item_code):
	if not cop or not branch or not posting_date or not item_code:
		frappe.throw("COP, Branch, Item Code and Posting Date are mandatory")
	item_sub_group = frappe.db.get_value("Item", item_code, "item_sub_group")
	if not item_sub_group:
		frappe.db.sql("No Item Sub Group Assigned")
	cop_amount = frappe.db.sql("select cop_amount from `tabCOP Rate Item` where parent = %s and item_sub_group = %s", (cop, item_sub_group), as_dict=1)
	return cop_amount and flt(cop_amount[0].cop_amount) or 0.0


@frappe.whitelist()
def get_selling_rate(price_list, branch, item_code, transaction_date, selling_uom):
	if not branch or not item_code or not transaction_date:
		frappe.throw("Select Item Code or Branch or Posting Date")

	cond = ''
	if selling_uom == '':
		cond += "IF(selling_uom IS NULL,'',selling_uom) = ''"
	else:
		check_loc = frappe.db.sql("""
			select 1 
			from `tabSelling Price` sp, `tabSelling Price Rate` spr 
			where spr.parent = sp.name 
				and spr.particular=%s 
				and spr.selling_uom=%s 
				and sp.to_date >= %s
		""", (item_code, selling_uom, nowdate()))

		if not check_loc:
			cond += " IF(selling_uom IS NULL,'',selling_uom) = ''"
		else:
			cond += " IF(selling_uom IS NULL,'',selling_uom) = %s" % frappe.db.escape(selling_uom)

	query = """
		select selling_price as rate
		from `tabSelling Price Rate`
		where parent=%s and particular=%s and {cond}
	""".format(cond=cond)

	rate = frappe.db.sql(query, (price_list, item_code), as_dict=1)

	if not rate:
		rate = frappe.db.sql("""
			select selling_price as rate 
			from `tabSelling Price Rate` 
			where parent=%s and particular=%s
		""", (price_list, item_code), as_dict=1)

	return rate and flt(rate[0].rate) or 0.0
