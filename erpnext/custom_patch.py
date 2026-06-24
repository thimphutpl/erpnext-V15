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
		
def cancel_asset():
	asset_names = [ 
		"AS-FF-260100038-1",
		"AS-FF-260100040-1",
		"AS-FF-260100066-1",
		"AS-FF-260100314-1",
		"AS-FF-260100316-1",
		"AS-FF-260100318-1",
		"AS-FF-260100320-1",
		"AS-FF-260100322-1",
		"AS-FF-260100324-1",
		"AS-FF-260100326-1",
		"AS-FF-260100328-1",
		"AS-FF-260100330-1",
		"AS-FF-260100332-1",
		"AS-FF-260100334-1",
		"AS-FF-260100336-1",
		"AS-FF-260100338-1",
		"AS-FF-260100340-1",
		"AS-FF-260100342-1",
		"AS-FF-260100344-1",
		"AS-FF-260100346-1",
		"AS-FF-260100348-1",
		"AS-FF-260100350-1",
		"AS-FF-260100352-1",
		"AS-FF-260100354-1",
		"AS-FF-260100356-1",
		"AS-FF-260100358-1",
		"AS-FF-260100360-1",
		"AS-FF-260100362-1",
		"AS-FF-260100364-1",
		"AS-FF-260100366-1",
		"AS-FF-260100368-1",
		"AS-FF-260100370-1",
		"AS-FF-260100372-1",
		"AS-FF-260100374-1",
		"AS-FF-260100376-1",
		"AS-FF-260100378-1",
		"AS-FF-260100380-1",
		"AS-FF-260100382-1",
		"AS-FF-260100384-1",
		"AS-FF-260100386-1",
		"AS-FF-260100388-1",
		"AS-FF-260100390-1",
		"AS-FF-260100392-1",
		"AS-FF-260100394-1",
		"AS-FF-260100396-1",
		"AS-FF-260100398-1",
		"AS-FF-260100404-1",
		"AS-FF-260100406-1",
		"AS-OE-260100550-1",
		"AS-OE-260100554-1",
		"AS-OE-260100556-1",
		"AS-OE-260100558-1",
		"AS-OE-260100560-1",
		"AS-OE-260100562-1",
		"AS-OE-260100564-1",
		"AS-OE-260100566-1",
		"AS-OE-260100568-1",
		"AS-OE-260100570-1",
		"AS-OE-260100572-1",
		"AS-OE-260100574-1",
		"AS-OE-260100576-1",
	]
	count = 0
	for asset_name in asset_names:
		count+=1
		asset = frappe.get_doc("Asset", asset_name)
		if asset.docstatus == 1:
			asset.cancel()
			print(str(count)+": "+str(asset_name))
	frappe.db.commit()
	print(count)
		
def update_docstatus_of_cancelled_asset():
	asset_names = [ 
		"AS-FF-260100014",
"AS-FF-260100016",
"AS-FF-260100018",
"AS-FF-260100020",
"AS-FF-260100022",
"AS-OE-260100024",
"AS-OE-260100426",
"AS-OE-260100428",
"AS-OE-260100430",
"AS-OE-260100432",
"AS-OE-260100434",
"AS-OE-260100436",
"AS-OE-260100438",
"AS-OE-260100440",
"AS-OE-260100442",
"AS-OE-260100462",
"AS-OE-260100464",
"AS-OE-260100466",
"AS-OE-260100468",
"AS-OE-260100470",
	]
	count = 0
	for asset_name in asset_names:
		asset = frappe.get_doc("Asset", asset_name)
		count += 1
		print(str(count)+": "+str(asset_name))
		new_asset = frappe.copy_doc(asset)
		new_asset.amended_from = asset.name
		new_asset.docstatus = 0
		new_asset.custodian = "NRDCL2403008"
		new_asset.custodian_name = "Tenzin Wangchuk"
		new_asset.branch = "Mongar"
		new_asset.cost_center = "Mongar - NRDCL"
		new_asset.insert()
		new_asset.submit()
	# frappe.db.commit()
	print(count)

def update_pol_entry():
	pols = frappe.get_all(
		"POL Receive",
		filters={"docstatus": 1, "fuel_type": ["is", "set"]},
		fields={"equipment","fuel_type","branch","posting_date","posting_time","total_qty","name","fuelbook","company"}
	)
	count = 0
	for pol in pols:
		count += 1
		container = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", pol.equipment, "equipment_type"), "is_container")
		direct_consumption = frappe.db.get_value("Equipment Type", frappe.db.get_value("Equipment", pol.equipment, "equipment_type"), "no_own_tank")
		fuelbook_branch = frappe.db.get_value("Fuelbook", pol.fuelbook, "branch")
		if pol.branch == fuelbook_branch:
			own = 1
		else:
			own = 0

		con = frappe.new_doc("POL Entry")
		con.flags.ignore_permissions = 1	
		con.equipment = pol.equipment
		con.pol_type = pol.fuel_type
		con.branch = pol.branch
		con.date = pol.posting_date
		con.posting_time = pol.posting_time
		con.qty = pol.total_qty
		con.company = pol.company
		con.reference_type = "POL Receive"
		con.reference_name = pol.name
		con.is_opening = 0
		con.own_cost_center = own
		if container:
			con.type = "Stock"
			con.insert()
		
		if direct_consumption == 0:
			con1 = frappe.new_doc("POL Entry")
			con1.flags.ignore_permissions = 1	
			con1.company = pol.company
			con1.equipment = pol.equipment
			con1.pol_type = pol.fuel_type
			con1.branch = pol.branch
			con1.date = pol.posting_date
			con1.posting_time = pol.posting_time
			con1.qty = pol.total_qty
			con1.reference_type = "POL Receive"
			con1.reference_name = pol.name
			con1.type = "Receive"
			con1.is_opening = 0
			con1.own_cost_center = own
			con1.insert()
			
			if container:
				con2 = frappe.new_doc("POL Entry")
				con2.flags.ignore_permissions = 1	
				con2.company = pol.company
				con2.equipment = pol.equipment
				con2.pol_type = pol.fuel_type
				con2.branch = pol.branch
				con2.date = pol.posting_date
				con2.posting_time = pol.posting_time
				con2.qty = pol.total_qty
				con2.reference_type = "POL Receive"
				con2.reference_name = pol.name
				con2.type = "Issue"
				con2.is_opening = 0
				con2.own_cost_center = own
				con2.insert()
	frappe.db.commit()
	print(count)