# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_columns(filters=None):
	if filters.aggregate:
		if filters.report_by == "Sales Order":
			columns = [
				_("Branch") + ":Link/Sales Order:150", 
				_("Transaction Type") + ":Data:150", 
				_("Location") + ":Link/Location:120",
				_("Sub Item Group") + ":Data:150", 
				_("Sales Qty") + ":Float:120",
				_("Delivered Qty") + ":Float:120",
				_("UOM") + ":Link/UOM:120",
				_("Amount") + ":Currency:120"
			]
		elif filters.report_by == "Sales Invoice":
			columns = [
				_("Branch") + ":Link/Sales Order:150", 
				_("Transaction Type") + ":Data:150", 
				# _("Location") + ":Data/120", 
				# _("Customer") + ":Link/Customer:150",
				# _("Customer Group") + ":Data:200", 
				_("Sub Item Group") + ":Data:150", 
				_("Delivered Qty") + ":Float:120",
				_("UOM") + ":Link/UOM:120",
				_("Amount") + ":Currency:120",
				_("Net Total")+":Currency:120",
			]
		else:
			columns = [
				_("Branch") + ":Link/Sales Order:150", 
				_("Transaction Type") + ":Data:150", 
				# _("Location") + ":Data/120", 
				# _("Customer") + ":Link/Customer:150",
				# _("Customer Group") + ":Data:200", 
				_("Sub Item Group") + ":Data:150", 
				_("Delivered Qty") + ":Float:120",
				_("UOM") + ":Link/UOM:120",
				# _("Amount") + ":Currency:120",
				_("Net Total")+":Currency:120",
			]
	elif filters.summary:
		if filters.report_by == "Sales Order":
			columns = [
				_("Posting Date") + ":Date:100",
				_("Sales Order") + ":Link/Sales Order:100",
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150",
				_("Customer Number") + ":Data:100", 
				_("Customer Group") + ":Data:200", 
				# _("Shipping Address") + ":Data:200", 
				_("Sub Group") + ":Data:100",
				_("Actual Qty") + ":Float:90",
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Amount") + ":Currency:100",
				# _("Discount") + ":Currency:120",
				# _("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120"
			]
		elif filters.report_by == "Sales Invoice":
			columns = [
				_("Posting Date") + ":Date:100",
				_("Sales Invoice") + ":Link/Sales Invoice:100", 
				_("Sales Order") + ":Link/Sales Order:100",
				_("Delivery Note") + ":Link/Delivery Note:100",
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150", 
				_("Customer Number") + ":Data:100", 
				_("Customer Group") + ":Data:200",
				# _("Destination") + ":Data:200",
				_("Sub Group") + ":Data:100", 
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Amount") + ":Currency:100",
				_("Discount") + ":Currency:120",
				# _("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				# _("Vehicle") + ":Link/Vehicle:120", 
				# _("Driver") + ":Data:120", 
				# _("Contact No") + ":Data:120",
				# _("Transporation Rate") + ":Float:100", 
				# _("Distance") + ":Float:100", 
				# _("Transportation Charges") + ":Currency:100"
			]
		else:
			columns = [
				_("Posting Date") + ":Date:100",
				_("Delivery Note") + ":Link/Delivery Note:100", 
				_("Sales Order") + ":Link/Sales Order:100", 
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150", 
				_("Customer Number") + ":Data:100", 
				_("Customer Group") + ":Data:200",
				# _("Destination") + ":Data:200",
				_("Sub Group") + ":Data:100", 
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Amount") + ":Currency:100",
				# _("Discount") + ":Currency:120",
				# _("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				# _("Vehicle") + ":Link/Vehicle:120", 
				# _("Driver") + ":Data:120", 
				# _("Contact No") + ":Data:120",
				# _("Transporation Rate") + ":Float:100", 
				# _("Distance") + ":Float:100", 
				# _("Transportation Charges") + ":Currency:100"
			]
	else:
		if filters.report_by == "Sales Order":
			columns = [
				_("Posting Date") + ":Date:100",
				_("Sales Order") + ":Link/Sales Order:100",
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Location") + ":Link/Location:120",
				_("Transaction Type") + ":Data:150",
				_("Customer") + ":Link/Customer:150",
				_("Customer Group") + ":Data:200",
				_("Shipping Address") + ":Data:200",  
				_("Item Code") + ":Link/Item: 80", 
				_("Item Name") + ":Data:150",
				_("Sub Group") + ":Data:100",
				_("Actual Qty")+ ":Float:100",
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Rate") + ":Float:90",
				_("Amount") + ":Currency:100",
				_("Discount") + ":Currency:120",
				_("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				_("Grand Total")+":Currency:120",
				_("Challan Cost")+":Currency:120"
			]
		elif filters.report_by == "Sales Invoice":
			columns = [
				_("Posting Date") + ":Date:100",
				_("Sales Invoice") + ":Link/Sales Invoice:100",
				_("Sales Order") + ":Link/Sales Order:100",
				_("Delivery Note") + ":Link/Delivery Note:100",
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Location") + ":Link/Location:120",
				_("Transaction Type") + ":Data:150", 
				_("Customer") + ":Link/Customer:150", 
				_("Customer Group") + ":Data:200",
				_("Destination") + ":Data:200",
				_("Item Code") + ":Link/Item: 80", 
				_("Item Name") + ":Data:150",
				_("Sub Group") + ":Data:100", 
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Rate") + ":Float:90",
				_("Amount") + ":Currency:100",
				_("Discount") + ":Currency:120",
				_("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				_("Grand Total")+":Currency:120",
				_("Challan Cost")+":Currency:120",
				_("Transportation Charges") + ":Currency:100",
			]
		else:
			columns = [
				_("Posting Date") + ":Date:100",
				_("Delivery Note") + ":Link/Delivery Note:100",
				_("Sales Order") + ":Link/Sales Order:100",
				_("Region") + ":Data:150",
				_("Branch") + ":Link/Branch:120",
				_("Location") + ":Link/Location:120",
				_("Transaction Type") + ":Data:150",
				_("Customer") + ":Link/Customer:150", 
				_("Customer Group") + ":Data:200",
				_("Destination") + ":Data:200",
				_("Item Code") + ":Link/Item: 80", 
				_("Item Name") + ":Data:150",
				_("Sub Group") + ":Data:100", 
				_("Qty Delivered") + ":Float:90",
				_("UOM") + ":Data:90",
				_("Rate") + ":Float:90",
				_("Amount") + ":Currency:100",
				_("Discount") + ":Currency:120",
				_("Additional Cost") + ":Currency:120",
				_("Net Total")+":Currency:120",
				_("Grand Total")+":Currency:120",
				_("Challan Cost")+":Currency:120",
				_("Transporation Rate") + ":Float:100", 
				_("Distance") + ":Float:100", 
				_("Transportation Charges") + ":Currency:100",
				_("Vehicle No") + ":Link/Vehicle:120", 
				_("Driver") + ":Data:120", 
				_("Contact No") + ":Data:120"
			]

	return columns

def get_data(filters=None):
	cond = get_conditions(filters)
	outer_cond = get_outer_cond(filters)
	data = []

	if filters.report_by == "Sales Order":
		if filters.aggregate:
			cols = """
				so.branch, 
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, so.location, i.item_sub_group, sum(soi.qty) as qty, 
				sum(soi.delivered_qty), soi.uom, so.net_total
			"""
			group_by = " group by so.name, so.branch, so.location, i.item_sub_group"
			order_by = ""
		
		elif filters.summary:
			cols = """
				so.transaction_date, so.name, (select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = so.branch)) as region,
				so.branch, 
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, soi.uom,
				so.customer, (select mobile_no from `tabCustomer` where name=so.customer) as customer_number, so.customer_group, 
				i.item_sub_group, sum(soi.qty) as qty, sum(soi.delivered_qty),
				 sum(soi.amount), so.net_total
			"""
			group_by = " group by soi.name"
			order_by = "order by so.transaction_date"
		
		else:
			cols = """ 
				so.transaction_date, so.name, (	select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = so.branch)) as region,
				so.branch, so.location, 
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type,
				so.customer, so.customer_group, so.shipping_address,
				soi.item_code, soi.item_name, i.item_sub_group, sum(soi.qty) as qty, 
				sum(soi.delivered_qty), soi.uom,
				sum(soi.rate), sum(soi.amount),
				CASE
					WHEN so.discount_or_cost_amount > 0
					THEN so.discount_or_cost_amount * soi.amount / so.total
					ELSE 0
				END as discount_or_cost_amount, so.additional_cost, 
				CASE
					WHEN so.discount_or_cost_amount > 0
					THEN soi.amount - so.discount_or_cost_amount * soi.amount / so.total
					ELSE soi.amount
				END as amount, so.grand_total, so.challan_cost
			"""
			group_by = "group by soi.name, soi.item_code"
			order_by = "order by so.transaction_date"
		
		query = """
		select * from (
			select {0}
			from `tabSales Order` so 
			inner join `tabSales Order Item` soi on so.name = soi.parent
			inner join `tabItem` i on soi.item_code = i.name
			where so.docstatus = 1
			{1} {2} {3} ) as data where 1 = 1 {4}
			""".format(cols, cond, group_by, order_by, outer_cond)
	elif filters.report_by == "Sales Invoice":
		if filters.aggregate:
			cols = """
				si.branch,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, 
				i.item_sub_group, sum(sii.qty) as qty, sii.stock_uom as uom, sum(sii.amount),
				si.net_total-si.loading_cost-si.challan_cost
			"""
			group_by = " group by si.name, si.branch, si.location, i.item_sub_group"
			order_by = ""

		elif filters.summary:
			cols = """
				si.posting_date, si.name, sii.sales_order, sii.delivery_note,
				(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = si.branch)) as region,
				si.branch,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, 
				si.customer, (select mobile_no from `tabCustomer` where name=si.customer) as customer_number, si.customer_group, 
				i.item_sub_group, sum(sii.qty) as qty, sii.stock_uom as uom, sum(sii.amount),
				CASE
					WHEN si.discount_or_cost_amount > 0
					THEN si.discount_or_cost_amount * sii.amount / si.total
					ELSE 0
				END as discount_or_cost_amount, 
				CASE
					WHEN si.discount_or_cost_amount > 0
					THEN sii.amount - si.discount_or_cost_amount * sii.amount / si.total
					ELSE sii.amount
				END as net_total
			"""
			group_by = "group by sii.name"
			order_by = "order by si.posting_date"

		else:
			cols = """
				si.posting_date, si.name, sii.sales_order, sii.delivery_note,
				(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = si.branch)) as region,
				si.branch, si.location,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, 
				si.customer, si.customer_group, si.shipping_address, 
				sii.item_code, sii.item_name, i.item_sub_group, sum(sii.qty) as qty,
				sii.stock_uom as uom, sum(sii.rate), sum(sii.amount),
				CASE
					WHEN si.discount_or_cost_amount > 0
					THEN si.discount_or_cost_amount * sii.amount / si.total
					ELSE 0
				END as discount_or_cost_amount, si.additional_cost, 
				CASE
					WHEN si.discount_or_cost_amount > 0
					THEN sii.amount - si.discount_or_cost_amount * sii.amount / si.total
					ELSE sii.amount
				END as net_total, si.grand_total,
				si.challan_cost, si.transportation_charges
			"""
			group_by = "group by sii.name, sii.item_code"
			order_by = "order by si.posting_date"
		query = """
			select * from (
			select {0}
			from `tabSales Invoice` si 
			inner join `tabSales Invoice Item` sii on si.name = sii.parent
			inner join `tabItem` i on sii.item_code = i.name
			where si.docstatus = 1
			{1} {2} {3}) as data where 1 = 1 {4}
			""".format(cols, cond, group_by, order_by, outer_cond)
	else:
		if filters.aggregate:
			cols = """
				dn.branch,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, 
				i.item_sub_group, sum(dni.qty) as qty, dni.uom,
				
				dn.net_total-(dn.challan_cost)/(select distinct count(b.item_sub_group) from `tabDelivery Note Item` a JOIN `tabItem` b on a.item_code = b.name where a.parent = dn.name) -(dn.loading_cost)/(select distinct count(b.item_group) from `tabDelivery Note Item` a JOIN `tabItem` b on a.item_code = b.name where a.parent = dn.name)
			"""
			group_by = " group by dn.name, dn.branch, dn.location, i.item_sub_group"
			order_by = ""

		elif filters.summary:
			cols = """
				dn.posting_date, dn.name, dni.against_sales_order,
				(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = dn.branch)) as region,
				dn.branch,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type,
				dn.customer, (select mobile_no from `tabCustomer` where name=dn.customer) as customer_number, dn.customer_group, 
				i.item_sub_group, sum(dni.qty) as qty, dni.uom
					
				dn.net_total-dn.loading_cost-dn.challan_cost
			"""
			group_by = "group by dni.name"
			order_by = "order by dn.posting_date"

		else:
			cols = """
				dn.posting_date, dn.name, dni.against_sales_order, 
				(select cc.parent_cost_center from `tabCost Center` cc where cc.name = (select b.cost_center from `tabBranch` b where b.name = dn.branch)) as region,
				dn.branch, dn.location,
				CASE
					WHEN is_allotment=1 THEN "Is Allotment"
					WHEN is_credit=1 THEN "Is Credit Sale"
					WHEN is_rural_sale=1 THEN "Is Rural Sale"
					WHEN is_export=1 THEN "Is Export"
					WHEN is_kidu_sale=1 THEN "Is Kidu Sale"
					ELSE "None"
				END as transaction_type, 
				dn.customer, dn.customer_group, dn.shipping_address, 
				dni.item_code, dni.item_name, i.item_sub_group, sum(dni.qty) as qty, dni.uom,
				sum(dni.rate), sum(dni.amount),
				CASE
					WHEN dn.discount_or_cost_amount > 0
					THEN dn.discount_or_cost_amount * dni.amount / dn.total
					ELSE 0
				END as discount_or_cost_amount, dn.additional_cost, 
				CASE
					WHEN dn.discount_or_cost_amount > 0
					THEN dni.amount - dn.discount_or_cost_amount * dni.amount / dn.total
					ELSE dni.amount
				END as net_total, dn.grand_total,
				dn.challan_cost, dn.transportation_rate, dn.total_distance, dn.transportation_charges,
				dn.vehicle_no, dn.driver_name, dn.driver_contact_no
			"""
			group_by = "group by dni.name, dni.item_code"
			order_by = "order by dn.posting_date"
		
		query = """
			select * from (
			select {0}
			from `tabDelivery Note` dn 
			inner join `tabDelivery Note Item` dni on dn.name = dni.parent
			inner join `tabItem` i on dni.item_code = i.name
			where dn.docstatus = 1
			{1} {2} {3}) as data where 1 = 1 {4}
			""".format(cols, cond, group_by, order_by, outer_cond)

	data = frappe.db.sql(query)
	return data
	
def get_outer_cond(filters=None):
	outer_cond = ""
	if filters.get("volume"):
		outer_cond += " and data.qty = {0}".format(filters.get("volume"))
	return outer_cond
			
def get_conditions(filters=None):
	cond=""
	all_ccs = []
	if filters.from_date and filters.to_date:
		if filters.report_by == "Sales Order":
			cond += " and so.transaction_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
		elif filters.report_by == "Sales Invoice":
			cond += " and si.posting_date between'" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
		else:
			cond += " and dn.posting_date between'" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"

	if filters.has_challan_cost:
		if filters.report_by == "Delivery Note":
			cond += " and dn.challan_cost > 0"

	if filters.has_loading_cost:
		if filters.report_by == "Delivery Note":
			cond += " and dn.loading_cost > 0"

	if filters.transaction_id:
		if filters.report_by == "Delivery Note":
			cond += " and dn.name = '{}'".format(filters.transaction_id)
		if filters.report_by == "Sales Order":
			cond += " and so.name = '{}'".format(filters.transaction_id)
		if filters.report_by == "Sales Invoice":
			cond += " and si.name = '{}'".format(filters.transaction_id)

	if filters.cost_center:
		all_ccs = get_child_cost_centers(filters.cost_center)
		if filters.report_by == "Sales Order":
			cond += " and so.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
		elif filters.report_by == "Sales Invoice":
			cond += " and si.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
		else:
			cond += " and dn.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	if filters.item_group:
		cond += " and i.item_group = '" + str(filters.item_group) + "'"
	#	cond += " and exists (select 1 from `tabItem` i where i.item_group = '"+ str(filters.item_group) +"' and i.item_code = soi.item_code)"
	
	if filters.customer:
		if filters.report_by == "Sales Order":
			cond += " and so.customer = '"+str(filters.customer)+"'"
		elif filters.report_by == "Sales Invoice":
			cond += " and si.customer = '"+str(filters.customer)+"'"
		else:
			cond += " and dn.customer = '"+str(filters.customer)+"'"

	if filters.customer_group:
		if filters.report_by == "Sales Order":
			cond += " and so.customer_group = '"+str(filters.customer_group)+"'"
		elif filters.report_by == "Sales Invoice":
			cond += " and si.customer_group = '"+str(filters.customer_group)+"'"
		else:
			cond += " and dn.customer_group = '"+str(filters.customer_group)+"'"

	if filters.item_sub_group:
		cond += " and i.item_sub_group = '" + str(filters.item_sub_group) + "'"
		# cond += " and exists(select 1 from `tabItem` i where i.item_sub_group = '"+ str(filters.item_sub_group)+"' and i.item_code = soi.item_code)"

	if filters.item:
		cond += " and i.item_code = '" + str(filters.item) + "'"
	
	if filters.warehouse:
		if filters.report_by == "Sales Order":
			cond += " and soi.warehouse = '" + str(filters.warehouse) + "'"
		elif filters.report_by == "Sales Invoice":
			cond += " and sii.warehouse = '" + str(filters.warehouse) + "'"
		else:
			cond += " and dni.warehouse = '" + str(filters.warehouse) + "'"
	
	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NRDCL','')
		if filters.report_by == "Sales Order":
			cond += " and so.branch = '"+branch+"'"
		elif filters.report_by == "Sales Invoice":
			cond += " and si.branch = '"+branch+"'"
		else:
			cond += " and dn.branch = '"+branch+"'"
	
	if filters.location:
		if filters.report_by == "Delivery Note":
			cond += " and dn.location = '" + str(filters.location) + "'"
		if filters.report_by == "Sales Order":
			cond += " and so.location = '"+ str(filters.location) + "'"

	if filters.uom:
		if filters.report_by == "Sales Order":
			cond += " and soi.uom = '"+str(filters.uom)+"'"
		elif filters.report_by == "Sales Invoice":
			cond += " and sii.stock_uom = '"+str(filters.uom)+"'"
		else:
			cond += " and dni.uom = '"+str(filters.uom)+"'"

	if filters.transaction_type:
		if filters.report_by == "Sales Order":
			if filters.transaction_type == "Is Allotment":
				cond += " and so.is_allotment = 1"
			elif filters.transaction_type == "Is Credit Sale":
				cond += " and so.is_credit = 1"
			elif filters.transaction_type == "Is Rural Sale":
				cond += " and so.is_rural_sale = 1"
			elif filters.transaction_type == "Is Export":
				cond += " and so.is_export = 1"
			elif filters.transaction_type == "Is Kidu Sale":
				cond += " and so.is_kidu_sale = 1"
			else:
				cond += " and so.is_allotment != 1 and so.is_credit != 1 and so.is_rural_sale != 1 and so.is_export != 1 and so.is_kidu_sale != 1"
		elif filters.report_by == "Delivery Note":
			if filters.transaction_type == "Is Allotment":
				cond += " and dn.is_allotment = 1"
			elif filters.transaction_type == "Is Credit Sale":
				cond += " and dn.is_credit = 1"
			elif filters.transaction_type == "Is Rural Sale":
				cond += " and dn.is_rural_sale = 1"
			elif filters.transaction_type == "Is Export":
				cond += " and dn.is_export = 1"
			elif filters.transaction_type == "Is Kidu Sale":
				cond += " and dn.is_kidu_sale = 1"
			else:
				cond += " and dn.is_allotment != 1 and dn.is_credit != 1 and dn.is_rural_sale != 1 and dn.is_export != 1 and dn.is_kidu_sale != 1"
		else:
			if filters.transaction_type == "Is Allotment":
				cond += " and si.is_allotment = 1"
			elif filters.transaction_type == "Is Credit Sale":
				cond += " and si.is_credit = 1"
			elif filters.transaction_type == "Is Rural Sale":
				cond += " and si.is_rural_sale = 1"
			elif filters.transaction_type == "Is Export":
				cond += " and si.is_export = 1"
			elif filters.transaction_type == "Is Kidu Sale":
				cond += " and si.is_kidu_sale = 1"
			else:
				cond += " and si.is_allotment != 1 and si.is_credit != 1 and si.is_rural_sale != 1 and si.is_export != 1 and si.is_kidu_sale != 1"
		# else:
		# 	if filters.transaction_type == "Is Allotment":
		# 		frappe.throw("Filter not applicable for Sales Invoice")
		# 	elif filters.transaction_type == "Is Credit Sale":
		# 		frappe.throw("Filter not applicable for Sales Invoice")
		# 	elif filters.transaction_type == "Is Rural Sale":
		# 		frappe.throw("Filter not applicable for Sales Invoice")
		# 	if filters.transaction_type == "Is Export":
		# 		frappe.throw("Filter not applicable for Sales Invoice")
		# 	elif filters.transaction_type == "Is Kidu Sale":
		# 		frappe.throw("Filter not applicable for Sales Invoice")
		# 	else:
		# 		frappe.throw("Filter not applicable for Sales Invoice")

	return cond
