
# import frappe
# from frappe import _


# def execute(filters=None):
# 	filters = frappe._dict(filters or {})

# 	validate_filters(filters)

# 	columns = get_columns()
# 	data = get_data(filters)

# 	return columns, data


# def validate_filters(filters):
# 	if not filters.get("fiscal_year"):
# 		frappe.throw(_("Please select a Fiscal Year."))

# 	if not filters.get("company"):
# 		frappe.throw(_("Please select a Company."))
	


# def get_columns():
# 	return [
# 		{
# 			"fieldname": "company",
# 			"label": _("Company"),
# 			"fieldtype": "Link",
# 			"options": "Company",
# 			"width": 100,
# 		},
# 		{
# 			"fieldname":"fiscal_year",
# 			"lable":"Fiscal Year",
# 			"fieldtype":"Data",
# 			"width": 100

# 		},
# 		{
# 			"fieldname":"posting_date",
# 			"lable":"Posting Date",
# 			"fieldtype":"Date",
# 			"width": 100

# 		},
# 		{
# 			"fieldname": "party",
# 			"label": _("Party"),
# 			"fieldtype": "Data",
# 			"width": 150,
# 		},
# 		 {
# 			"fieldname": "party_type",
# 			"label": _("Party Type"),
# 			"fieldtype": "Data",
# 			"width": 150,
# 		},
# 		{
# 			"fieldname": "code",
# 			"label": _("Account Code"),
# 			"fieldtype": "Data",
# 			"width": 120,
# 		},
# 		{
# 			"fieldname": "activity_code",
# 			"label": _("Activity Code"),
# 			"fieldtype": "Data",
# 			"width": 120,
# 		},
# 		{
# 			"fieldname": "fi_code",
# 			"label": _("FI Code"),
# 			"fieldtype": "Data",
# 			"width": 120,
# 		},
# 		{
# 			"fieldname": "opening_balance",
# 			"label": _("Opening Balance"),
# 			"fieldtype": "Currency",
# 			"width": 150,
# 		},
# 		{
# 			"fieldname": "advance_amount",
# 			"label": _("Advance Amount"),
# 			"fieldtype": "Currency",
# 			"width": 150,
# 		},
	   
# 		{
# 			"fieldname": "settlement_amount",
# 			"label": _("Settlement Amount"),
# 			"fieldtype": "Currency",
# 			"width": 150,
# 		},
# 		{
# 			"fieldname": "total_outstanding",
# 			"label": _("Total Outstanding"),
# 			"fieldtype": "Currency",
# 			"width": 150,
# 		},
# 	]

# def get_data(filters):

# 	fiscal_year = filters.get("fiscal_year")
# 	company = filters.get("company")

# 	party_type = filters.get("party_type")
# 	party = filters.get("party")
# 	account = filters.get("account")
# 	budget_activity = filters.get("budget_activity")
# 	budget_sub_activity = filters.get("budget_sub_activity")
# 	source_of_fund = filters.get("source_of_fund")

# 	conditions = [
# 		"ae.company = %s",
# 		"ae.fiscal_year = %s",
# 		"ae.is_cancelled = 0",
# 	]

# 	values = [
# 		company,
# 		fiscal_year,
# 	]

# 	if party_type:
# 		conditions.append("ae.party_type = %s")
# 		values.append(party_type)

# 	if party:
# 		if isinstance(party, str):
# 			party = frappe.parse_json(party)

# 		if party:
# 			conditions.append("ae.customer IN %s")
# 			values.append(tuple(party))

# 	if account:
# 		conditions.append("mei.account = %s")
# 		values.append(account)

# 	if budget_activity:
# 		conditions.append("mei.budget_activity = %s")
# 		values.append(budget_activity)

# 	if budget_sub_activity:
# 		conditions.append("mei.budget_sub_activity = %s")
# 		values.append(budget_sub_activity)

# 	if source_of_fund:
# 		conditions.append("mei.source_of_fund = %s")
# 		values.append(source_of_fund)
# 	if filters.get("from_date") and filters.get("to_date"):
# 		conditions.append("ae.posting_date BETWEEN %s AND %s")
# 		values.extend([
# 			filters.get("from_date"),
# 			filters.get("to_date")
# 		])

# 	data = frappe.db.sql(
# 		f"""
# 		SELECT
# 			ae.company AS company,
# 			ae.fiscal_year as fiscal_year,
# 			ae.posting_date as posting_date,
# 			ae.customer AS party,
# 			ae.party_type AS party_type,
# 			ae.advance AS reference,
# 			mei.account AS code,
# 			mei.budget_activity AS activity_code,
# 			mei.budget_sub_activity AS sub_activity_code,
# 			mei.source_of_fund AS fi_code,
# 			SUM(
# 				CASE
# 					WHEN mei.is_opening = 1
# 					THEN COALESCE(mei.advance_amount, 0)
# 					ELSE 0
# 				END) AS opening_balance,
			
# 			SUM(
# 				CASE
# 					WHEN mei.is_opening = 0
# 					THEN COALESCE(mei.advance_amount, 0)
# 					ELSE 0
# 				END) AS advance_amount,
# 			SUM(COALESCE(mei.allocated_amount, 0)) AS settlement_amount,

# 		   (
# 			SUM(
# 				CASE
# 					WHEN mei.is_opening = 1
# 					THEN COALESCE(mei.advance_amount, 0)
# 					ELSE 0
# 				END
# 			)
# 			+
# 			SUM(
# 				CASE
# 					WHEN mei.is_opening = 0
# 					THEN COALESCE(mei.advance_amount, 0)
# 					ELSE 0
# 				END
# 			)
# 			-
# 			SUM(
# 				COALESCE(mei.allocated_amount, 0)
# 			)
# 		) AS total_outstanding
		

# 		FROM `tabAdvance Entry` ae
# 		INNER JOIN `tabMobilisation Entry Item` mei
# 			ON mei.parent = ae.name
# 		WHERE {" AND ".join(conditions)}
# 		GROUP BY
# 			ae.customer

# 		ORDER BY ae.posting_date ASC
# 		""",
# 		values,
# 		as_dict=True,
# 	)

# 	return data

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
            "fieldname": "party_name",
            "label": _("Party Name"),
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
            "fieldname": "associated_remarks",
            "label": _("Name"),
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
            "fieldname": "budget_activity_code",
            "label": _("Budget Activity Code"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "budget_sub_activity",
            "label": _("Budget Sub Activity"),
            "fieldtype": "Data",
            "width": 120,

        },
        {
            "fieldname": "budget_sub_activity_code",
            "label": _("Budget Sub Activity Code"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
          "fieldname": "program_code",
          "label": _("Program Code"),
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

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("ae.posting_date BETWEEN %s AND %s")
        values.extend([
            filters.get("from_date"),
            filters.get("to_date")
        ])    

    data = frappe.db.sql(
        f"""
        SELECT
            ae.company AS company,
            ae.customer AS party,
            ae.party_type AS party_type,
            c.program_code as program_code,
            CASE
                WHEN ae.party_type = 'Employee' THEN emp.employee_name
                WHEN ae.party_type = 'Supplier' THEN sup.supplier_name
                WHEN ae.party_type = 'Customer' THEN cust.customer_name
                ELSE ae.customer
            END AS party_name,
            ae.advance AS reference,
            mei.account AS code,
            mei.budget_activity AS activity_code,
            ba.activity_code as budget_activity_code,
            mei.budget_sub_activity AS budget_sub_activity,
            bsf.sub_activity_code as budget_sub_activity_code,
            mei.source_of_fund AS fi_code,
            mei.particular AS associated_remarks,

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
        INNER JOIN `tabBudget Activity` ba
            ON mei.budget_activity = ba.name
        INNER JOIN `tabBudget Sub Activity` bsf
            ON mei.budget_sub_activity = bsf.name
        INNER JOIN `tabCompany` c
            ON ae.company = c.name
        LEFT JOIN `tabEmployee` emp
            ON ae.party_type = 'Employee'
            AND emp.name = ae.customer
        

        LEFT JOIN `tabSupplier` sup
            ON ae.party_type = 'Supplier'
            AND sup.name = ae.customer

        LEFT JOIN `tabCustomer` cust
            ON ae.party_type = 'Customer'
            AND cust.name = ae.customer
        WHERE {" AND ".join(conditions)}

        ORDER BY ae.customer ASC
        """,
        values,
        as_dict=True,
    )

    return data