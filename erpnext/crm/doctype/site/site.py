# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt, get_datetime, today
from frappe.model.document import Document
from erpnext.crm_utils import add_user_roles, remove_user_roles
from datetime import datetime

class Site(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.crm.doctype.site_distance.site_distance import SiteDistance
        from erpnext.crm.doctype.site_item.site_item import SiteItem
        from erpnext.crm.doctype.site_private_pool.site_private_pool import SitePrivatePool
        from frappe.types import DF

        allow_private_pool: DF.Check
        approval_document: DF.Attach | None
        approval_no: DF.Data
        construction_end_date: DF.Date
        construction_start_date: DF.Date
        construction_type: DF.Link
        customer: DF.Link | None
        customer_group: DF.Link | None
        customer_type: DF.Literal["", "Domestic Customer", "International Customer"]
        distance: DF.Table[SiteDistance]
        dzongkhag: DF.Link
        enabled: DF.Check
        extension_approval_document: DF.Attach | None
        extension_till_date: DF.Date | None
        full_name: DF.ReadOnly | None
        gewog: DF.Link | None
        items: DF.Table[SiteItem]
        latitude: DF.Data | None
        location: DF.SmallText | None
        longitude: DF.Data | None
        number_of_floors: DF.Data | None
        plot_no: DF.Data | None
        private_pool: DF.Table[SitePrivatePool]
        product_category: DF.Link
        purpose: DF.Link | None
        remarks: DF.LongText | None
        site_registration: DF.Link | None
        site_type: DF.Link
        territory: DF.Link | None
        user: DF.Link
    # end: auto-generated types
    def validate(self):
        self.validate_defaults()
        self.add_user_roles()
        self.validate_items()
        self.update_customer()

    def on_trash(self):
        """ remove role `CRM Customer` if no sites available for the user """
        if not frappe.db.exists("Site", {"user": self.user, "name": ("!=", self.name)}):
            remove_user_roles(self.user, "CRM Customer")

    def add_user_roles(self):
        """ add role `CRM Customer` """
        add_user_roles(self.user, "CRM Customer")

    def update_customer(self):
        """ create/update Customer based on CID """
        if frappe.db.exists("Customer", {"customer_id": self.user}):
            #doc = frappe.get_doc("Customer", {"customer_id": self.user})
            return
        else:
            doc = frappe.new_doc("Customer")

        ua = frappe.get_doc("User Account", self.user)
        customer_address = [ua.first_name, ua.last_name, ua.billing_address_line1, ua.billing_address_line2,
                    ua.billing_dzongkhag, ua.billing_gewog, ua.billing_pincode]
        customer_address = [i for i in customer_address if i]
        customer_address = "\n".join(customer_address) if customer_address else doc.customer_details
        doc.customer_name = ua.full_name if ua.full_name else frappe.db.get_value("User", self.user, "full_name")    
        doc.customer_type = self.customer_type if self.customer_type else "Domestic Customer"
        doc.customer_group= self.customer_group if self.customer_group else "Domestic"
        doc.territory      = self.territory if self.territory else "Bhutan"

        if self.customer_group:
            cg = frappe.get_doc("Customer Group", self.customer_group)
            doc.customer_id = ua.user
            if cg.document_type == "Citizenship ID":
                doc.customer_id = ua.user
            elif cg.document_type == "License Number":
                doc.license_no = ua.user
            elif cg.document_type == "Reference Number":
                doc.reference_no = ua.user
            elif cg.document_type == "License/Reference Number":
                doc.reference_no = ua.user
        else:
            doc.customer_id      = ua.user

        doc.dzongkhag      = ua.billing_dzongkhag if ua.billing_dzongkhag else self.dzongkhag
        doc.mobile_no      = ua.mobile_no if ua.mobile_no else doc.mobile_no
        doc.customer_details = customer_address
        doc.save(ignore_permissions=True)
        self.customer      = doc.name

    def validate_defaults(self):
        """ basic validations  """
        if get_datetime(self.construction_end_date) <= get_datetime(self.construction_start_date):
            frappe.throw(_("Construction End Date cannot be on or before Construction Start Date"))
        self.extension_till_date = self.construction_end_date if not self.extension_till_date else self.extension_till_date

    def validate_items(self):
        dup = {}
        for i in self.get("items"):
            '''########## Ver.2020.11.10 Begins, Phase-II by SHIV ##########'''
            # following code is added as a replacement for the subsequent by SHIV on 2020/11/10 as part of Phase-II
            if i.product_category in dup:
                frappe.throw(_("Row#{0}: Duplication of material {1} not permitted").format(i.idx, i.product_category))
            else:
                dup[i.product_category] = 1

            # following code is replaced by the above one by SHIV on 2020/11/10 as part of Phase-II
            '''
            if i.item_sub_group in dup:
                frappe.throw(_("Row#{0}: Duplication of material {1} not permitted").format(i.idx, i.item_sub_group))
            else:
                dup[i.item_sub_group] = 1
            '''
            '''########## Ver.2020.11.10 Ends, Phase-II ##########'''
            
            if flt(i.expected_quantity) < 0:
                frappe.throw(_("Row#{0}: Expected Quantity cannot be a negative value").format(i.idx))
            i.overall_expected_quantity  = flt(i.expected_quantity) + flt(i.extended_quantity)
            i.balance_quantity  = flt(i.expected_quantity) + flt(i.extended_quantity) - flt(i.ordered_quantity)

@frappe.whitelist()
def site_active(site):
    return frappe.db.get_value("Site", site, "enabled")

@frappe.whitelist()
def has_pending_transactions(site):
    return frappe.db.sql("""select count(*) from `tabCustomer Order`
        where site = "{site}" and docstatus = 1 and ifnull(total_balance_amount,0) > 0
    """.format(site=site))[0][0]
 
@frappe.whitelist()
def change_site_status():
    sites = frappe.db.sql("""
        select name, enabled, construction_start_date, construction_end_date from `tabSite`
    """,as_dict = 1)
    if sites:
        for site in sites:
            site_status = frappe.db.get_value("Site Status",{"site": site.name},"name")
            if site_status:
                ss = frappe.get_doc("Site Status",site_status)
                if ss:
                    if ss.docstatus == 1:
                        if datetime.strptime(today(),'%Y-%m-%d').date() >= datetime.strptime(str(site.construction_start_date),"%Y-%m-%d").date() and datetime.strptime(today(),'%Y-%m-%d').date() <= datetime.strptime(str(site.construction_end_date),"%Y-%m-%d").date():
                            if ss.current_status == 'Inactive':
                                frappe.db.sql("""
                            	              update `tabSite Status` set current_status = 'Active',
                            	              change_status = 'Deactivate'
                            	              """)
                                if site.enabled == 0:
                                    frappe.db.sql("""update `tabSite` set enabled = 1 where name = '{}'""".format(site.name))
                        elif datetime.strptime(today(),'%Y-%m-%d').date() >= datetime.strptime(str(site.construction_end_date),"%Y-%m-%d").date():
                            if ss.current_status == "Active":
                                frappe.db.sql("""
                            	              update `tabSite Status` set current_status = 'Inactive',
                            	              change_status = 'Activate'
                            	              """)
                                if site.enabled == 1:
                                    frappe.db.sql("""update `tabSite` set enabled = 0 where name = '{}'""".format(site.name))
                            
          
            
            