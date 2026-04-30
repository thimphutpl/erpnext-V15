# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange
from erpnext.accounts.utils import get_child_cost_centers


def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

def get_data(filters):
	query = """
		select * from 
		(
			select 
				CASE
					WHEN IFNULL(SUM(td.quantity),0) >= ll.total_volume 
						AND MAX(td.transaction_type) = 'Sales Order'
						THEN 'Sold'
					WHEN IFNULL(SUM(td.quantity),0) > 0 
						AND MAX(td.transaction_type) = 'Sales Order'
						THEN 'Partially Sold'

					WHEN IFNULL(SUM(td.quantity),0) >= ll.total_volume 
						AND MAX(td.transaction_type) = 'Stock Entry'
						THEN 'Stock Transferred'

					WHEN IFNULL(SUM(td.quantity),0) > 0 
						AND MAX(td.transaction_type) = 'Stock Entry'
						THEN 'Stock Partially Transferred'

					ELSE 'Unsold'
				END AS status,
				lld.timber_class as timber_class , ll.posting_date as posting_date, lld.item as item_code, lld.item_name, lld.item_sub_group as type, 
				lld.total_volume as volume, lld.total_pieces as pieces, ll.lot_no, monthname(ll.posting_date) as month,ll.branch,ll.warehouse 
			from `tabLot List` ll 
			LEFT JOIN `tabLot List Details` lld
			ON ll.name = lld.parent 
			LEFT JOIN `tabLot List Transaction Details` td
    		ON td.parent = ll.name
			where ll.docstatus=1
			GROUP BY
        		ll.name
		) as data 
		where 
			posting_date >= '{0}' and posting_date <= '{1}'
		""".format(filters.from_date, filters.to_date)

	if filters.cost_center:
		all_ccs = get_child_cost_centers(filters.cost_center)
		query += " and branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NRDCL','')
		query += " and branch = '"+branch+"'"

	if filters.warehouse:
		query+=" and warehouse = \'"+filters.warehouse+"\'"

	if filters.item_group:
		query+=" and type in (select distinct i.item_sub_group from `tabItem` i where i.item_group = \'"+filters.item_group+"\')"

	if filters.item_code:
		query+=" and item_code = \'"+filters.item_code+"\'"
	
	if filters.status:
		query+=" and status = \'"+filters.status+"\'"
	
	if filters.timber_class:
		query+=" and timber_class = \'"+filters.timber_class+"\'"

	data = frappe.db.sql(query, as_dict=True)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options" : "Item",
			"width": 120
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 130
		},
			{
			"fieldname": "timber_class",
			"label": _("Timber Class"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "lot_no",
			"label": _("Lot Number"),
			"fieldtype": "Link",
			"options":"Lot List",
			"width": 120
		},
		{
			"fieldname": "pieces",
			"label": _("Total Pieces"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "volume",
			"label": _("Total Volume"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "branch",
			"label": _("Branch"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 130
		}
	]
	
	return columns

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_warehouse_query(doctype, txt, searchfield, start, page_len, filters):

	return frappe.db.sql("""
		SELECT DISTINCT w.name
		FROM `tabWarehouse` w
		INNER JOIN `tabWarehouse Branch` wb
			ON wb.parent = w.name
		WHERE
			w.disabled = 0
			AND wb.branch = %(branch)s
			AND w.name LIKE %(txt)s
		ORDER BY w.name
		LIMIT %(start)s, %(page_len)s
	""", {
		"branch": filters.get("branch"),
		"txt": f"%{txt}%",
		"start": start,
		"page_len": page_len
	})