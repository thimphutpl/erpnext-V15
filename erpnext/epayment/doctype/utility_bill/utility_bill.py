# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import requests, json
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.custom_utils import check_future_date
from erpnext.integrations.bank_api import fetch_balance
from erpnext.epayment.doctype.bank_payment.bank_payment import get_transaction_id


class UtilityBill(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.epayment.doctype.utility_bill_item.utility_bill_item import UtilityBillItem
		from frappe.types import DF

		amended_from: DF.Link | None
		bank_account: DF.Data
		bank_balance: DF.Currency
		branch: DF.Link
		company: DF.Link
		cost_center: DF.Link
		expense_account: DF.Link
		item: DF.Table[UtilityBillItem]
		journal_entry: DF.Link | None
		net_payable_amount: DF.Currency
		payment_status: DF.Literal["Draft", "Pending", "Payment Successful", "Payment Failed", "Partial Payment"]
		posting_date: DF.Date
		tds_account: DF.Link | None
		tds_percent: DF.Literal["", "2", "3", "5", "10"]
		total_bill_amount: DF.Currency
		total_tds_amount: DF.Currency
		utility_services: DF.Link
		workflow_state: DF.Link | None
	# end: auto-generated types

	def validate(self):
		check_future_date(self.posting_date)
		self.calculate_tds_net()
		self.get_bank_available_balance()
		self.remove_bill_without_os()
		self.update_pi_number()
		if self.workflow_state == "Waiting For Verification":
			self.payment_status="Pending"
			
	def before_submit(self):
		self.utility_payment()
		self.update_status()
		# if self.payment_status=="Payment Successful":
		#     self.make_direct_payment()
		
	def update_pi_number(self):
		for a in self.get("item"):
			if not a.pi_number:
				a.pi_number = get_transaction_id()

	def get_bank_available_balance(self):
		if self.bank_account and frappe.db.get_value('Bank Payment Settings', "BOBL", 'enable_one_to_one'):
			try:
				result = fetch_balance(self.bank_account)
			except Exception as e:
				frappe.msgprint(_("Unable to fetch Bank Balance.\n  {}").format(str(e)))
			else:
				if result['status'] == "0":
					self.bank_balance = result['balance_amount']
				else:
					frappe.msgprint(_("Unable to fetch Bank Balance.\n  {}").format(result['error']))

	def on_submit(self):
		self.db_set("workflow_state", self.payment_status)
	
	def on_cancel(self):
		if self.workflow_state=="Partial Payment" or self.workflow_state=="Payment Successful":
			frappe.throw("Not allowed to cancel the Utility Bill Payments")
	
	def update_status(self):
		success = failed = 0
		for a in self.item:
			if a.payment_status == "Failed":
				failed += 1
			elif a.payment_status == "Success":
				success += 1
		if success > 0 and failed > 0:
			self.payment_status = "Partial Payment"
		elif failed == 0 and success > 0:
			self.payment_status = "Payment Successful"
		elif failed > 0 and success == 0:
			self.payment_status = "Payment Failed"
		
	def calculate_tds_net(self):
		total_amount = total_tds = net_amount = 0.00
		for a in self.item:
			total_amount += flt(a.invoice_amount)
			total_tds += flt(a.tds_amount)
			net_amount += flt(a.net_amount)
		self.total_bill_amount = total_amount
		self.total_tds_amount = total_tds
		self.net_payable_amount = net_amount
		
		if self.tds_percent and not self.net_payable_amount:
			frappe.throw("Net Payable amount should be greater than zero")
	
	def utility_payment(self):
		# frappe.throw(str("hi"))
		for d in self.item:
			if d.outstanding_amount > 0 and not d.payment_status_code:
				api_name, service_id, service_type, consumer_field = frappe.db.get_value("Utility Service Type", d.utility_service_type, ["payment_api", "service_id", "service_type", "unique_key_field"])
				api_details = frappe.get_doc("API Detail", api_name)
				url = api_details.api_link
			
				api_param = {}
				os = str(d.outstanding_amount)
				if os.count("."):
					os_nu = os.split(".",1)[0]
					os_ch = os.split(".",1)[1]
					os_ch = os_ch if len(os_ch) > 1 else str(os_ch)+"0"
					actual_os = str(os_nu)+"."+str(os_ch)
				else:
					actual_os = str(os)
				for a in api_details.item:
					if a.pre_defined_value:
						api_param[a.param] = str(a.defined_value)
					elif a.param == "serviceid":
						api_param[a.param] = str(service_id)
					elif a.param == "servicetype":
						api_param[a.param] = str(service_type)
					elif a.param == "FrmAcctNum":
						api_param[a.param] = str(self.bank_account)
					elif a.param == "Amt":
						api_param[a.param] = str(actual_os)
					elif a.param == "pi":
						api_param[a.param] = d.pi_number
				if consumer_field == "landlnenumber":
					consumer_field = "landlinenumber"
	
				api_param[consumer_field] = str(d.consumer_code)
				payload = json.dumps(api_param)

		      
				d.request = str(payload)
				headers = {
		
				'accept': 'application/json',
				'Content-Type': 'application/json'
				}               
				response = requests.request("POST", url, headers=headers, json=api_param)
				
				details = response.json()
				d.response = str(details)
				res_status = details['statusCode']
				d.payment_status_code = res_status
				if res_status == "00":
					d.payment_response_msg = details['ResultMessage']
					d.payment_journal_no = details['jrnlno']
					d.payment_status = "Success"
				else:
					d.payment_response_msg = details['ErrorMessage']
					d.payment_status = "Failed"

	# @frappe.whitelist()
	# def get_utility_services(self):
	
	# 	data = []
	# 	data = frappe.db.sql("""
	# 				  SELECT 
	# 					i.utility_service_type, i.customer_identification, 
	# 					i.consumer_code, i.party,
	# 					i.service_id, i.service_type
	# 				  FROM `tabUtility Services` u 
	# 				  INNER JOIN `tabUtility Services Item` i
	# 				  ON u.name = i.parent
	# 				  WHERE i.disabled = 0
	# 					and u.name = '{}'
	# 				   """.format(self.utility_services), as_dict=True)
	# 	self.set('item', [])
	# 	# frappe.throw(str(data))
	# 	for d in data:
	# 		row = self.append('item', {})
	# 		api_name, service_id, service_type, consumer_field, expense_account = frappe.db.get_value("Utility Service Type", d.utility_service_type, ["fetch_outstanding_api", "service_id", "service_type", "unique_key_field","expense_account"])
	# 		api_details = frappe.get_doc("API Detail", api_name)
	# 		url = api_details.api_link
	# 		# frappe.throw(str(url))
	# 		api_param = {}
	# 		for a in api_details.item:
	# 			if a.pre_defined_value:
	# 				api_param[a.param] = a.defined_value
	# 			elif a.param == "SERVICEID":
	# 				api_param[a.param] = service_id
	# 			elif a.param == "SERVICETYPE":
	# 				api_param[a.param] = service_type
	# 		if str(consumer_field) != "RRCOTaxCode":
	# 			api_param[consumer_field.upper()] = d.consumer_code
	# 		else:
	# 			api_param[consumer_field] = d.consumer_code
			
	# 		payload = json.dumps(api_param)
	# 		headers = {
	# 		'Content-Type': 'application/json'
	# 		}

	# 		response = requests.request("POST", url, headers=headers, data=payload)
	# 		details = response.json()
	# 		res_status = details['statusCode']
	# 		row.payment_status = "Pending"
	# 		if res_status == "00":
	# 			row.invoice_amount = details['ResultMessage']
	# 			row.outstanding_amount = details['ResultMessage']
	# 			row.response_msg = "Success"
	# 			row.net_amount = details['ResultMessage']
	# 		elif res_status == "01":
	# 			row.response_msg = details['ErrorMessage']
	# 		row.debit_account = expense_account
	# 		row.outstanding_datetime = now_datetime()
	# 		row.fetch_status_code = res_status
	# 		row.create_direct_payment = 1
	# 		row.update(d)
	
	@frappe.whitelist()
	def get_utility_outstandings(self):
		for d in self.item:
			# frappe.msgprint("d:{}".format(str(d)))
			if not d.utility_service_type:
				frappe.throw("Utility Service Type is mandatory")
			api_name, service_id, service_type, consumer_field, expense_account = frappe.db.get_value("Utility Service Type", d.utility_service_type, ["fetch_outstanding_api", "service_id", "service_type", "unique_key_field","expense_account"])
			api_details = frappe.get_doc("API Detail", api_name)
			url = api_details.api_link
			api_param = {}
			for a in api_details.item:
				if a.pre_defined_value:
					api_param[a.param] = a.defined_value
				elif a.param == "SERVICEID":
					api_param[a.param] = service_id
				elif a.param == "SERVICETYPE":
					api_param[a.param] = service_type
			if str(consumer_field) != "RRCOTaxCode":
				api_param[consumer_field.upper()] = d.consumer_code
			else:
				api_param[consumer_field] = d.consumer_code
				
			payload = json.dumps(api_param)
			headers = {
				'Content-Type': 'application/json'
			}

			response = requests.request("POST", url, headers=headers, data=payload)
			#frappe.throw(str(payload),str(response))
			details = response.json()
			res_status = details['statusCode']
			d.payment_status = "In Progress"
			if res_status == "00":
				d.invoice_amount = details['ResultMessage']
				d.outstanding_amount = details['ResultMessage']
				d.response_msg = "Success"
				d.net_amount = details['ResultMessage']
			elif res_status == "01":
				d.response_msg = details['ErrorMessage']
				d.invoice_amount = 0
				d.outstanding_amount = 0
				d.net_amount = 0
			d.debit_account = expense_account
			d.outstanding_datetime = now_datetime()
			d.fetch_status_code = res_status

	
	@frappe.whitelist()
	def make_journal_entry(self):
		if self.journal_entry:
			frappe.throw("Journal Entry No. <b> {} </b>already created for this Utility Bill".format(self.journal_entry))

		doc = frappe.new_doc("Journal Entry")
		doc.branch = self.branch
		doc.posting_date = self.posting_date
		doc.voucher_type = "Disbursement Voucher"
		doc.naming_series = "Disbursement Voucher"
		doc.company = self.company
		doc.utility_bill = str(self.name)
		doc.remarks = "Utility Bill Payment " + str(self.name)
		doc.status = "Completed"
		doc.cheque_no = self.name
		doc.cheque_date = self.posting_date
		doc.payment_status = "Payment Successful"
		if self.item:
			count_child = 0
			for a in self.item:
				if a.invoice_amount > 0 and a.payment_status == "Success":
					doc.append("accounts", {
								"account": a.debit_account,
								"debit_in_account_currency": a.net_amount,
								"reference_type": "",
								"reference_no": self.name,
								"cost_center": self.cost_center,
								"party_type": "Supplier",
								"party": a.party
						},)
					doc.append("accounts", {
						"account": self.expense_account,
						"credit_in_account_currency": a.net_amount,
						"cost_center": self.cost_center,
						"reference_type": ""
					})
					count_child +=1
			if count_child > 0:
				doc.save()
			if doc.name:
				self.db_set("journal_entry", doc.name)
			return doc.name
				
	def remove_bill_without_os(self):
		to_remove = []
		for d in self.get("item"):
			if not d.outstanding_amount:
				to_remove.append(d)
				
		[self.remove(d) for d in to_remove]

# ================= MODULE LEVEL — must be at column 0 =================

@frappe.whitelist()
def get_utility_services(docname, doctype, utility_services, item_rows=None):
    """
    Enqueue the utility services fetching as a background job.
    Returns the total number of rows to be fetched so the client can show progress.
    """
    if not utility_services:
        frappe.throw(_("Utility Services is required"))

    # total count -> returned to the client to initialise the progress bar
    total = frappe.db.count(
        "Utility Services Item",
        {"parent": utility_services, "disabled": 0},
    )
    if not total:
        frappe.throw(_("No active items found in Utility Services {0}").format(utility_services))

    frappe.enqueue(
        method="erpnext.epayment.doctype.utility_bill.utility_bill.process_utility_services",
        queue="long",
        timeout=3600,
        docname=docname,
        doctype=doctype,
        utility_services=utility_services,
        user=frappe.session.user,
        now=frappe.flags.in_test,
    )
    return {"total": total, "docname": docname, "doctype": doctype}


def process_utility_services(docname, doctype, utility_services, user=None):
    """
    Background job to fetch utility services.
    Publishes a progress event after every row.
    """
    user = user or frappe.session.user

    data = frappe.db.sql(
        """
        SELECT 
            i.utility_service_type, i.customer_identification, 
            i.consumer_code, i.party,
            i.service_id, i.service_type
        FROM `tabUtility Services` u 
        INNER JOIN `tabUtility Services Item` i
            ON u.name = i.parent
        WHERE i.disabled = 0
            AND u.name = %s
        """,
        (utility_services,),
        as_dict=True,
    )

    total = len(data)
    if not total:
        frappe.log_error(
            title="Utility Services Fetch",
            message=f"No active items found in Utility Services {utility_services}",
        )
        _publish_progress(docname, doctype, 0, 0, None, user)
        return

    # initial progress event
    _publish_progress(docname, doctype, 0, total, None, user)

    rows = []
    errors = []
    done = 0

    for d in data:
        try:
            api_name, service_id, service_type, consumer_field, expense_account = frappe.db.get_value(
                "Utility Service Type",
                d.utility_service_type,
                ["fetch_outstanding_api", "service_id", "service_type", "unique_key_field", "expense_account"],
            )

            if not api_name:
                errors.append(f"{d.utility_service_type}: no fetch_outstanding_api configured")
                done += 1
                _publish_progress(docname, doctype, done, total, d.service_id, user)
                continue

            api_details = frappe.get_doc("API Detail", api_name)
            url = api_details.api_link

            api_param = {}
            for a in api_details.item:
                if a.pre_defined_value:
                    api_param[a.param] = a.defined_value
                elif a.param == "SERVICEID":
                    api_param[a.param] = service_id
                elif a.param == "SERVICETYPE":
                    api_param[a.param] = service_type

            if str(consumer_field) != "RRCOTaxCode":
                api_param[consumer_field.upper()] = d.consumer_code
            else:
                api_param[consumer_field] = d.consumer_code

            headers = {"Content-Type": "application/json"}
            response = requests.request("POST", url, headers=headers, json=api_param, timeout=30)
            details = response.json()

            res_status = details.get("statusCode")
            row = {
                "doctype": "Utility Bill Item",
                "utility_service_type": d.utility_service_type,
                "customer_identification": d.customer_identification,
                "consumer_code": d.consumer_code,
                "party": d.party,
                "service_id": d.service_id,
                "service_type": d.service_type,
                "payment_status": "Pending",
                "debit_account": expense_account,
                "outstanding_datetime": now_datetime(),
                "fetch_status_code": res_status,
                "create_direct_payment": 1,
                "response_msg": "Success" if res_status == "00" else details.get("ErrorMessage", ""),
            }

            if res_status == "00":
                row["invoice_amount"] = details["ResultMessage"]
                row["outstanding_amount"] = details["ResultMessage"]
                row["net_amount"] = details["ResultMessage"]
            elif res_status == "01":
                row["response_msg"] = details.get("ErrorMessage", "")

            rows.append(row)

        except Exception as e:
            frappe.log_error(title="Utility Service API Error", message=f"{d.service_id}: {str(e)}")
            errors.append(f"{d.service_id}: {str(e)}")

        done += 1
        _publish_progress(docname, doctype, done, total, d.service_id, user)

    # persist rows
    if frappe.db.exists(doctype, docname):
        doc = frappe.get_doc(doctype, docname)
        doc.set("item", [])
        for r in rows:
            doc.append("item", r)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.publish_realtime(
            event="utility_services_completed",
            message={"docname": docname, "doctype": doctype, "errors": errors},
            user=user,
        )
    else:
        frappe.publish_realtime(
            event="utility_services_result",
            message={"docname": docname, "doctype": doctype, "rows": rows, "errors": errors},
            user=user,
        )


def _publish_progress(docname, doctype, done, total, current, user):
    frappe.publish_realtime(
        event="utility_services_progress",
        message={
            "docname": docname,
            "doctype": doctype,
            "done": done,
            "total": total,
            "current": current,
            "percent": int((done / total) * 100) if total else 0,
        },
        user=user,
    )