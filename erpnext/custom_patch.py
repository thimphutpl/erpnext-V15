import frappe
from erpnext.setup.doctype.employee.employee import create_user
# import pandas as pd
import csv
from frappe.utils import flt, cint, nowdate, getdate, formatdate
import re



def update_asset_account():
	count =0
	assets = frappe.db.sql("""select name from `tabAsset` where docstatus = 0  and asset_account = 'Furniture - NRDCL' """,as_dict=True)
	
	if assets:
		for row in assets:
			# if row.asset_account == "Furniture - NRDCL":
			count +=1
			frappe.db.sql("""
					update `tabAsset` set accumulated_depreciation_account = 'Accumulated depreciation-Furniture - NRDCL', available_for_use_date = '2026-01-01' where name="{0}"
				""".format(row.name))
			# doc.save()
			print(count)

def update_item_in_asset():
	count =0
	assets = frappe.db.sql("""select name, asset_name from `tabAsset` where docstatus = 0  and asset_category = 'Cable Crane' """,as_dict=True)
	
	if assets:
		for row in assets:
			# if row.asset_account == "Furniture - NRDCL":
			count +=1
			# doc = frappe.get_doc("Item", {"item_name", row.asset_name})
			frappe.db.sql("""
					update `tabAsset` set asset_category = "Machinary and Equipment" where name="{0}"
				""".format(row.name))
			# doc.save()
			print(count)

def update_name_in_asset():
	count = 0
	assets = frappe.get_all("Asset", 
		{"asset_category": "Machinary and Equipment"},
		pluck="name"
	)

	for old_name in assets:

		if "-CC-" in old_name:
			if old_name == "AS-CC-260100001":

				# new_name = old_name.replace("-CC-", "-ME-")

				# frappe.rename_doc(
				# 	"Asset",
				# 	old_name,
				# 	new_name,
				# 	force=True,
				# 	merge=False
				# )
				count +=1
				print(count)
				print(old_name, "→", old_name.replace("-None-", "-ME-"))

	# frappe.db.commit()

def update_cc_in_asset():
	PREFIX = "AS-ME-"
	count = 0
	max_no = 260100269
	# 2️⃣ Get CC assets to rename
	cc_assets = frappe.get_all(
		"Asset",
		filters={"name": ["like", "AS-CC-%"], "asset_category": "Machinary and Equipment"},
		pluck="name",
		order_by="name"
	)

	# 3️⃣ Rename incrementally
	for old_name in cc_assets:
		new_name = f"{PREFIX}{max_no}"
		# if old_name == "AS-CC-260100001":

		frappe.rename_doc("Asset", old_name, new_name, force=True)
			
		count += 1
		max_no += 1
	
		print(count)
		print(max_no)
		print(old_name, "→", new_name)

	frappe.db.commit()

def update_ba_in_gl():
	count = 0
	# Get CC assets to rename
	je_entries = frappe.get_all(
		"Journal Entry",
		pluck=["name","business_activity"]
		# filters={"voucher_type": "Journal Entry"},
	)

	gl_entries = frappe.get_all(
		"GL Entry",
		filters={"voucher_type": "Journal Entry"},
	)

	# Rename incrementally
	for gl in gl_entries:
		for je in je_entries:
			if je.name == gl.voucher_no:
				count += 1	
				print(count)

	# frappe.db.commit()

def update_transaction_in_lot():
	doc = frappe.get_doc({
		"doctype": "Lot List Transaction Details",
		"transaction_type": "Sales Order",
		"transaction_id": "SAL-ORD-2026-1727",
		"parent": "SU-ST/06/2026",
		"parentfield": "transaction_details",
		"parenttype": "Lot List",
		"quantity": "365.09",
	})
	doc.insert()

def update_retirement_date():
	from hrms.overrides.employee_master import get_retirement_date
	count = 0
	doc = frappe.get_all(
		"Employee",
		filters={"status": "Active", "date_of_retirement": ["is", "not set"]},
		fields=["date_of_birth", "employee_group", "name"]
	)
	for i in doc:
		# if i.name == "NRDCL2405039":
		retirement_date = get_retirement_date(
			i.date_of_birth,
			i.employee_group
		)
		count += 1
		print(str(count)+". "+str(i.name)+"-"+str(retirement_date))
		frappe.db.set_value(
			"Employee",
			i.name,
			"date_of_retirement",
			retirement_date
		)
		
