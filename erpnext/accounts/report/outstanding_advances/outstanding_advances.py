# import frappe
# from frappe import _


# def execute(filters=None):
#     filters = frappe._dict(filters or {})

#     validate_filters(filters)

#     columns = get_columns()
#     data = get_data(filters)

#     return columns, data


# def validate_filters(filters):
#     """
#     Validate the mandatory report filters.
#     """

#     if not filters.get("fiscal_year"):
#         frappe.throw(_("Please select a Fiscal Year."))

#     if not filters.get("company"):
#         frappe.throw(_("Please select a Company."))


# def get_columns():
#     return [
#         {
#             "fieldname": "customer",
#             "label": _("Party/Employee"),
#             "fieldtype": "Data",
#             "width": 150,
#         },
#         {
#             "fieldname": "code",
#             "label": _("Account Code"),
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "fieldname": "name",
#             "label": _("Name"),
#             "fieldtype": "Data",
#             "width": 200,
#         },
#         {
#             "fieldname": "activity_code",
#             "label": _("Activity Code"),
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "fieldname": "fi_code",
#             "label": _("FI Code"),
#             "fieldtype": "Data",
#             "width": 120,
#         },
#         {
#             "fieldname": "testing",
#             "label": _("Opening Balance"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "opening_balance",
#             "label": _("Advance Amount"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "settlement_amount",
#             "label": _("Settlement Amount"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "fieldname": "total_outstanding",
#             "label": _("Total Outstanding"),
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#     ]


# def get_data(filters):


# # def get_data(filters):
# #     """
# #     Get the Outstanding Advance data based on the selected filters.
# #     """

# #     data = []

# #     settlement_filters = get_advance_settlement_filters(filters)

# #     advance_settlements = frappe.get_all(
# #         "Advance Settlement",
# #         filters=settlement_filters,
# #         fields=[
# #             "name",
# #             "customer",
# #         ],
# #         order_by="name asc",
# #     )

# #     for settlement in advance_settlements:
# #         mobilisation_items = get_mobilisation_items(
# #             settlement.name
# #         )

# #         # Get opening items where is_opening = 1 in the linked Advance
# #         opening_items = get_opening_items(
# #             settlement.name
# #         )

# #         recoup_items = get_recoup_items(
# #             settlement.name,
# #             filters,
# #         )

# #         # Do not create a row when no recoup item matches
# #         # the selected report filters.
# #         if not recoup_items:
# #             continue

# #         total_opening_balance = sum(
# #             item.get("advance_amount") or 0
# #             for item in mobilisation_items
# #         )

# #         total_testing = sum(
# #             item.get("advance_amount") or 0
# #             for item in opening_items
# #         )

# #         total_settlement_amount = sum(
# #             item.get("allocated_amount") or 0
# #             for item in mobilisation_items
# #         )

# #         total_outstanding = (
# #             total_opening_balance
# #             - total_settlement_amount
# #         )

# #         customer_name = get_party_name(
# #             settlement.customer
# #         )

# #         for recoup_item in recoup_items:
# #             account_number = get_account_number(
# #                 recoup_item.account
# #             )

# #             activity_code = get_sub_activity_code(
# #                 recoup_item.budget_sub_activity
# #             )

# #             row = {
# #                 "customer": (
# #                     customer_name
# #                     or settlement.customer
# #                     or ""
# #                 ),
# #                 "code": (
# #                     account_number
# #                     or recoup_item.account
# #                     or ""
# #                 ),
# #                 "name": recoup_item.remark or "",
# #                 "activity_code": activity_code,
# #                 "fi_code": (
# #                     recoup_item.source_of_fund
# #                     or ""
# #                 ),
# #                 "opening_balance": total_opening_balance,
# #                 "testing": total_testing,
# #                 "settlement_amount": total_settlement_amount,
# #                 "total_outstanding": total_outstanding,
# #             }

# #             data.append(row)

# #     return data


# # def get_advance_settlement_filters(filters):
# #     """
# #     Build filters for the Advance Settlement parent doctype.
# #     """

# #     settlement_filters = {
# #         "docstatus": 1,
# #     }

# #     advance_settlement_meta = frappe.get_meta(
# #         "Advance Settlement"
# #     )

# #     # Apply Company only when the field exists
# #     # in Advance Settlement.
# #     if (
# #         filters.get("company")
# #         and advance_settlement_meta.has_field("company")
# #     ):
# #         settlement_filters["company"] = filters.company

# #     # Filter by Party/Employee.
# #     if filters.get("customer"):
# #         settlement_filters["customer"] = filters.customer

# #     apply_fiscal_year_filter(
# #         settlement_filters,
# #         filters.fiscal_year,
# #         advance_settlement_meta,
# #     )

# #     return settlement_filters


# # def apply_fiscal_year_filter(
# #     settlement_filters,
# #     fiscal_year,
# #     advance_settlement_meta,
# # ):
# #     """
# #     Apply Fiscal Year using the fiscal_year field when it exists.

# #     Otherwise, filter using a date field such as posting_date,
# #     transaction_date or date.
# #     """

# #     if not fiscal_year:
# #         return

# #     # Direct Fiscal Year field
# #     if advance_settlement_meta.has_field("fiscal_year"):
# #         settlement_filters["fiscal_year"] = fiscal_year
# #         return

# #     fiscal_year_dates = frappe.db.get_value(
# #         "Fiscal Year",
# #         fiscal_year,
# #         [
# #             "year_start_date",
# #             "year_end_date",
# #         ],
# #         as_dict=True,
# #     )

# #     if not fiscal_year_dates:
# #         frappe.throw(
# #             _("Fiscal Year {0} was not found.").format(
# #                 fiscal_year
# #             )
# #         )

# #     date_field = get_advance_settlement_date_field(
# #         advance_settlement_meta
# #     )

# #     if not date_field:
# #         frappe.throw(
# #             _(
# #                 "Advance Settlement does not have a "
# #                 "Fiscal Year or date field for filtering."
# #             )
# #         )

# #     settlement_filters[date_field] = [
# #         "between",
# #         [
# #             fiscal_year_dates.year_start_date,
# #             fiscal_year_dates.year_end_date,
# #         ],
# #     ]


# # def get_advance_settlement_date_field(
# #     advance_settlement_meta,
# # ):
# #     """
# #     Find the available transaction date field from
# #     Advance Settlement.
# #     """

# #     possible_date_fields = [
# #         "posting_date",
# #         "transaction_date",
# #         "date",
# #     ]

# #     for fieldname in possible_date_fields:
# #         if advance_settlement_meta.has_field(fieldname):
# #             return fieldname

# #     return None


# # def get_mobilisation_items(settlement_name):
# #     """
# #     Get Mobilisation Advance Item rows.
# #     """

# #     return frappe.get_all(
# #         "Mobilisation Advance Item",
# #         filters={
# #             "parent": settlement_name,
# #             "parenttype": "Advance Settlement",
# #         },
# #         fields=[
# #             "advance_amount",
# #             "allocated_amount",
# #         ],
# #         order_by="idx asc",
# #     )


# # def get_opening_items(settlement_name):
# #     """
# #     Get Mobilisation Advance Item rows where the linked Advance has is_opening = 1.
# #     Uses SQL to join with the Advance doctype.
# #     """
    
# #     # Use SQL to join Mobilisation Advance Item with Advance doctype
# #     # to filter by is_opening = 1
# #     result = frappe.db.sql("""
# #         SELECT 
# #             mai.advance_amount
# #         FROM 
# #             `tabMobilisation Advance Item` mai
# #         INNER JOIN 
# #             `tabAdvance` a ON mai.reference = a.name
# #         WHERE 
# #             mai.parent = %s
# #             AND mai.parenttype = 'Advance Settlement'
# #             AND a.is_opening = 1
# #         ORDER BY 
# #             mai.idx ASC
# #     """, (settlement_name,), as_dict=True)
    
# #     return result


# # def get_recoup_items(settlement_name, filters):
# #     """
# #     Get Advance Recoup Item rows and apply the optional filters.
# #     """

# #     recoup_filters = {
# #         "parent": settlement_name,
# #         "parenttype": "Advance Settlement",
# #     }

# #     if filters.get("account"):
# #         recoup_filters["account"] = filters.account

# #     if filters.get("budget_sub_activity"):
# #         recoup_filters["budget_sub_activity"] = (
# #             filters.budget_sub_activity
# #         )

# #     if filters.get("source_of_fund"):
# #         recoup_filters["source_of_fund"] = (
# #             filters.source_of_fund
# #         )

# #     return frappe.get_all(
# #         "Advance Recoup Item",
# #         filters=recoup_filters,
# #         fields=[
# #             "account",
# #             "remark",
# #             "budget_sub_activity",
# #             "source_of_fund",
# #         ],
# #         order_by="idx asc",
# #     )


# # def get_account_number(account):
# #     """
# #     Get Account Code from the Account doctype.
# #     """

# #     if not account:
# #         return ""

# #     account_number = frappe.db.get_value(
# #         "Account",
# #         account,
# #         "account_number",
# #     )

# #     return account_number or account


# # def get_sub_activity_code(budget_sub_activity):
# #     """
# #     Get the Sub Activity Code from Budget Sub Activity.
# #     """

# #     if not budget_sub_activity:
# #         return ""

# #     sub_activity_code = frappe.db.get_value(
# #         "Budget Sub Activity",
# #         budget_sub_activity,
# #         "sub_activity_code",
# #     )

# #     return sub_activity_code or ""


# # def get_party_name(party):
# #     """
# #     Find the Party/Employee display name.

# #     First check Employee, then Customer, then Supplier.
# #     """

# #     if not party:
# #         return ""

# #     employee_name = frappe.db.get_value(
# #         "Employee",
# #         party,
# #         "employee_name",
# #     )

# #     if employee_name:
# #         return employee_name

# #     customer_name = frappe.db.get_value(
# #         "Customer",
# #         party,
# #         "customer_name",
# #     )

# #     if customer_name:
# #         return customer_name

# #     supplier_name = frappe.db.get_value(
# #         "Supplier",
# #         party,
# #         "supplier_name",
# #     )

# #     if supplier_name:
# #         return supplier_name

# #     return party

import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def validate_filters(filters):
    if not filters.get("fiscal_year"):
        frappe.throw(_("Please select a Fiscal Year."))

    if not filters.get("company"):
        frappe.throw(_("Please select a Company."))
    


def get_columns():
    return [
        {
            "fieldname": "company",
            "label": _("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "width": 100,
        },
        {
            "fieldname": "party",
            "label": _("Party"),
            "fieldtype": "Data",
            "width": 150,
        },
         {
            "fieldname": "party_type",
            "label": _("Party Type"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "code",
            "label": _("Account Code"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "activity_code",
            "label": _("Activity Code"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "fi_code",
            "label": _("FI Code"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "advance_amount",
            "label": _("Advance Amount"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "opening_balance",
            "label": _("Opening Balance"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "settlement_amount",
            "label": _("Settlement Amount"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "total_outstanding",
            "label": _("Total Outstanding"),
            "fieldtype": "Currency",
            "width": 150,
        },
    ]
# def get_data(filters):

#     fiscal_year = filters.get("fiscal_year")
#     company = filters.get("company")

#     party_type = filters.get("party_type")
#     party = filters.get("party")
#     account = filters.get("account")
#     budget_sub_activity = filters.get("budget_sub_activity")
#     source_of_fund = filters.get("source_of_fund")

#     conditions = [
#         "ae.company = %s",
#         "ae.fiscal_year = %s",
#         "ae.is_cancelled = 0"
#     ]

#     values = [
#         company,
#         fiscal_year,
#     ]

#     if party_type:
#         conditions.append("ae.party_type = %s")
#         values.append(party_type)

#     if party:
#         if isinstance(party, str):
#             party = frappe.parse_json(party)

#         if party:
#             conditions.append("ae.customer IN %s")
#             values.append(tuple(party))

#     if account:
#         conditions.append("mei.account = %s")
#         values.append(account)

#     if budget_sub_activity:
#         conditions.append("mei.budget_activity = %s")
#         values.append(budget_sub_activity)

#     if source_of_fund:
#         conditions.append("mei.source_of_fund = %s")
#         values.append(source_of_fund)

#     data = frappe.db.sql(
#         f"""
#         SELECT
#             ae.customer AS party,
#             ae.party_type as party_type,
#             mei.account AS code,
#             mei.budget_activity AS activity_code,
#             mei.source_of_fund AS fi_code,
#             CASE
#                 WHEN COALESCE(mei.is_opening, 0) = 0
#                 THEN COALESCE(mei.advance_amount, 0)
#                 ELSE 0
#             END AS advance_amount,

#             CASE
#                 WHEN COALESCE(mei.is_opening, 0) = 1
#                 THEN COALESCE(mei.advance_amount, 0)
#                 ELSE 0
#             END AS opening_balance,
#             COALESCE(mei.allocated_amount, 0) AS settlement_amount,

#             (
#                 COALESCE(mei.advance_amount, 0)
#                 - COALESCE(mei.allocated_amount, 0)
#             ) AS total_outstanding

#         FROM `tabAdvance Entry` ae

#         INNER JOIN `tabAdvance` a
#             ON a.name = ae.advance

#         INNER JOIN `tabMobilisation Entry Item` mei
#             ON mei.parent = ae.name

#         WHERE {" AND ".join(conditions)}

#         ORDER BY ae.posting_date ASC
#         """,
#         values,
#         as_dict=True,
#     )


#     return data

def get_data(filters):

    fiscal_year = filters.get("fiscal_year")
    company = filters.get("company")

    party_type = filters.get("party_type")
    party = filters.get("party")
    account = filters.get("account")
    budget_activity = filters.get("budget_activity")
    budget_sub_activity = filters.get("budget_sub_activity")
    source_of_fund = filters.get("source_of_fund")

    conditions = [
        "ae.company = %s",
        "ae.fiscal_year = %s",
        "ae.is_cancelled = 0",
    ]

    values = [
        company,
        fiscal_year,
    ]

    if party_type:
        conditions.append("ae.party_type = %s")
        values.append(party_type)

    if party:
        if isinstance(party, str):
            party = frappe.parse_json(party)

        if party:
            conditions.append("ae.customer IN %s")
            values.append(tuple(party))

    if account:
        conditions.append("mei.account = %s")
        values.append(account)

    if budget_activity:
        conditions.append("mei.budget_activity = %s")
        values.append(budget_activity)

    if budget_sub_activity:
        conditions.append("mei.budget_sub_activity = %s")
        values.append(budget_sub_activity)

    if source_of_fund:
        conditions.append("mei.source_of_fund = %s")
        values.append(source_of_fund)

    data = frappe.db.sql(
        f"""
        SELECT
            ae.company AS company,
            ae.customer AS party,
            ae.party_type AS party_type,
            ae.advance AS reference,
            mei.account AS code,
            mei.budget_activity AS activity_code,
            mei.budget_sub_activity AS sub_activity_code,
            mei.source_of_fund AS fi_code,

            COALESCE(mei.advance_amount, 0) AS advance_amount,
            COALESCE(mei.allocated_amount, 0) AS settlement_amount,

            CASE
                WHEN mei.is_opening = 1
                THEN COALESCE(mei.advance_amount, 0)
                ELSE 0
            END AS opening_balance,

            (
                COALESCE(mei.advance_amount, 0)
                - COALESCE(mei.allocated_amount, 0)
            ) AS total_outstanding

        FROM `tabAdvance Entry` ae
        INNER JOIN `tabMobilisation Entry Item` mei
            ON mei.parent = ae.name
        WHERE {" AND ".join(conditions)}

        ORDER BY ae.posting_date ASC
        """,
        values,
        as_dict=True,
    )

    return data