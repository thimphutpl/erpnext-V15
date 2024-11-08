# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from dateutil.relativedelta import relativedelta
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_years, cstr, getdate


class FiscalYear(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from erpnext.accounts.doctype.fiscal_year_company.fiscal_year_company import FiscalYearCompany

		auto_created: DF.Check
		companies: DF.Table[FiscalYearCompany]
		disabled: DF.Check
		is_calendar_year: DF.Check
		is_short_year: DF.Check
		year: DF.Data
		year_end_date: DF.Date
		year_start_date: DF.Date
	# end: auto-generated types

	def validate(self):
		self.validate_is_company_calendar_year()
		self.validate_fiscal_year_name()
		self.validate_dates()
		self.validate_overlap()

		if not self.is_new():
			year_start_end_dates = frappe.db.sql(
				"""select year_start_date, year_end_date
				from `tabFiscal Year` where name=%s""",
				(self.name),
			)

			if year_start_end_dates:
				if (
					getdate(self.year_start_date) != year_start_end_dates[0][0]
					or getdate(self.year_end_date) != year_start_end_dates[0][1]
				):
					frappe.throw(
						_(
							"Cannot change Fiscal Year Start Date and Fiscal Year End Date once the Fiscal Year is saved."
						)
					)

	def validate_is_company_calendar_year(self):
		if self.get("companies"):
			for c in self.companies:
				calendar_year_based = frappe.db.get_value("Company", c.company, "calendar_year_based")
				if not calendar_year_based and self.is_calendar_year:
					frappe.throw("{} cannot be Calander Year.".format(frappe.get_desk_link("Company", c.company)))
				elif calendar_year_based and not self.is_calendar_year:
					frappe.throw("{} is Calander Year.".format(frappe.get_desk_link("Company", c.company)))

	def validate_fiscal_year_name(self):
		# Determine if the fiscal year should be a calendar year or cross-year
		if self.is_calendar_year:
			start_year = cstr(getdate(self.year_start_date).year)
			end_year = cstr(getdate(self.year_end_date).year)

			if self.name != start_year:
				frappe.throw(
					_("For a calendar year fiscal year, the name should be '{0}'").format(start_year)
				)
		else:
			start_year = cstr(getdate(self.year_start_date).year)
			end_year = cstr(getdate(self.year_end_date).year)

			if self.name != f"{start_year}-{end_year[-2:]}":
				frappe.throw(
					_("For a fiscal year spanning multiple years, the name should be '{0}-{1}'").format(start_year, end_year[-2:])
				)

	def validate_dates(self):
		self.validate_from_to_dates("year_start_date", "year_end_date")
		if self.is_short_year:
			# Fiscal Year can be shorter than one year, in some jurisdictions
			# under certain circumstances. For example, in the USA and Germany.
			return

		start_date = getdate(self.year_start_date)
		end_date = getdate(self.year_end_date)

		# date = getdate(self.year_start_date) + relativedelta(years=1) - relativedelta(days=1)

		# if getdate(self.year_end_date) != date:
		# 	frappe.throw(
		# 		_("Fiscal Year End Date should be one year after Fiscal Year Start Date"),
		# 		frappe.exceptions.InvalidDates,
		# 	)

		if start_date.year == end_date.year:
			expected_end_date = start_date + relativedelta(years=1) - relativedelta(days=1)
			if end_date != expected_end_date:
				frappe.throw(
					_("Fiscal Year End Date should be one year after Fiscal Year Start Date"),
					frappe.exceptions.InvalidDates,
				)
		else:
		# Non-standard fiscal year logic (e.g., 2024-25)
			expected_end_date = start_date + relativedelta(months=12) - relativedelta(days=1)
			if end_date != expected_end_date:
				frappe.throw(
					_("For non-standard fiscal years, the end date should be exactly one year minus a day after the start date."),
					frappe.exceptions.InvalidDates,
				)

	def on_update(self):
		check_duplicate_fiscal_year(self)
		frappe.cache().delete_value("fiscal_years")

	def on_trash(self):
		frappe.cache().delete_value("fiscal_years")

	def validate_overlap(self):
		existing_fiscal_years = frappe.db.sql(
			"""select name from `tabFiscal Year`
			where (
				(%(year_start_date)s between year_start_date and year_end_date)
				or (%(year_end_date)s between year_start_date and year_end_date)
				or (year_start_date between %(year_start_date)s and %(year_end_date)s)
				or (year_end_date between %(year_start_date)s and %(year_end_date)s)
			) and name!=%(name)s""",
			{
				"year_start_date": self.year_start_date,
				"year_end_date": self.year_end_date,
				"name": self.name or "No Name",
			},
			as_dict=True,
		)

		if existing_fiscal_years:
			for existing in existing_fiscal_years:
				company_for_existing = frappe.db.sql_list(
					"""select company from `tabFiscal Year Company`
					where parent=%s""",
					existing.name,
				)

				overlap = False
				if not self.get("companies") or not company_for_existing:
					overlap = True

				for d in self.get("companies"):
					if d.company in company_for_existing:
						overlap = True

				if overlap:
					frappe.throw(
						_(
							"Year start date or end date is overlapping with {0}. To avoid please set company"
						).format(existing.name),
						frappe.NameError,
					)


@frappe.whitelist()
def check_duplicate_fiscal_year(doc):
	year_start_end_dates = frappe.db.sql(
		"""select name, year_start_date, year_end_date from `tabFiscal Year` where name!=%s""",
		(doc.name),
	)
	for fiscal_year, ysd, yed in year_start_end_dates:
		if (getdate(doc.year_start_date) == ysd and getdate(doc.year_end_date) == yed) and (
			not frappe.flags.in_test
		):
			frappe.throw(
				_(
					"Fiscal Year Start Date and Fiscal Year End Date are already set in Fiscal Year {0}"
				).format(fiscal_year)
			)


@frappe.whitelist()
def auto_create_fiscal_year():
	for d in frappe.db.sql(
		"""select name from `tabFiscal Year` where year_end_date = date_add(current_date, interval 3 day)"""
	):
		try:
			current_fy = frappe.get_doc("Fiscal Year", d[0])

			new_fy = frappe.copy_doc(current_fy, ignore_no_copy=False)

			new_fy.year_start_date = add_days(current_fy.year_end_date, 1)
			new_fy.year_end_date = add_years(current_fy.year_end_date, 1)

			start_year = cstr(new_fy.year_start_date.year)
			end_year = cstr(new_fy.year_end_date.year)
			new_fy.year = start_year if start_year == end_year else (start_year + "-" + end_year)
			new_fy.auto_created = 1

			new_fy.insert(ignore_permissions=True)
		except frappe.NameError:
			pass


def get_from_and_to_date(fiscal_year):
	fields = ["year_start_date", "year_end_date"]
	cached_results = frappe.get_cached_value("Fiscal Year", fiscal_year, fields, as_dict=1)
	return dict(from_date=cached_results.year_start_date, to_date=cached_results.year_end_date)


def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	user_roles = frappe.get_roles(user)

	if user == "Administrator" or "System Manager" in user_roles:
		return

	return """(
		exists(select 1
			from `tabEmployee` as e
			where e.company = `tabFiscal Year Company`.company
			and e.user_id = '{user}')
	)""".format(user=user)

	# return """(
	# 	exists(select 1
	# 		from `tabEmployee` as e
	# 		where e.company = `tabFiscal Year Company`.company
	# 		and e.user_id = '{user}')
	# 	or
	# 	exists(select 1
	# 		from `tabEmployee` e, `tabAssign Branch` ab, `tabBranch Item` bi
	# 		where e.user_id = '{user}'
	# 		and ab.employee = e.name
	# 		and bi.parent = ab.name
	# 		and bi.branch = `tabJournal Entry`.branch)
	# )""".format(user=user)
