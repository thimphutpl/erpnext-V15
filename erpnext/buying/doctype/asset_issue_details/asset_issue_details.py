# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, nowdate, get_last_day

class AssetIssueDetails(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        amount: DF.Currency
        asset_rate: DF.Currency
        asset_received_entries: DF.Link | None
        balance_qty: DF.Float
        branch: DF.Link
        brand: DF.Data
        chesis_no: DF.Data | None
        company: DF.Link
        cost_center: DF.ReadOnly | None
        create_single_asset: DF.Check
        emp_branch: DF.Data | None
        employee_name: DF.Data | None
        engine_no: DF.Data | None
        entry_date: DF.Date
        equipment_type: DF.Link | None
        is_existing_asset: DF.Check
        issued_date: DF.Date
        issued_to: DF.Link | None
        item_code: DF.Link
        item_name: DF.Data
        location: DF.Link | None
        model: DF.Data
        purchase_receipt: DF.Link | None
        qty: DF.Int
        reference_code: DF.Link | None
        reg_number: DF.Data | None
        serial_number: DF.Data | None
        uom: DF.Data | None
        warehouse: DF.Link | None
    # end: auto-generated types
    def validate(self):
        if self.asset_received_entries and self.is_existing_asset == 1:
            qty = frappe.db.get_value("Asset Received Entries", self.asset_received_entries, "qty")
            warehouse = frappe.db.get_value("Asset Received Entries", self.asset_received_entries, "warehouse")
            rate = frappe.db.get_value("Asset Received Entries", self.asset_received_entries, "asset_rate")
            issued_qty = frappe.db.sql("""
                                       select sum(ifnull(qty,0)) as qty from `tabAsset Issue Details` where asset_received_entries = '{}'
                                       and docstatus = 1
                                       """.format(self.asset_received_entries),as_dict=1)[0].qty
            if flt(qty) - flt(issued_qty) <= 0:
                frappe.throw("Insufficient Quanitity/All Quantity Issued from Asset Received Entry {}".format(self.asset_received_entries))
            if not warehouse:
                frappe.throw("Warehouse not selected in Asset Received Entry {}".format(self.asset_received_entries))
            if not rate:
                frappe.throw("Asset Rate not set in Asset Received Entry {}".format(self.asset_received_entries))
        self.check_balance_qty()
    def on_submit(self):
        self.check_qty_balance()
        if not self.create_single_asset:
            for i in range(cint(self.qty)):
                self.make_asset(1)
        else:
            self.make_asset(1)

    def on_cancel(self):
        for d in frappe.db.sql("select * from `tabAsset` where asset_issue_details='{}'".format(self.name), as_dict=1):
            if d.docstatus < 2:
                frappe.throw("You cannot cancel the document before cancelling Asset with code <a href='#Form/Asset/{0}'>{0}</a>".format(d.name))

        # if self.reference_code:
        #     asset_status = frappe.db.get_value("Asset", self.reference_code, 'docstatus')
        #     if asset_status < 2:
        #         frappe.throw("You cannot cancel the document before cancelling asset with code {0}".format(self.reference_code))    
    
    def check_qty_balance(self):
        if flt(self.qty) > flt(self.balance_qty) and self.is_existing_asset == 1:
            frappe.throw(_("Issuing Quantity cannot be greater than Balance Quantity i.e., {}").format(flt(self.balance_qty)), title="Insufficient Balance")

    def check_balance_qty(self):
        if self.is_existing_asset:
            if not self.asset_received_entries:
                frappe.throw("Asset Received Entry is Required")
            if self.qty > self.balance_qty:
                frappe.throw("Qty cannot be more than balance qty that is "+str(self.balance_qty))
        elif self.purchase_receipt:
            qty=frappe.db.sql("""select sum(received_qty) from `tabPurchase Receipt Item` where parent='{parent}' and item_code='{item_code}'""".format(parent=self.purchase_receipt, item_code=self.item_code))[0][0]
            used_qty= frappe.db.sql("""select sum(qty) from `tabAsset Issue Details` where purchase_receipt='{pr}' and docstatus=1 and item_code='{item_code}'""".format(pr=self.purchase_receipt,item_code=self.item_code))[0][0]
            if str(used_qty)=="None":
                balance_qty=qty
            else:   
                balance_qty = cint(qty) - cint(used_qty)
            if balance_qty ==0:
                frappe.throw("Cannot make Asset Issue Details as balance qty is 0")
            if self.qty > balance_qty:
                frappe.throw("Qty cannot be more than balance qty that is "+str(balance_qty))
    @frappe.whitelist()
    def get_existing_details(self):
        if self.asset_received_entries and self.is_existing_asset == 1:
            qty = frappe.db.get_value("Asset Received Entries", self.asset_received_entries, "qty")
            warehouse = frappe.db.get_value("Asset Received Entries", self.asset_received_entries, "warehouse")
            rate = frappe.db.get_value("Asset Received Entries", self.asset_received_entries, "asset_rate")
            issued_qty = frappe.db.sql("""
                                       select sum(ifnull(qty,0)) as qty from `tabAsset Issue Details` where asset_received_entries = '{}'
                                       and docstatus = 1
                                       """.format(self.asset_received_entries),as_dict=1)[0].qty
            if flt(qty) - flt(issued_qty) <= 0:
                frappe.throw("Insufficient Quanitity/All Quantity Issued from Asset Received Entry {}".format(self.asset_received_entries))
            if not warehouse:
                frappe.throw("Warehouse not selected in Asset Received Entry {}".format(self.asset_received_entries))
            if not rate:
                frappe.throw("Asset Rate not set in Asset Received Entry {}".format(self.asset_received_entries))
            return flt(qty) - flt(issued_qty), warehouse, rate

    def make_asset(self, qty):
        item_doc = frappe.get_doc("Item",self.item_code)
        if not cint(item_doc.is_fixed_asset):
            frappe.throw(_("Item selected is not a fixed asset"))

        if item_doc.asset_category:
            asset_category = frappe.db.get_value("Asset Category", item_doc.asset_category, "name")
            fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
            if item_doc.asset_sub_category:
                for a in frappe.db.sql("""select total_number_of_depreciations, income_depreciation_percent 
                                        from `tabAsset Finance Book` where parent = '{0}' 
                                        and `asset_sub_category`='{1}'
                                        """.format(asset_category, item_doc.asset_sub_category), as_dict=1):
                    total_number_of_depreciations = a.total_number_of_depreciations
                    depreciation_percent = a.income_depreciation_percent
            else:
                frappe.throw(_("No Asset Sub-Category for Item: " +"{}").format(self.item_name))
        else:
            frappe.throw(_("<b>Asset Category</b> is missing for material {}").format(frappe.get_desk_link("Item", self.item_code)))

        item_data = frappe.db.get_value(
            "Item", self.item_code, ["asset_naming_series", "asset_category","asset_sub_category"], as_dict=1
        )
        asset_abbr = frappe.db.get_value('Asset Category',item_data.get("asset_category"),'abbr')
        if not self.create_single_asset:
            asset = frappe.get_doc(
                {
                    "doctype": "Asset",
                    "item_code": self.item_code,
                    "asset_name": self.item_name,
                    # "naming_series": item_data.get("asset_naming_series") or "AST",
                    "asset_category": item_data.get("asset_category"),
                    "asset_sub_category":item_data.get("asset_sub_category"),
                    "abbr": asset_abbr,
                    "cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
                    "company": self.company,
                    "purchase_date": self.entry_date,
                    "calculate_depreciation": 1,
                    "asset_rate": self.asset_rate,
                    "purchase_amount": self.asset_rate,
                    "gross_purchase_amount": flt(self.asset_rate) * flt(qty),
                    "asset_quantity": qty,
                    "purchase_receipt": self.purchase_receipt,
                    "location": self.location,
                    "branch": self.branch,
                    "custodian": self.issued_to,
                    "custodian_name": self.employee_name,
                    "available_for_use_date": self.issued_date,
                    "asset_account": fixed_asset_account,
                    "credit_account": credit_account,
                    "asset_issue_details":self.name,
                    "serial_number":self.reg_number,
                    "next_depreciation_date":get_last_day(self.issued_date)
                }
            )
        else:
            asset = frappe.get_doc(
                {
                    "doctype": "Asset",
                    "item_code": self.item_code,
                    "asset_name": self.item_name,
                    # "naming_series": item_data.get("asset_naming_series") or "AST",
                    "asset_category": item_data.get("asset_category"),
                    "asset_sub_category":item_data.get("asset_sub_category"),
                    "abbr": asset_abbr,
                    "cost_center": frappe.db.get_value("Branch", self.branch, "cost_center"),
                    "company": self.company,
                    "purchase_date": self.entry_date,
                    "calculate_depreciation": 1,
                    "asset_rate": self.asset_rate,
                    "purchase_amount": self.asset_rate,
                    "gross_purchase_amount": flt(self.asset_rate) * flt(self.qty),
                    "asset_quantity": self.qty,
                    "purchase_receipt": self.purchase_receipt,
                    "location": self.location,
                    "branch": self.branch,
                    "custodian": self.issued_to,
                    "custodian_name": self.employee_name,
                    "available_for_use_date": self.issued_date,
                    "asset_account": fixed_asset_account,
                    "credit_account": credit_account,
                    "asset_issue_details":self.name,
                    "serial_number":self.reg_number,
                    "is_single_asset":1,
                    "next_depreciation_date":get_last_day(self.issued_date)
                }
            )
        asset.flags.ignore_validate = True
        asset.flags.ignore_mandatory = True
        asset.set_missing_values()
        asset.insert()
        # asset.save()
        asset.submit()
        asset_code = asset.name
        
        if not asset_code:
            frappe.throw("Asset not able to create for asset issue no. {}".format(self.name))

def get_permission_query_conditions(user):
    if not user: user = frappe.session.user
    user_roles = frappe.get_roles(user)

    if user == "Administrator" or "System Manager" in user_roles: 
        return

    return """(
        exists(select 1
            from `tabEmployee` as e
            where e.branch = `tabAsset Issue Details`.branch
            and e.user_id = '{user}')
        or
        exists(select 1
            from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
            where e.user_id = '{user}'
            and ab.employee = e.name
            and bi.parent = ab.name
            and bi.branch = `tabAsset Issue Details`.branch)
    )""".format(user=user)

@frappe.whitelist()
def check_item_code(doctype, txt, searchfield, start, page_len, filters):
    cond = ""
    if not filters.get('item_code'):
        frappe.throw("Please select Item Code to fetch Purchase Receipt")
    if not filters.get("branch"):
        if not filters.get("cost_center"):
            frappe.throw("Please select Branch or Cost Center first.")
    if filters.get("branch"):
        cost_center = frappe.db.get_value("Branch",filters.get("branch"),"cost_center")
    if filters.get("cost_center"):
        cost_center = filters.get("cost_center")
    if filters.get('item_code'):
        cond += " ar.item_code = '{}'".format(filters.get('item_code'))
        cond += " and ar.cost_center = '{}'".format(cost_center)
        # cond += " and ar.cost_center = '{}'".format(filters.get("cost_center"))
    query = "select ar.ref_doc from `tabAsset Received Entries` ar where {cond}".format(cond=cond)
    # query = """select ar.ref_doc 
	# 			from `tabAsset Received Entries` ar 
	# 			where {cond}
	# 			and not exists(
	# 				select 1 
	# 				from `tabAsset Issue Details` aid
	# 				where aid.purchase_receipt = ar.ref_doc
	# 				and aid.docstatus != 2
	# 				and (select sum(ad.qty) from `tabAsset Issue Details` ad where ad.docstatus != 2 and ad.purchase_receipt = ar.ref_doc and ad.item_code = '{item}') > ar.qty
	# 			)
	# 		""".format(cond=cond, item=filters.get('item_code'))
 
    return frappe.db.sql(query)

def update_branch():
    for a in frappe.db.sql("select *from `tabAsset Received Entries`", as_dict=True):
        branch = frappe.db.get_value("Branch", {'cost_center':a.cost_center}, 'branch')
        frappe.db.sql("update `tabAsset Received Entries` set branch = '{}' where name='{}'".format(branch,a.name))
    frappe.db.commit()
