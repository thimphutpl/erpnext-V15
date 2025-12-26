# # Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

# Supported doctypes + fields
SUPPORTED = {
	"Journal Entry": {
		"header": {
			"posting_date",
			"cheque_date",
			"mode_of_payment",
			"clearance_date",
			"cheque_no",
			
		},
		"child": {
			# table_fieldname : allowed_fields
			"accounts": {"account", "cost_center", "party_type", "party", "cost_center", "reference_due_date", "bill_no", "bill_date"},
		},
	},
	"Purchase Invoice": {
		# keep strict; add more only when you really need
		"header": {
			"posting_date",
			"bill_no",
			"bill_date",
			"remarks",
			"due_date",
		},
		"child": {
			"taxes": {
				"account_head",				
				"cost_center",
				"party_type",
				"party",
			},
			"items": {
				"expense_account",
				"cost_center",
				"project",
				"qty",
				"rate",
				"amount",
			},
		},
	},

	"Payment Entry": {
		"header": {			
			"paid_from",
			"paid_to",			
		},
		"child": {			
			# Payment Entry Deduction
			"deductions": {
				"account",
				"cost_center",
				"amount",
				"description",
			},
		},
	},

}


class VoucherCorrection(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.accounting_tools.doctype.voucher_corection_detail.voucher_corection_detail import VoucherCorectionDetail
		from frappe.types import DF

		amended_from: DF.Link | None
		applied: DF.Check
		applied_by: DF.Link | None
		applied_on: DF.Datetime | None
		changes: DF.Table[VoucherCorectionDetail]
		posting_date: DF.Date | None
		reason: DF.SmallText
		voucher_doctype: DF.Link
		voucher_name: DF.DynamicLink
	# end: auto-generated types
	def validate(self):
		if not self.voucher_doctype or not self.voucher_name:
			frappe.throw("Voucher Doctype and Voucher Name are required.")
		if not self.reason:
			frappe.throw("Reason is required.")

		if self.voucher_doctype not in SUPPORTED:
			frappe.throw(f"{self.voucher_doctype} is not supported in Voucher Correction yet.")

		# Source checks
		source = frappe.get_doc(self.voucher_doctype, self.voucher_name)
		if source.docstatus not in (0, 1):
			frappe.throw("Only Draft or Submitted vouchers can be corrected.")

		if not self.get("changes"):
			frappe.throw("Please add at least one row in Changes.")

		# Optional: enable later
		# self._check_duplicate_corrections()

	def on_submit(self):
		# submit-safe idempotency
		if self.applied:
			return
		self.apply_correction(from_submit=True)

	def _ensure_not_applied(self):
		if self.applied:
			frappe.throw("This correction is already applied.")

	# Optional duplicate check (disabled in your version)
	def _check_duplicate_corrections(self):
		return

	@frappe.whitelist()
	def apply_correction(self, from_submit: bool = False):
		# idempotent / submit-safe
		if self.applied:
			if from_submit:
				return
			self._ensure_not_applied()

		if self.docstatus != 1:
			frappe.throw("Please submit this Voucher Correction before applying.")

		if self.voucher_doctype not in SUPPORTED:
			frappe.throw(f"{self.voucher_doctype} is not supported in Voucher Correction yet.")

		doc = frappe.get_doc(self.voucher_doctype, self.voucher_name)
		if doc.docstatus not in (0, 1):
			frappe.throw("Only Draft or Submitted vouchers can be corrected.")

		conf = SUPPORTED[self.voucher_doctype]
		updated_any = False

		for ch in (self.get("changes") or []):
			scope = (ch.scope or "").strip()

			# HEADER
			if scope == "Header":
				fieldname = (ch.field_name or "").strip()
				if not fieldname:
					frappe.throw("Field Name is required for Header changes.")
				if fieldname not in conf["header"]:
					frappe.throw(f"Header field not allowed for {doc.doctype}: {fieldname}")

				# store old_value only once
				if not (ch.old_value or "").strip():
					old_val = getattr(doc, fieldname, None)
					frappe.db.set_value(ch.doctype, ch.name, "old_value", str(old_val or ""))

				# apply header value
				if doc.docstatus == 0:
					setattr(doc, fieldname, ch.new_value)
				else:
					# submitted doc: DB update
					frappe.db.set_value(doc.doctype, doc.name, fieldname, ch.new_value)

					# verify
					new_val = frappe.db.get_value(doc.doctype, doc.name, fieldname)
					if str(new_val or "") != str(ch.new_value or ""):
						frappe.throw(f"Failed to update header field {fieldname}. Not marking applied.")

				updated_any = True
				continue

			# CHILD
			if scope == "Child":
				table = (ch.child_table or "").strip()
				fieldname = (ch.field_name or "").strip()
				if not table:
					frappe.throw("Child Table is required for Child changes.")
				if not fieldname:
					frappe.throw("Field Name is required for Child changes.")
				if not ch.child_row_idx:
					frappe.throw("Child Row IDX is required for Child changes.")

				if table not in conf["child"]:
					frappe.throw(f"Child table not allowed for {doc.doctype}: {table}")
				if fieldname not in conf["child"][table]:
					frappe.throw(f"Child field not allowed: {table}.{fieldname}")

				if ch.new_value in (None, ""):
					frappe.throw("New Value is required.")

				row_idx = int(ch.child_row_idx)

				rows = doc.get(table) or []
				row = next((r for r in rows if int(r.idx) == row_idx), None)
				if not row:
					frappe.throw(f"No row found in {table} for idx {row_idx}")

				# store old_value only once
				if not (ch.old_value or "").strip():
					old_val = getattr(row, fieldname, None)
					frappe.db.set_value(ch.doctype, ch.name, "old_value", str(old_val or ""))

				if doc.docstatus == 0:
					# draft: normal set
					setattr(row, fieldname, ch.new_value)
				else:
					# submitted: DB update using the child doctype dynamically
					child_field = frappe.get_meta(doc.doctype).get_field(table)
					if not child_field or not child_field.options:
						frappe.throw(f"Invalid child table field: {table} for {doc.doctype}")
					child_dt = child_field.options

					frappe.db.set_value(child_dt, row.name, fieldname, ch.new_value)

					# verify
					new_val = frappe.db.get_value(child_dt, row.name, fieldname)
					if str(new_val or "") != str(ch.new_value or ""):
						frappe.throw(f"DB update failed for {table} idx {row_idx}. Not marking applied.")

				updated_any = True
				continue

			# ignore unknown scope
		if not updated_any:
			frappe.throw("No valid change rows found. Nothing was applied.")

		# Persist + Repost logic
		if doc.docstatus == 0:
			# Draft doc: normal save recalculates where applicable
			doc.save(ignore_permissions=True)

		else:
			# Submitted doc: commit DB updates first
			frappe.db.commit()
			doc.reload()
			# Allow controlled updates to submitted docs in this flow
			frappe.flags.ignore_validate_update_after_submit = True

			# Purchase Invoice needs totals recalculated after DB-set changes
			if doc.doctype == "Purchase Invoice":
				if hasattr(doc, "calculate_taxes_and_totals"):
					doc.calculate_taxes_and_totals()
				if hasattr(doc, "set_status"):
					doc.set_status(update=True)
				doc.save(ignore_permissions=True)

			# Payment Entry needs recalculation after DB-set changes
			elif doc.doctype == "Payment Entry":
				# These exist in most ERPNext v15 builds; harmless if missing				
				if hasattr(doc, "set_amounts"):
					doc.set_amounts()
				if hasattr(doc, "set_status"):
					doc.set_status()
				doc.save(ignore_permissions=True)

			# Rebuild GL (safe, no duplicates)
			self._rebuild_gl_for_voucher(doc)

		# mark applied
		self.db_set("applied", 1)
		self.db_set("applied_by", frappe.session.user)
		self.db_set("applied_on", now_datetime())

		return {"status": "ok", "voucher": doc.name, "doctype": doc.doctype, "docstatus": doc.docstatus}

	def _rebuild_gl_for_voucher(self, doc):
		"""
		Rebuild GL for any voucher type safely (JE, PI, PE, etc.)
		"""
		# allow updating submitted docs in this controlled flow
		frappe.flags.ignore_validate_update_after_submit = True

		# 1) Delete existing GL
		frappe.db.sql(
			"""
			DELETE FROM `tabGL Entry`
			WHERE voucher_type=%s AND voucher_no=%s
			""",
			(doc.doctype, doc.name),
		)
		# 1b) Delete Payment Ledger (prevents duplicates)
		frappe.db.sql(
			"""
			DELETE FROM `tabPayment Ledger Entry`
			WHERE voucher_type=%s AND voucher_no=%s
			""", (doc.doctype, doc.name)
		)
		frappe.db.commit()

		# 2) Repost correctly based on doctype
		try:
			from erpnext.accounts.utils import repost_accounting_entries
		except Exception:
			repost_accounting_entries = None

		if repost_accounting_entries:
			repost_accounting_entries([(doc.doctype, doc.name)])
			return
		# Fallback (rare)
		if hasattr(doc, "make_gl_entries"):
			doc.make_gl_entries()
			return
		frappe.throw(f"{doc.doctype} cannot repost GL entries.")


@frappe.whitelist()
def get_old_value(
	voucher_doctype: str,
	voucher_name: str,
	scope: str,
	fieldname: str,
	child_table: str | None = None,
	row_idx: int | None = None,
):
	if voucher_doctype not in SUPPORTED:
		frappe.throw(f"{voucher_doctype} is not supported in Voucher Correction yet.")

	doc = frappe.get_doc(voucher_doctype, voucher_name)
	if doc.docstatus not in (0, 1):
		frappe.throw("Only Draft or Submitted vouchers are allowed.")

	conf = SUPPORTED[voucher_doctype]

	if scope == "Header":
		if fieldname not in conf["header"]:
			frappe.throw(f"Header field not allowed for {voucher_doctype}: {fieldname}")
		return str(getattr(doc, fieldname, "") or "")

	if scope == "Child":
		if not child_table or not row_idx:
			frappe.throw("Child Table and Row No. are required.")

		if child_table not in conf["child"]:
			frappe.throw(f"Child table not allowed for {voucher_doctype}: {child_table}")
		if fieldname not in conf["child"][child_table]:
			frappe.throw(f"Child field not allowed: {child_table}.{fieldname}")

		rows = doc.get(child_table) or []
		row = next((r for r in rows if int(r.idx) == int(row_idx)), None)
		if not row:
			frappe.throw("No row found for the given Row No.")
		return str(getattr(row, fieldname, "") or "")
	frappe.throw("Invalid scope. Use Header or Child.")
