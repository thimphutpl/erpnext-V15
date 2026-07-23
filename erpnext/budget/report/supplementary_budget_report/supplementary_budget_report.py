# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import re

import frappe
from frappe import _
from frappe.utils import flt, formatdate, getdate


_META_CACHE = {}
_OPTIONAL_VALUE_CACHE = {}


def execute(filters=None):
	filters = frappe._dict(filters or {})

	validate_filters(filters)

	data = get_data(filters)
	columns = get_columns(filters)

	return columns, data


def validate_filters(filters):
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	if not filters.get("fiscal_year"):
		frappe.throw(_("Fiscal Year is required"))

	if not filters.get("budget_against"):
		frappe.throw(_("Budget Against is required"))

	if filters.budget_against not in ("Cost Center", "Project"):
		frappe.throw(
			_("Budget Against must be either Cost Center or Project")
		)

	fiscal_year = frappe.db.get_value(
		"Fiscal Year",
		filters.fiscal_year,
		["year_start_date", "year_end_date"],
		as_dict=True
	)

	if not fiscal_year:
		frappe.throw(
			_("Fiscal Year {0} does not exist").format(
				filters.fiscal_year
			)
		)

	filters.year_start_date = getdate(
		fiscal_year.year_start_date
	)

	filters.year_end_date = getdate(
		fiscal_year.year_end_date
	)

	filters.from_date = getdate(
		filters.get("from_date")
		or filters.year_start_date
	)

	filters.to_date = getdate(
		filters.get("to_date")
		or filters.year_end_date
	)

	if filters.from_date > filters.to_date:
		frappe.throw(
			_("From Date cannot be greater than To Date")
		)

	if not (
		filters.year_start_date
		<= filters.from_date
		<= filters.year_end_date
	):
		frappe.msgprint(
			_(
				"From Date should be within the Fiscal Year. "
				"Using Fiscal Year start date: {0}"
			).format(
				formatdate(filters.year_start_date)
			)
		)

		filters.from_date = filters.year_start_date

	if not (
		filters.year_start_date
		<= filters.to_date
		<= filters.year_end_date
	):
		frappe.msgprint(
			_(
				"To Date should be within the Fiscal Year. "
				"Using Fiscal Year end date: {0}"
			).format(
				formatdate(filters.year_end_date)
			)
		)

		filters.to_date = filters.year_end_date


def get_data(filters):
	conditions = [
		"sb.company = %(company)s",
		"sb.fiscal_year = %(fiscal_year)s",
		"sb.posting_date BETWEEN %(from_date)s AND %(to_date)s",
		"sb.budget_against = %(budget_against)s",
		"sb.workflow_state = %(workflow_state)s",
		"sb.docstatus < 2"
	]

	values = {
		"company": filters.company,
		"fiscal_year": filters.fiscal_year,
		"from_date": filters.from_date,
		"to_date": filters.to_date,
		"budget_against": filters.budget_against,
		"workflow_state": "Approved"
	}

	if filters.budget_against == "Project":
		conditions.append(
			"IFNULL(sb.project, '') != ''"
		)

		if filters.get("to_project"):
			conditions.append(
				"sb.project = %(to_project)s"
			)

			values["to_project"] = filters.to_project

	else:
		conditions.append(
			"IFNULL(sb.cost_center, '') != ''"
		)

		if filters.get("to_cc"):
			conditions.append(
				"sb.cost_center = %(to_cc)s"
			)

			values["to_cc"] = filters.to_cc

	if filters.get("to_acc"):
		conditions.append(
			"sbi.account = %(to_acc)s"
		)

		values["to_acc"] = filters.to_acc

	query = """
		SELECT
			/* Hidden values used by print format */
			sb.name AS transaction,
			sb.company AS company,
			sb.fiscal_year AS fiscal_year,
			sb.supplementary_type AS supplementary_type,
			sb.workflow_state AS workflow_state,

			/* Fields shown in report */
			sb.posting_date AS date,
			sb.cost_center AS to_cc,
			sb.project AS to_project,
			sb.remarks AS remarks,

			sbi.name AS item_row,
			sbi.broad_head AS broad_head,
			sbi.account AS to_acc,
			sbi.account_number AS account_number,
			sbi.approved_budget AS approved_budget,
			sbi.amount AS amount,
			sbi.month AS month,
			sbi.budget_activity AS budget_activity,
			sbi.budget_sub_activity AS budget_sub_activity,

			/* Keep Link ID for internal lookups */
			sbi.source_of_fund AS source_of_fund_id,

			/* Show Source of Fund descriptive name */
			sof.source_of_fund AS source_of_fund,

			/* Financial Code */
			sof.fic AS fic,

			/* FIC is available in Source of Fund */
			sof.fic AS financing_code

		FROM `tabSupplementary Budget` sb

		INNER JOIN `tabSupplementary Budget Item` sbi
			ON sbi.parent = sb.name
			AND sbi.parenttype = 'Supplementary Budget'

		LEFT JOIN `tabSource of Fund` sof
			ON sof.name = sbi.source_of_fund

		WHERE {conditions}

		ORDER BY
			sb.posting_date ASC,
			sb.name ASC,
			sbi.idx ASC
	""".format(
		conditions=" AND ".join(conditions)
	)

	data = frappe.db.sql(
		query,
		values,
		as_dict=True
	)

	add_print_format_fields(data)

	return data


def add_print_format_fields(data):
	"""
	Add helper values needed by Budget Form VIII.

	The exact custom fieldnames for AUC, PUC and SPC may differ
	in your site. Candidate fieldnames are checked safely.
	"""

	for row in data:
		# AUC
		row.auc = first_value(
			get_optional_value(
				"Supplementary Budget",
				row.transaction,
				[
					"auc",
					"auc_code",
					"agency_unit_code"
				]
			),
			get_optional_value(
				"Cost Center",
				row.to_cc,
				[
					"auc",
					"auc_code",
					"agency_unit_code"
				]
			)
		)

		# PUC
		row.puc = first_value(
			get_optional_value(
				"Supplementary Budget",
				row.transaction,
				[
					"puc",
					"puc_code",
					"programme_unit_code",
					"program_unit_code"
				]
			),
			get_optional_value(
				"Cost Center",
				row.to_cc,
				[
					"puc",
					"puc_code",
					"programme_unit_code",
					"program_unit_code"
				]
			)
		)

		# SPC
		row.spc = first_value(
			get_optional_value(
				"Supplementary Budget",
				row.transaction,
				[
					"spc",
					"spc_code",
					"sub_program_code",
					"sub_programme_code"
				]
			),
			get_optional_value(
				"Cost Center",
				row.to_cc,
				[
					"spc",
					"spc_code",
					"sub_program_code",
					"sub_programme_code"
				]
			)
		)

		# Budget Activity code
		row.activity_code = first_value(
			get_optional_value(
				"Budget Activity",
				row.budget_activity,
				[
					"activity_code",
					"budget_activity_code",
					"code"
				]
			),
			extract_activity_code(
				row.budget_activity
			)
		)

		# Budget Sub Activity code
		row.sub_activity_code = first_value(
			get_optional_value(
				"Budget Sub Activity",
				row.budget_sub_activity,
				[
					"sub_activity_code",
					"budget_sub_activity_code",
					"code"
				]
			),
			extract_activity_code(
				row.budget_sub_activity
			)
		)

		# AC/SAC column should normally use the sub-activity code
		row.ac_sac = (
			row.sub_activity_code
			or row.activity_code
			or ""
		)

		# Financing source acronym
		row.financing_source_acronym = first_value(
			get_optional_value(
				"Source of Fund",
				row.source_of_fund_id,
				[
					"acronym",
					"source_acronym",
					"financing_source_acronym"
				]
			),
			make_source_acronym(
				row.source_of_fund
			)
		)

		# Financing type
		row.fin_type = first_value(
			get_optional_value(
				"Supplementary Budget Item",
				row.item_row,
				[
					"fin_type",
					"finance_type",
					"financing_type",
					"type_of_financing"
				]
			),
			get_optional_value(
				"Source of Fund",
				row.source_of_fund_id,
				[
					"fin_type",
					"finance_type",
					"financing_type",
					"type_of_financing"
				]
			),
			"IN-CASH"
		)

		# Clean title without leading codes
		row.name_of_activity = strip_code_prefix(
			row.budget_sub_activity
			or row.budget_activity
		)

		# Approved Budget
		row.approved_budget = flt(
			row.approved_budget or 0,
			2
		)

		# Check whether separate RGOB and Donor fields exist
		from_rgob = get_optional_value(
			"Supplementary Budget Item",
			row.item_row,
			[
				"from_rgob",
				"rgob_amount",
				"government_amount"
			]
		)

		from_donor = get_optional_value(
			"Supplementary Budget Item",
			row.item_row,
			[
				"from_donor",
				"donor_amount"
			]
		)

		# If separate fields do not exist, place the child amount
		# under RGOB or Donor according to Source of Fund.
		if (
			from_rgob in (None, "")
			and from_donor in (None, "")
		):
			if is_rgob_source(row.source_of_fund):
				from_rgob = row.amount
				from_donor = None
			else:
				from_rgob = None
				from_donor = row.amount

		row.from_rgob = (
			flt(from_rgob)
			if from_rgob not in (None, "")
			else None
		)

		row.from_donor = (
			flt(from_donor)
			if from_donor not in (None, "")
			else None
		)


def get_optional_value(doctype, document_name, candidate_fields):
	"""
	Safely get the first available value from a list of possible
	custom fieldnames without causing an SQL unknown-column error.
	"""

	if not document_name:
		return None

	meta = get_cached_meta(doctype)

	valid_fields = [
		fieldname
		for fieldname in candidate_fields
		if meta.has_field(fieldname)
	]

	if not valid_fields:
		return None

	cache_key = (
		doctype,
		document_name,
		tuple(valid_fields)
	)

	if cache_key in _OPTIONAL_VALUE_CACHE:
		return _OPTIONAL_VALUE_CACHE[cache_key]

	values = frappe.db.get_value(
		doctype,
		document_name,
		valid_fields,
		as_dict=True
	)

	result = None

	if values:
		for fieldname in valid_fields:
			value = values.get(fieldname)

			if value not in (None, ""):
				result = value
				break

	_OPTIONAL_VALUE_CACHE[cache_key] = result

	return result


def get_cached_meta(doctype):
	if doctype not in _META_CACHE:
		_META_CACHE[doctype] = frappe.get_meta(doctype)

	return _META_CACHE[doctype]


def first_value(*values):
	for value in values:
		if value not in (None, ""):
			return value

	return ""


def extract_activity_code(value):
	"""
	Examples:

	001 - 001.00 - GENERAL ADMINISTRATION
	Returns: 001.00

	001 - 01 - PAY AND ALLOWANCES
	Returns: 001.01
	"""

	if not value:
		return ""

	parts = [
		part.strip()
		for part in str(value).split(" - ")
	]

	code_parts = []

	for part in parts[:3]:
		if re.fullmatch(
			r"[A-Za-z0-9./]+",
			part
		) and re.search(r"\d", part):
			code_parts.append(part)
		else:
			break

	if not code_parts:
		return ""

	if len(code_parts) >= 2:
		second_code = code_parts[1]

		if "." in second_code or "/" in second_code:
			return second_code

		return "{0}.{1}".format(
			code_parts[0],
			second_code.zfill(2)
		)

	return code_parts[0]


def strip_code_prefix(value):
	if not value:
		return ""

	parts = [
		part.strip()
		for part in str(value).split(" - ")
	]

	while parts:
		first_part = parts[0]

		if (
			re.fullmatch(
				r"[A-Za-z0-9./]+",
				first_part
			)
			and re.search(r"\d", first_part)
		):
			parts.pop(0)
		else:
			break

	return " - ".join(parts) or str(value)


def make_source_acronym(source_of_fund):
	if not source_of_fund:
		return ""

	words = str(source_of_fund).strip().split()

	ignored_words = {
		"grant",
		"fund",
		"funds",
		"source",
		"financing"
	}

	words = [
		word
		for word in words
		if word.lower() not in ignored_words
	]

	if not words:
		return str(source_of_fund)

	return " ".join(words[:2])


def is_rgob_source(source_of_fund):
	source = str(
		source_of_fund or ""
	).upper()

	rgob_words = [
		"RGOB",
		"RGoB",
		"GOVERNMENT",
		"GOVT"
	]

	return any(
		word.upper() in source
		for word in rgob_words
	)


def get_columns(filters):
	columns = [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 110
		}
	]

	if filters.budget_against == "Project":
		columns.append(
			{
				"fieldname": "to_project",
				"label": _("To Project"),
				"fieldtype": "Link",
				"options": "Project",
				"width": 220
			}
		)

	else:
		columns.append(
			{
				"fieldname": "to_cc",
				"label": _("To Cost Center"),
				"fieldtype": "Link",
				"options": "Cost Center",
				"width": 200
			}
		)

	columns.extend([
		{
			"fieldname": "broad_head",
			"label": _("Broad Head"),
			"fieldtype": "Data",
			"width": 190
		},
		{
			"fieldname": "to_acc",
			"label": _("To Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 250
		},
		{
			"fieldname": "fic",
			"label": _("Financial Code"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "source_of_fund",
			"label": _("Source of Fund"),
			"fieldtype": "Data",
			"width": 180
		},
		{
			"fieldname": "budget_activity",
			"label": _("Budget Activity"),
			"fieldtype": "Link",
			"options": "Budget Activity",
			"width": 280
		},
		{
			"fieldname": "budget_sub_activity",
			"label": _("Budget Sub Activity"),
			"fieldtype": "Link",
			"options": "Budget Sub Activity",
			"width": 260
		},
		{
			"fieldname": "approved_budget",
			"label": _("Approved Budget"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "amount",
			"label": _("Amount"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 200
		}
	])

	return columns