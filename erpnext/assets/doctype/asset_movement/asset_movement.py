# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_link_to_form

from erpnext.assets.doctype.asset_activity.asset_activity import add_asset_activity


class AssetMovement(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.assets.doctype.asset_movement_item.asset_movement_item import AssetMovementItem
		from frappe.types import DF

		amended_from: DF.Link | None
		assets: DF.Table[AssetMovementItem]
		attachment: DF.Attach | None
		based_on: DF.Literal["", "Custodian", "Cost Center"]
		company: DF.Link
		cost_center: DF.Link | None
		from_employee: DF.Link | None
		project: DF.Link | None
		purpose: DF.Literal["", "Transfer", "Receipt"]
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		to_employee: DF.Link | None
		to_single: DF.Check
		transaction_date: DF.Datetime
		workflow_state: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.validate_asset()
		self.validate_cost_center()
		self.validate_employee()

	def validate_asset(self):
		for d in self.assets:
			status, company = frappe.db.get_value("Asset", d.asset, ["status", "company"])
			if self.purpose == "Transfer" and status in ("Draft", "Scrapped", "Sold"):
				frappe.throw(_("{0} asset cannot be transferred").format(status))

			if company != self.company:
				frappe.throw(_("Asset {0} does not belong to company {1}").format(d.asset, self.company))

			if not (d.source_cost_center or d.target_cost_center or d.from_employee or d.to_employee):
				frappe.throw(_("Either cost center or employee must be required"))

	def validate_cost_center(self):
		for d in self.assets:
			if self.purpose in ["Transfer", "Issue"]:
				current_cost_center = frappe.db.get_value("Asset", d.asset, "cost_center")
				if d.source_cost_center:
					if current_cost_center != d.source_cost_center:
						frappe.throw(
							_("Asset {0} does not belongs to the cost center {1}").format(
								d.asset, d.source_cost_center
							)
						)
				else:
					d.source_cost_center = source_cost_center

			if self.purpose == "Issue":
				# if d.target_cost_center:
				# 	frappe.throw(
				# 		_(
				# 			"Issuing cannot be done to a location. Please enter employee to issue the Asset {0} to"
				# 		).format(d.asset),
				# 		title=_("Incorrect Movement Purpose"),
				# 	)
				if not d.to_employee:
					frappe.throw(_("Employee is required while issuing Asset {0}").format(d.asset))

			# if self.purpose == "Transfer":
			# 	if d.to_employee:
			# 		frappe.throw(
			# 			_(
			# 				"Transferring cannot be done to an Employee. Please enter location where Asset {0} has to be transferred"
			# 			).format(d.asset),
			# 			title=_("Incorrect Movement Purpose"),
			# 		)
			# 	if not d.target_location:
			# 		frappe.throw(
			# 			_("Target Location is required while transferring Asset {0}").format(d.asset)
			# 		)
			# 	if d.source_location == d.target_location:
			# 		frappe.throw(_("Source and Target Location cannot be same"))

			if self.purpose == "Transfer":
				if not (d.to_employee or d.target_cost_center):
					frappe.throw(
						_("Target Cost Center or Employee is required while transferring Asset {0}").format(d.asset)
					)

				if d.to_employee and d.target_location:
					frappe.msgprint(
						_("Asset {0} will be transferred to Cost Center {1} and Employee {2}").format(
							d.asset, d.target_cost_center, d.to_employee
						)
					)
				elif d.to_employee:
					frappe.msgprint(
						_("Asset {0} will be transferred to Employee {1} only").format(
							d.asset, d.to_employee
						)
					)
				elif d.target_cost_center:
					frappe.msgprint(
						_("Asset {0} will be transferred to Cost Center {1} only").format(
							d.asset, d.target_cost_center
						)
					)

			if self.purpose == "Receipt":
				if not (d.source_location) and not (d.target_location or d.to_employee):
					frappe.throw(
						_("Target Location or To Employee is required while receiving Asset {0}").format(
							d.asset
						)
					)
				elif d.source_location:
					if d.from_employee and not d.target_location:
						frappe.throw(
							_(
								"Target Location is required while receiving Asset {0} from an employee"
							).format(d.asset)
						)
					elif d.to_employee and d.target_location:
						frappe.throw(
							_(
								"Asset {0} cannot be received at a location and given to an employee in a single movement"
							).format(d.asset)
						)

	def get_assets_for_employee(self):
		if self.from_employee:
			# Clear current assets in table
			self.assets = []

			# Fetch assets assigned to the selected employee
			assets = frappe.db.get_all(
				"Assets",
				filters={"custodian": self.from_employee, "company": self.company},
				fields=["name as asset", "location as source_location"]
			)

			# Add each asset to the assets table
			for asset in assets:
				self.append("assets", asset)
            
	def on_asset_fetch_button_click(self):
		# Call the function to fetch assets
		self.get_assets_for_employee()

	def validate_employee(self):
    	# Existing validation for employee's ownership
		if self.from_employee:
			current_custodian = frappe.db.get_value("Asset", self.assets, "custodian")
			
			if current_custodian != self.from_employee:
				frappe.throw(_("Asset does not belong to custodian {0}").format(self.from_employee))
            
		# Call function to fetch assets
		self.get_assets_for_employee()	
	
	def validate_employee(self):
		for d in self.assets:
			if d.from_employee:
				current_custodian = frappe.db.get_value("Asset", d.asset, "custodian")

				if current_custodian != d.from_employee:
					frappe.throw(
						_("Asset {0} does not belongs to the custodian {1}").format(d.asset, d.from_employee)
					)

			if d.to_employee and frappe.db.get_value("Employee", d.to_employee, "company") != self.company:
				frappe.throw(
					_("Employee {0} does not belongs to the company {1}").format(d.to_employee, self.company)
				)

	def on_submit(self):
		self.set_latest_location_and_custodian_in_asset()

	def on_cancel(self):
		self.set_latest_location_and_custodian_in_asset()

	def set_latest_location_and_custodian_in_asset(self):
		current_location, current_employee = "", ""
		cond = "1=1"

		for d in self.assets:
			args = {"asset": d.asset, "company": self.company}

			# latest entry corresponds to current document's location, employee when transaction date > previous dates
			# In case of cancellation it corresponds to previous latest document's location, employee
			latest_movement_entry = frappe.db.sql(
				f"""
				SELECT asm_item.target_location, asm_item.to_employee
				FROM `tabAsset Movement Item` asm_item, `tabAsset Movement` asm
				WHERE
					asm_item.parent=asm.name and
					asm_item.asset=%(asset)s and
					asm.company=%(company)s and
					asm.docstatus=1 and {cond}
				ORDER BY
					asm.transaction_date desc limit 1
				""",
				args,
			)
			if latest_movement_entry:
				current_location = latest_movement_entry[0][0]
				current_employee = latest_movement_entry[0][1]

			frappe.db.set_value("Asset", d.asset, "location", current_location, update_modified=False)
			frappe.db.set_value("Asset", d.asset, "custodian", current_employee, update_modified=False)

			if current_location and current_employee:
				add_asset_activity(
					d.asset,
					_("Asset received at Location {0} and issued to Employee {1}").format(
						get_link_to_form("Location", current_location),
						get_link_to_form("Employee", current_employee),
					),
				)
			elif current_location:
				add_asset_activity(
					d.asset,
					_("Asset transferred to Location {0}").format(
						get_link_to_form("Location", current_location)
					),
				)
			elif current_employee:
				add_asset_activity(
					d.asset,
					_("Asset issued to Employee {0}").format(get_link_to_form("Employee", current_employee)),
				)	

	@frappe.whitelist()
	def get_asset_list(self):
		if not self.from_employee and self.based_on == 'Custodian' or not self.cost_center and self.based_on == 'Cost Center':
			frappe.throw("From Employee/Cost Center is required.")
		else:
			# if self.to_single:
			# 	if not self.to_employee:
			# 		frappe.throw("To Employee is Mandatory")
			# 	elif self.from_employee == self.to_employee:
			# 		frappe.throw("Select Different Employee")
			condition_statement=''
			if self.based_on == 'Custodian':
				condition_statement = f"custodian = '{self.from_employee}'"
			else:
				condition_statement = f"cost_center = '{self.cost_center}'"
			
			asset_list = frappe.db.sql("""
				select name, custodian_name, custodian, cost_center
				from `tabAsset` 
				where {cond} 
				and docstatus = 1 
				""".format(cond=condition_statement),as_dict = 1)
			if asset_list:
				self.set("assets",[])
				for x in asset_list:
					row = self.append("assets",{})
					data = {"asset":x.name, 
							"from_employee":x.custodian,
							"from_employee_name":x.custodian_name, 
							"source_cost_center":x.cost_center,
							}
					row.update(data)
			else:
				frappe.msgprint(f"No Assets registered with given Custodian/Cost Center", title="Notification", indicator='green')

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles: 
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.branch = `tabAsset Movement`.branch
			and e.user_id = '{user}')
		or
		exists(select 1
			from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
			where e.user_id = '{user}'
			and ab.employee = e.name
			and bi.parent = ab.name
			and bi.branch = `tabPurchase Invoice`.branch)
	)""".format(user=user)				