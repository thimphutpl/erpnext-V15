# # Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# # License: GNU General Public License v3. See license.txt

# import json
# import frappe
# import frappe.defaults
# from frappe import _, msgprint, qb
# from frappe.contacts.address_and_contact import (
# 	delete_contact_and_address,
# 	load_address_and_contact,
# )
# from frappe.model.mapper import get_mapped_doc
# from frappe.model.naming import set_name_by_naming_series, set_name_from_naming_options
# from frappe.model.utils.rename_doc import update_linked_doctypes
# from frappe.utils import cint, cstr, flt, get_formatted_email, today
# from frappe.utils.deprecations import deprecated
# from frappe.utils.user import get_users_with_role

# from erpnext.accounts.party import get_dashboard_info, validate_party_accounts
# from erpnext.controllers.website_list_for_contact import add_role_for_portal_user
# from erpnext.utilities.transaction_base import TransactionBase

# class Customer(TransactionBase):
# 	# begin: auto-generated types
# 	# This code is auto-generated. Do not modify anything in this block.

# 	from typing import TYPE_CHECKING

# 	if TYPE_CHECKING:
# 		from erpnext.accounts.doctype.allowed_to_transact_with.allowed_to_transact_with import AllowedToTransactWith
# 		from erpnext.accounts.doctype.party_account.party_account import PartyAccount
# 		from erpnext.selling.doctype.customer_credit_limit.customer_credit_limit import CustomerCreditLimit
# 		from erpnext.selling.doctype.sales_team.sales_team import SalesTeam
# 		from erpnext.utilities.doctype.portal_user.portal_user import PortalUser
# 		from frappe.types import DF

# 		account_manager: DF.Link | None
# 		account_number: DF.Data | None
# 		accounts: DF.Table[PartyAccount]
# 		bank_account_type: DF.Link | None
# 		bank_branch: DF.Link | None
# 		bank_name: DF.Link | None
# 		branch: DF.Link | None
# 		companies: DF.Table[AllowedToTransactWith]
# 		cost_center: DF.Link | None
# 		credit_limits: DF.Table[CustomerCreditLimit]
# 		customer_details: DF.Text | None
# 		customer_group: DF.Link
# 		customer_name: DF.Data
# 		customer_pos_id: DF.Data | None
# 		customer_primary_address: DF.Link | None
# 		customer_primary_contact: DF.Link | None
# 		# customer_type: DF.Literal["", "Domestic Customer", "International Customer"] 
# 		customer_type: DF.Literal["", "Company", "Individual"] 
# 		default_bank_account: DF.Link | None
# 		default_commission_rate: DF.Float
# 		default_currency: DF.Link | None
# 		default_price_list: DF.Link | None
# 		default_sales_partner: DF.Link | None
# 		disabled: DF.Check
# 		dn_required: DF.Check
# 		email_id: DF.ReadOnly | None
# 		gender: DF.Link | None
# 		image: DF.AttachImage | None
# 		industry: DF.Link | None
# 		inr_bank_code: DF.Literal["", "01 - AXIS BANK", "02- SBI", "03 -Others", "04 - SCB"]
# 		inr_purpose_code: DF.Literal["", "01- INVT IN EQUITY SHARE", "02- INVT IN MUTUAL FUND", "03- INVT IN DEBENTURES", "04- BILL PAYMENT", "05- CREDIT TO NRE A/c", "06- PAYMENT TO HOTELS", "07- TRAVEL & TOURISM", "08- INVT IN REAL ESTATE", "09- PYMNT TO ESTATE DEVELOPER", "10- LIC PREMIUM", "11- EDUCATIONAL EXPENSES", "12- FAMILY MAINTENANCE", "13- POSTMASTER / UTI PREMIUM", "14- PROPERTY Pymnt-Co-op Hsg.Soc", "15- PROPERTY Pymnt-Govt. Hsg.Scheme", "16- MEDICAL EXPENSES", "17- UTILITY PAYMENTS", "18- TAX PAYMENTS", "19- EMI FOR LOAN REPAYMENT", "20- COMPENSATION OF EMPLOYEES", "21- SALARY"]
# 		is_frozen: DF.Check
# 		is_internal_customer: DF.Check
# 		language: DF.Link | None
# 		lead_name: DF.Link | None
# 		location: DF.Link | None
# 		loyalty_program: DF.Link | None
# 		loyalty_program_tier: DF.Data | None
# 		market_segment: DF.Link | None
# 		mobile_no: DF.ReadOnly | None
# 		naming_series: DF.Literal["CUST-", "CUST-.YYYY.-"]
# 		opportunity_name: DF.Link | None
# 		payment_terms: DF.Link | None
# 		portal_users: DF.Table[PortalUser]
# 		primary_address: DF.Text | None
# 		represents_company: DF.Link | None
# 		sales_team: DF.Table[SalesTeam]
# 		salutation: DF.Link | None
# 		so_required: DF.Check
# 		status: DF.Literal["Active", "Dormant", "Open"]
# 		tax_category: DF.Link | None
# 		tax_id: DF.Data | None
# 		tax_withholding_category: DF.Link | None
# 		telephone_and_fax: DF.Link | None
# 		territory: DF.Link
# 		website: DF.Data | None
# 	# end: auto-generated types
# 	def get_feed(self):
# 		return self.customer_name

# 	def onload(self):
# 		"""Load address and contacts in `__onload`"""
# 		load_address_and_contact(self, "customer")

# 	def autoname(self):
# 		cust_master_name = frappe.defaults.get_global_default('cust_master_name')
# 		if cust_master_name == 'Customer Name':
# 			self.name = self.get_customer_name()
# 		else:
# 			if not self.naming_series:
# 				frappe.throw(_("Series is mandatory"), frappe.MandatoryError)

# 			self.name = make_autoname(self.naming_series+'.#####')

# 	def get_customer_name(self):
# 		if frappe.db.get_value("Customer", self.customer_name):
# 			count = frappe.db.sql("""select ifnull(max(SUBSTRING_INDEX(name, ' ', -1)), 0) from tabCustomer
# 				 where name like %s""", "%{0} - %".format(self.customer_name), as_list=1)[0][0]
# 			count = cint(count) + 1
# 			return "{0} - {1}".format(self.customer_name, cstr(count))

# 		return self.customer_name

# 	def validate(self):
# 		self.flags.is_new_doc = self.is_new()
# 		validate_party_accounts(self)
# 		# self.status = get_party_status(self)
# 		self.check_id_required()
# 		#self.check_duplication()

# 	def check_duplication(self):
# 		customer = frappe.db.sql("""select customer_id, customer_name from tabCustomer where disabled != 1""",as_dict =1)
# 		for a in customer:
# 			if self.customer_id == a.customer_id:
# 				frappe.throw("Customer ID, {0} already exist for the customer {1}".format(self.customer_id, a.customer_name))

# 	def check_id_required(self):
# 		if self.customer_group == "Domestic" and not self.customer_id:
# 			frappe.throw("CID or License No is mandatory for domestic customers")

# 	def update_lead_status(self):
# 		if self.lead_name:
# 			frappe.db.sql("update `tabLead` set status='Converted' where name = %s", self.lead_name)

# 	def update_address(self):
# 		frappe.db.sql("""update `tabAddress` set customer_name=%s, modified=NOW()
# 			where customer=%s""", (self.customer_name, self.name))

# 	def update_contact(self):
# 		frappe.db.sql("""update `tabContact` set customer_name=%s, modified=NOW()
# 			where customer=%s""", (self.customer_name, self.name))

# 	def create_lead_address_contact(self):
# 		if self.lead_name:
# 			if not frappe.db.get_value("Address", {"lead": self.lead_name, "customer": self.name}):
# 				frappe.db.sql("""update `tabAddress` set customer=%s, customer_name=%s where lead=%s""",
# 					(self.name, self.customer_name, self.lead_name))

# 			lead = frappe.db.get_value("Lead", self.lead_name, ["lead_name", "email_id", "phone", "mobile_no"], as_dict=True)

# 			c = frappe.new_doc('Contact')
# 			c.first_name = lead.lead_name
# 			c.email_id = lead.email_id
# 			c.phone = lead.phone
# 			c.mobile_no = lead.mobile_no
# 			c.customer = self.name
# 			c.customer_name = self.customer_name
# 			c.is_primary_contact = 1
# 			c.flags.ignore_permissions = self.flags.ignore_permissions
# 			c.autoname()
# 			if not frappe.db.exists("Contact", c.name):
# 				c.insert()

# 	def on_update(self):
# 		self.validate_name_with_customer_group()

# 		self.update_lead_status()
# 		self.update_address()
# 		self.update_contact()

# 		if self.flags.is_new_doc:
# 			self.create_lead_address_contact()

# 	def validate_name_with_customer_group(self):
# 		if frappe.db.exists("Customer Group", self.name):
# 			frappe.throw(_("A Customer Group exists with same name please change the Customer name or rename the Customer Group"), frappe.NameError)

# 	def delete_customer_address(self):
# 		addresses = frappe.db.sql("""select name, lead from `tabAddress`
# 			where customer=%s""", (self.name,))

# 		for name, lead in addresses:
# 			if lead:
# 				frappe.db.sql("""update `tabAddress` set customer=null, customer_name=null
# 					where name=%s""", name)
# 			else:
# 				frappe.db.sql("""delete from `tabAddress` where name=%s""", name)

# 	def delete_customer_contact(self):
# 		for contact in frappe.db.sql_list("""select name from `tabContact`
# 			where customer=%s""", self.name):
# 				frappe.delete_doc("Contact", contact)

# 	def on_trash(self):
# 		self.delete_customer_address()
# 		self.delete_customer_contact()
# 		if self.lead_name:
# 			frappe.db.sql("update `tabLead` set status='Interested' where name=%s",self.lead_name)

# 	def after_rename(self, olddn, newdn, merge=False):
# 		set_field = ''
# 		if frappe.defaults.get_global_default('cust_master_name') == 'Customer Name':
# 			frappe.db.set(self, "customer_name", newdn)
# 			self.update_contact()
# 			set_field = ", customer_name=%(newdn)s"
# 		self.update_customer_address(newdn, set_field)

# 	def update_customer_address(self, newdn, set_field):
# 		frappe.db.sql("""update `tabAddress` set address_title=%(newdn)s
# 			{set_field} where customer=%(newdn)s"""\
# 			.format(set_field=set_field), ({"newdn": newdn}))


# def get_customer_list(doctype, txt, searchfield, start, page_len, filters):
# 	if frappe.db.get_default("cust_master_name") == "Customer Name":
# 		fields = ["name", "customer_group", "territory"]
# 	else:
# 		fields = ["name", "customer_name", "customer_group", "territory"]

# 	match_conditions = build_match_conditions("Customer")
# 	match_conditions = "and {}".format(match_conditions) if match_conditions else ""

# 	return frappe.db.sql("""select %s from `tabCustomer` where docstatus < 2
# 		and (%s like %s or customer_name like %s)
# 		{match_conditions}
# 		order by
# 		case when name like %s then 0 else 1 end,
# 		case when customer_name like %s then 0 else 1 end,
# 		name, customer_name limit %s, %s""".format(match_conditions=match_conditions) %
# 		(", ".join(fields), searchfield, "%s", "%s", "%s", "%s", "%s", "%s"),
# 		("%%%s%%" % txt, "%%%s%%" % txt, "%%%s%%" % txt, "%%%s%%" % txt, start, page_len))


# def check_credit_limit(customer, company):
# 	customer_outstanding = get_customer_outstanding(customer, company)

# 	credit_limit = get_credit_limit(customer, company)
# 	if credit_limit > 0 and flt(customer_outstanding) > credit_limit:
# 		msgprint(_("Credit limit has been crossed for customer {0} {1}/{2}")
# 			.format(customer, customer_outstanding, credit_limit))

# 		# If not authorized person raise exception
# 		credit_controller = frappe.db.get_value('Accounts Settings', None, 'credit_controller')
# 		if not credit_controller or credit_controller not in frappe.get_roles():
# 			throw(_("Please contact to the user who have Sales Master Manager {0} role")
# 				.format(" / " + credit_controller if credit_controller else ""))

# def get_customer_outstanding(customer, company):
# 	# Outstanding based on GL Entries
# 	outstanding_based_on_gle = frappe.db.sql("""select sum(debit) - sum(credit)
# 		from `tabGL Entry` where party_type = 'Customer' and party = %s and company=%s""", (customer, company))

# 	outstanding_based_on_gle = flt(outstanding_based_on_gle[0][0]) if outstanding_based_on_gle else 0

# 	# Outstanding based on Sales Order
# 	outstanding_based_on_so = frappe.db.sql("""
# 		select sum(base_grand_total*(100 - per_billed)/100)
# 		from `tabSales Order`
# 		where customer=%s and docstatus = 1 and company=%s
# 		and per_billed < 100 and status != 'Closed'""", (customer, company))

# 	outstanding_based_on_so = flt(outstanding_based_on_so[0][0]) if outstanding_based_on_so else 0.0

# 	# Outstanding based on Delivery Note
# 	unmarked_delivery_note_items = frappe.db.sql("""select
# 			dn_item.name, dn_item.amount, dn.base_net_total, dn.base_grand_total
# 		from `tabDelivery Note` dn, `tabDelivery Note Item` dn_item
# 		where
# 			dn.name = dn_item.parent
# 			and dn.customer=%s and dn.company=%s
# 			and dn.docstatus = 1 and dn.status not in ('Closed', 'Stopped')
# 			and ifnull(dn_item.against_sales_order, '') = ''
# 			and ifnull(dn_item.against_sales_invoice, '') = ''""", (customer, company), as_dict=True)

# 	outstanding_based_on_dn = 0.0

# 	for dn_item in unmarked_delivery_note_items:
# 		si_amount = frappe.db.sql("""select sum(amount)
# 			from `tabSales Invoice Item`
# 			where dn_detail = %s and docstatus = 1""", dn_item.name)[0][0]

# 		if flt(dn_item.amount) > flt(si_amount) and dn_item.base_net_total:
# 			outstanding_based_on_dn += ((flt(dn_item.amount) - flt(si_amount)) \
# 				/ dn_item.base_net_total) * dn_item.base_grand_total

# 	return outstanding_based_on_gle + outstanding_based_on_so + outstanding_based_on_dn


# def get_credit_limit(customer, company):
# 	credit_limit = None

# 	if customer:
# 		credit_limit, customer_group = frappe.db.get_value("Customer", customer, ["credit_limit", "customer_group"])

# 		if not credit_limit:
# 			credit_limit = frappe.db.get_value("Customer Group", customer_group, "credit_limit")

# 	if not credit_limit:
# 		credit_limit = frappe.db.get_value("Company", company, "credit_limit")

# 	return flt(credit_limit)


# def parse_full_name(full_name):
#     # Custom implementation to split a full name into first, middle, and last names
#     name_parts = full_name.strip().split(" ")
#     first_name = name_parts[0]
#     middle_name = name_parts[1] if len(name_parts) > 2 else ""
#     last_name = name_parts[-1] if len(name_parts) > 1 else ""
#     return first_name, middle_name, last_name










import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, today
from frappe import _
from erpnext.accounts.party import get_dashboard_info, validate_party_accounts
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils.user import get_users_with_role

class Customer(TransactionBase):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from erpnext.accounts.doctype.allowed_to_transact_with.allowed_to_transact_with import AllowedToTransactWith
        from erpnext.accounts.doctype.party_account.party_account import PartyAccount
        from erpnext.selling.doctype.customer_credit_limit.customer_credit_limit import CustomerCreditLimit
        from erpnext.selling.doctype.sales_team.sales_team import SalesTeam
        from erpnext.utilities.doctype.portal_user.portal_user import PortalUser
        from frappe.types import DF

        account_manager: DF.Link | None
        account_number: DF.Data | None
        accounts: DF.Table[PartyAccount]
        bank_account_type: DF.Link | None
        bank_branch: DF.Link | None
        bank_name: DF.Link | None
        branch: DF.Link | None
        companies: DF.Table[AllowedToTransactWith]
        company_code: DF.Link | None
        company_name: DF.Data | None
        cost_center: DF.Link | None
        credit_limits: DF.Table[CustomerCreditLimit]
        customer_details: DF.Text | None
        customer_group: DF.Link
        customer_id: DF.Data | None
        customer_name: DF.Data
        customer_pos_id: DF.Data | None
        customer_primary_address: DF.Link | None
        customer_primary_contact: DF.Link | None
        customer_type: DF.Literal["", "Company", "Individual"]
        default_bank_account: DF.Link | None
        default_commission_rate: DF.Float
        default_currency: DF.Link | None
        default_price_list: DF.Link | None
        default_sales_partner: DF.Link | None
        disabled: DF.Check
        dn_required: DF.Check
        email_id: DF.ReadOnly | None
        gender: DF.Link | None
        image: DF.AttachImage | None
        industry: DF.Link | None
        inr_bank_code: DF.Literal["", "01 - AXIS BANK", "02- SBI", "03 -Others", "04 - SCB"]
        inr_purpose_code: DF.Literal["", "01- INVT IN EQUITY SHARE", "02- INVT IN MUTUAL FUND", "03- INVT IN DEBENTURES", "04- BILL PAYMENT", "05- CREDIT TO NRE A/c", "06- PAYMENT TO HOTELS", "07- TRAVEL & TOURISM", "08- INVT IN REAL ESTATE", "09- PYMNT TO ESTATE DEVELOPER", "10- LIC PREMIUM", "11- EDUCATIONAL EXPENSES", "12- FAMILY MAINTENANCE", "13- POSTMASTER / UTI PREMIUM", "14- PROPERTY Pymnt-Co-op Hsg.Soc", "15- PROPERTY Pymnt-Govt. Hsg.Scheme", "16- MEDICAL EXPENSES", "17- UTILITY PAYMENTS", "18- TAX PAYMENTS", "19- EMI FOR LOAN REPAYMENT", "20- COMPENSATION OF EMPLOYEES", "21- SALARY"]
        inter_company: DF.Check
        is_frozen: DF.Check
        is_internal_customer: DF.Check
        language: DF.Link | None
        lead_name: DF.Link | None
        location: DF.Link | None
        loyalty_program: DF.Link | None
        loyalty_program_tier: DF.Data | None
        market_segment: DF.Link | None
        mobile_no: DF.ReadOnly | None
        naming_series: DF.Literal["CUST-", "CUST-.YYYY.-"]
        opportunity_name: DF.Link | None
        payment_terms: DF.Link | None
        portal_users: DF.Table[PortalUser]
        primary_address: DF.Text | None
        represents_company: DF.Link | None
        sales_team: DF.Table[SalesTeam]
        salutation: DF.Link | None
        so_required: DF.Check
        status: DF.Literal["Active", "Dormant", "Open"]
        tax_category: DF.Link | None
        tax_id: DF.Data | None
        tax_withholding_category: DF.Link | None
        telephone_and_fax: DF.Link | None
        territory: DF.Link
        website: DF.Data | None
    # end: auto-generated types
    
    def get_feed(self):
        return self.customer_name

    def onload(self):
        pass
        """Load address and contacts in `__onload`"""
        # load_address_and_contact(self, "customer")

    def autoname(self):
        cust_master_name = frappe.defaults.get_global_default('cust_master_name')
        if cust_master_name == 'Customer Name':
            self.name = self.get_customer_name()
        else:
            if not self.naming_series:
                frappe.throw(_("Series is mandatory"), frappe.MandatoryError)
            self.name = make_autoname(self.naming_series + '.#####')

    def get_customer_name(self):
        if frappe.db.get_value("Customer", self.customer_name):
            count = frappe.db.sql("""select ifnull(max(SUBSTRING_INDEX(name, ' ', -1)), 0) from tabCustomer
                    where name like %s""", "%{0} - %".format(self.customer_name), as_list=1)[0][0]
            count = cint(count) + 1
            return "{0} - {1}".format(self.customer_name, cstr(count))
        return self.customer_name

    def validate(self):
        self.flags.is_new_doc = self.is_new()
        validate_party_accounts(self)
        self.check_id_required()

    def check_id_required(self):
        if self.customer_group == "Domestic" and not self.customer_id:
            frappe.throw(_("CID or License No is mandatory for domestic customers"))

    def update_lead_status(self):
        if self.lead_name:
            frappe.db.sql("update `tabLead` set status='Converted' where name = %s", self.lead_name)

    def update_address(self):
        frappe.db.sql("""update `tabAddress` set customer_name=%s, modified=NOW()
                        where customer=%s""", (self.customer_name, self.name))

    def update_contact(self):
        frappe.db.sql("""update `tabContact` set customer_name=%s, modified=NOW()
                        where customer=%s""", (self.customer_name, self.name))

    def create_lead_address_contact(self):
        if self.lead_name:
            if not frappe.db.get_value("Address", {"lead": self.lead_name, "customer": self.name}):
                frappe.db.sql("""update `tabAddress` set customer=%s, customer_name=%s where lead=%s""",
                              (self.name, self.customer_name, self.lead_name))

            lead = frappe.db.get_value("Lead", self.lead_name, ["lead_name", "email_id", "phone", "mobile_no"], as_dict=True)

            c = frappe.new_doc('Contact')
            c.first_name = lead.lead_name
            c.email_id = lead.email_id
            c.phone = lead.phone
            c.mobile_no = lead.mobile_no
            c.customer = self.name
            c.customer_name = self.customer_name
            c.is_primary_contact = 1
            c.flags.ignore_permissions = self.flags.ignore_permissions
            c.autoname()
            if not frappe.db.exists("Contact", c.name):
                c.insert()

    def on_update(self):
        self.validate_name_with_customer_group()
        self.update_lead_status()
        self.update_address()
        self.update_contact()
        if self.flags.is_new_doc:
            self.create_lead_address_contact()

    def validate_name_with_customer_group(self):
        if frappe.db.exists("Customer Group", self.name):
            frappe.throw(_("A Customer Group exists with same name please change the Customer name or rename the Customer Group"), frappe.NameError)

    def delete_customer_address(self):
        addresses = frappe.db.sql("""select name, lead from `tabAddress`
                                     where customer=%s""", (self.name,))
        for name, lead in addresses:
            if lead:
                frappe.db.sql("""update `tabAddress` set customer=null, customer_name=null
                                 where name=%s""", name)
            else:
                frappe.db.sql("""delete from `tabAddress` where name=%s""", name)

    def delete_customer_contact(self):
        for contact in frappe.db.sql_list("""select name from `tabContact`
                                            where customer=%s""", self.name):
            frappe.delete_doc("Contact", contact)

    def on_trash(self):
        self.delete_customer_address()
        self.delete_customer_contact()

def parse_full_name(full_name):
    # Custom implementation to split a full name into first, middle, and last names
    name_parts = full_name.strip().split(" ")
    first_name = name_parts[0]
    middle_name = name_parts[1] if len(name_parts) > 2 else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    return first_name, middle_name, last_name