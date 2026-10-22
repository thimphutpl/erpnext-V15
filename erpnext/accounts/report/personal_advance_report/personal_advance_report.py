# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	return [
		{
			"label": "Company",
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},
		{
			"label": "Fiscal Year",
			"fieldname": "fiscal_year",
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"width": 120
		},
        {
            "label":"Code",
            "fieldname":"code",
            "fieldtype": "Data",
			"width": 180

        },
		{
			"label": "Employee Name",
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": "Cost Center",
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 120
		},
		{
			"label": "Posting Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": "Account",
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180,
		},
		
		{
			"label": "Advance Amount",
			"fieldname": "advance_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Settlement amount",
			"fieldname": "paid_amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": "Total Outstanding",
			"fieldname": "total_outstanding",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			
			"label": "Voucher No",
			"fieldname": "voucher_no",
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 120
		},
		{
			"label": "Against Voucher Type",
			"fieldname": "against_voucher_type",
			"fieldtype": "Data",
			"width": 140,
		}
	]


# def get_data(filters):
	
  

# 	conditions = [
# 		"""
# 		(
# 			gl.against_voucher_type IN (
# 				'Employee Advance',
# 				'Payroll Entry'
# 			)
# 			OR
# 			(
#             gl.account IN (
#                 '88.01 - Personal Advances - RBA',
#                 '88.02 - Personal Advances - RBG'
#             )
#             AND
#             gl.voucher_subtype = 'Other Voucher'
#         	)
# 			AND gl.against_voucher_type != 'Advance Settlement'
# 		)
	
# 		"""
# 	]
# 	values = []

# 	if filters.get("fiscal_year"):
# 		conditions.append("gl.fiscal_year = %s")
# 		values.append(filters.get("fiscal_year"))

# 	if filters.get("from_date") and filters.get("to_date"):
# 		conditions.append("gl.posting_date BETWEEN %s AND %s")
# 		values.extend([filters.get("from_date"), filters.get("to_date")])

# 	if filters.get("company"):
# 		conditions.append("gl.company = %s")
# 		values.append(filters.get("company"))

# 	if filters.get("employee"):
# 		conditions.append("gl.party = %s")
# 		values.append(filters.get("employee"))


# 	where_clause = " AND ".join(conditions)

# 	query = f"""
# 		SELECT
# 		    gl.company as company,
# 			gl.fiscal_year as fiscal_year,
# 			gl.party AS employee,
# 			emp.employee_name,
# 			gl.cost_center,
# 			gl.posting_date,
# 			gl.account,
# 			gl.voucher_type,
# 			gl.voucher_no,
# 			gl.against_voucher_type,


# 			SUM(
# 				CASE
# 					WHEN gl.against_voucher_type = 'Employee Advance'
# 					THEN gl.debit
# 					ELSE 0
# 				END
# 			) AS advance_amount,

# 			SUM(
# 				CASE
# 					WHEN gl.against_voucher_type ='Payroll Entry'
# 					OR 
# 					(
# 						gl.account IN (
# 							'88.01 - Personal Advances - RBA',
# 							'88.02 - Personal Advances - RBG'
# 						)
# 						AND gl.voucher_subtype = 'Other Voucher'
# 					)
# 					AND gl.against_voucher_type != 'Advance Settlement'

				
# 					THEN gl.credit
				
# 					ELSE 0
# 				END
# 			) AS paid_amount,

# 			SUM(
# 				CASE
# 					WHEN gl.against_voucher_type = 'Employee Advance'
# 					THEN gl.debit
# 					WHEN gl.against_voucher_type ='Payroll Entry'
# 					OR 
# 					(
# 						gl.account IN (
# 							'88.01 - Personal Advances - RBA',
# 							'88.02 - Personal Advances - RBG'
# 						)
# 						AND gl.voucher_subtype = 'Other Voucher'
# 					)
# 					AND gl.against_voucher_type != 'Advance Settlement'
# 					THEN -gl.credit

# 					ELSE 0
# 				END
# 			) AS total_outstanding

# 		FROM `tabGL Entry` gl

# 		INNER JOIN `tabEmployee` emp
# 			ON emp.name = gl.party


# 		WHERE {where_clause}

# 		GROUP BY
# 			gl.party

		
# 		ORDER BY
# 			gl.party ASC
# 	"""

# 	return frappe.db.sql(query, values, as_dict=True)

def get_data(filters):

    conditions = [
        "gl.is_cancelled = 0",
        """
        (
            (
                gl.against_voucher_type IN (
                    'Employee Advance',
                    'Payroll Entry'
                )
                OR
                (
                    gl.account IN (
                        '88.01 - Personal Advances - RBA',
                        '88.02 - Personal Advances - RBG'
                    )
                    AND gl.voucher_subtype = 'Other Voucher'
					AND (
						gl.against_voucher_type IS NULL
						OR gl.against_voucher_type != 'Advance Settlement'
					)
                )
            )

        )
        """
    ]

    values = []

    if filters.get("fiscal_year"):
        conditions.append("gl.fiscal_year = %s")
        values.append(filters.get("fiscal_year"))

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("gl.posting_date BETWEEN %s AND %s")
        values.extend([
            filters.get("from_date"),
            filters.get("to_date")
        ])

    if filters.get("company"):
        conditions.append("gl.company = %s")
        values.append(filters.get("company"))

    if filters.get("employee"):
        conditions.append("gl.party = %s")
        values.append(filters.get("employee"))

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            gl.company AS company,
            gl.fiscal_year AS fiscal_year,
            gl.party AS code,
            emp.employee_name,
            gl.cost_center,
            gl.posting_date,
            gl.account,
            gl.voucher_type,
            gl.voucher_no,
            gl.against_voucher_type,

            /* Advance */
            SUM(
                CASE
                    WHEN gl.against_voucher_type = 'Employee Advance'
                    THEN COALESCE(gl.debit, 0)
                    ELSE 0
                END
            ) AS advance_amount,

            /* Paid */
            SUM(
                CASE
                    WHEN (
                        gl.against_voucher_type = 'Payroll Entry'
                        OR
                        (
                            gl.account IN (
                                '88.01 - Personal Advances - RBA',
                                '88.02 - Personal Advances - RBG'
                            )
                            AND gl.voucher_subtype = 'Other Voucher'
                        )
                    )
                    THEN COALESCE(gl.credit, 0)
                    ELSE 0
                END
            ) AS paid_amount,

            /* Outstanding */
            SUM(
                CASE
                    WHEN gl.against_voucher_type = 'Employee Advance'
                    THEN COALESCE(gl.debit, 0)

                    WHEN (
                        gl.against_voucher_type = 'Payroll Entry' 
                        OR
                        (
                            gl.account IN (
                                '88.01 - Personal Advances - RBA',
                                '88.02 - Personal Advances - RBG'
                            )
                            AND gl.voucher_subtype = 'Other Voucher'
                        )
                    )
                    THEN -COALESCE(gl.credit, 0)

                    ELSE 0
                END
            ) AS total_outstanding

        FROM `tabGL Entry` gl

        INNER JOIN `tabEmployee` emp
            ON emp.name = gl.party

        WHERE {where_clause}

        GROUP BY
            gl.party

        ORDER BY
            gl.party ASC
    """

    return frappe.db.sql(query, values, as_dict=True)