import frappe
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	report_type = filters.get("report_type")

	if report_type == "Schedule of Revenue Receipt & Remittances":

		return [
			{
				"label": "A/C Code", 
				"fieldname": "account_code", 
				"fieldtype": "Data", 
				"width": 200
				},
			{
				"label": "Object Code", 
				"fieldname": "object_code", 
				"fieldtype": "Data", 
				"width": 150
			},
			{
				"label": "Object Name", 
				"fieldname": "object_name", 
				"fieldtype": "Data", 
				"width": 300
			},

			{
				"label": "Receipt Amount (Nu.)", 
				"fieldname": "receipt_amount", 
				"fieldtype": "Currency", 
				"width": 150
			},
			{
				"label": "Annual Progressive Receipt (Nu.)", 
				"fieldname": "annual_progressive_receipt", 
				"fieldtype": "Currency", 
				"width": 180
			},

			{
				"label": "Remittance Amount (Nu.)", 
				"fieldname": "remittance_amount", 
				"fieldtype": "Currency", "width": 150
			},
			{
				"label": "Annual Progressive Remittance (Nu.)", 
				"fieldname": "annual_progressive_remittance", 
				"fieldtype": "Currency", 
				"width": 180
			},
		]
	elif report_type == "Schedule of Other Recoveries & Remittances":
		return [
			{
				"label": "A/C Code", 
				"fieldname": "parent_code", 
				"fieldtype": "Data", 
				"width": 200
				},
			{
				"label": "Object Code", 
				"fieldname": "object_code", 
				"fieldtype": "Data", 
				"width": 150
			},
			{
				"label": "Object Name", 
				"fieldname": "object_name", 
				"fieldtype": "Data", 
				"width": 300
			},

			{
				"label": "Receipt Amount (Nu.)", 
				"fieldname": "receipt_amount", 
				"fieldtype": "Currency", 
				"width": 150
			},
			{
				"label": "Annual Progressive Receipt (Nu.)", 
				"fieldname": "annual_progressive_receipt", 
				"fieldtype": "Currency", 
				"width": 180
			},

			{
				"label": "Remittance Amount (Nu.)", 
				"fieldname": "remittance_amount", 
				"fieldtype": "Currency", "width": 150
			},
			{
				"label": "Annual Progressive Remittance (Nu.)", 
				"fieldname": "annual_progressive_remittance", 
				"fieldtype": "Currency", 
				"width": 180
			},
		]
	elif report_type =="Schedule of Miscellaneous Receipt & Payment":
		return [
			{
				"label": "A/C Code", 
				"fieldname": "parent_code", 
				"fieldtype": "Data", 
				"width": 200
				},
			{
				"label": "Object Code", 
				"fieldname": "object_code", 
				"fieldtype": "Data", 
				"width": 150
			},
			{
				"label": "Object Name", 
				"fieldname": "object_name", 
				"fieldtype": "Data", 
				"width": 300
			},

			{
				"label": "Receipt Amount (Nu.)", 
				"fieldname": "receipt_amount", 
				"fieldtype": "Currency", 
				"width": 150
			},
			{
				"label": "Annual Progressive Receipt (Nu.)", 
				"fieldname": "annual_progressive_receipt", 
				"fieldtype": "Currency", 
				"width": 180
			},

			{
				"label": "Payment Amount (Nu.)", 
				"fieldname": "payment_amount", 
				"fieldtype": "Currency", "width": 150
			},
			{
				"label": "Annual Progressive Remittance (Nu.)", 
				"fieldname": "annual_progressive_remittance", 
				"fieldtype": "Currency", 
				"width": 180
			},
		]
	elif report_type == "Schedule of Suspense - PW Advances":
		return [
			{
				"label": "Identity Code", 
				"fieldname": "identity_code", 
				"fieldtype": "Data", 
				"width": 200
				},
			{
				"label": "Name", 
				"fieldname": "name", 
				"fieldtype": "Data", 
				"width": 150
			},
			{
				"label": "Opening Balance (Nu.)", 
				"fieldname": "opening_balance", 
				"fieldtype": "Currency", 
				"width": 300
			},
			{
				"label": "Credit Amount (Nu.)", 
				"fieldname": "credit_amount", 
				"fieldtype": "Currency", 
				"width": 150
			},
			{
				"label": "Debit Amount (Nu.)", 
				"fieldname": "debit_amount", 
				"fieldtype": "Currency", 
				"width": 180
			},
			{
				"label":"Activity Code",
				"fieldname":"activity_code",
				"fieldtype":"Data",
				"width":180
			},
			{
				"label":"Date of Original Advance",
				"fieldname":"date_of_original_advance",
				"fieldtype":"Date",
				"width":180
			}
		]
	elif report_type=="Schedule of Fund Releases Included in the Monthly Accounts":
		{
			"label": "DBR Release Order No.",
			"fieldname": "dbr_release_order_no",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label":"Date",
			"fieldname":"date",
			"fieldtype":"Date",
			"width":180

		},
		{
			"label":"Amount (Nu.)",
			"fieldname":"amount",
			"fieldtype":"Currency",
			"width":180
		},
		{
			"lable":"Annual Progressive Amount (Nu.)",
			"fieldname":"annual_progressive_amount",
			"fieldtype":"Currency",
			"width":180
		},
		{
			"label":"Remarks",
			"fieldname":"remarks",
			"fieldtype":"Data",
			"width":180
		}
	else:
		return []


def get_data(filters):
	if not filters:
		return []
	
	report_type = filters.get("report_type")
	if not report_type:
		return

	fiscal_year = filters.get("fiscal_year")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	company = filters.get("company")
	month = filters.get("month")

	if not (fiscal_year and from_date and to_date and company):
		return []
	if report_type == "Schedule of Revenue Receipt & Remittances":

		query = """
			SELECT
				parent_acc.account_number AS account_code,
				acc.account_number AS object_code,
				acc.account_name AS object_name,
				SUM(
					CASE
						WHEN gl.posting_date BETWEEN %s AND %s
						THEN gl.credit
						ELSE 0
					END
				) AS receipt_amount,
				SUM(
					CASE
						WHEN gl.posting_date <= %s
						THEN gl.credit
						ELSE 0
					END
				) AS annual_progressive_receipt,
				SUM(
					CASE
						WHEN gl.posting_date BETWEEN %s AND %s
						THEN gl.debit
						ELSE 0
					END
				) AS remittance_amount,
				SUM(
					CASE
						WHEN gl.posting_date <= %s
						THEN gl.debit
						ELSE 0
					END
				) AS annual_progressive_remittance

			FROM `tabGL Entry` gl

			JOIN `tabAccount` acc
				ON gl.account = acc.name

			LEFT JOIN `tabAccount` parent_acc
				ON acc.parent_account = parent_acc.name

			WHERE
				gl.fiscal_year = %s
				AND gl.posting_date BETWEEN %s AND %s
				AND gl.company = %s
				AND acc.company = %s
				AND gl.is_cancelled = 0
				AND parent_acc.account_number = '5'
		"""

		params = [
			from_date,
			to_date,
			to_date,
			from_date,
			to_date,
			to_date,
			fiscal_year,
			from_date,
			to_date,
			company,
			company
		]

		if month:
			query += " AND MONTHNAME(gl.posting_date) = %s"
			params.append(month)

		query += """
			GROUP BY
				parent_acc.account_number,
				acc.account_number,
				acc.account_name
		"""

		return frappe.db.sql(query, params, as_dict=True)
	elif report_type == "Schedule of Other Recoveries & Remittances":

		query = """
			SELECT
				level2.account_number AS parent_code,
				acc.account_number AS object_code,
				acc.account_name AS object_name,
				SUM(
					CASE
						WHEN gl.posting_date BETWEEN %s AND %s
						THEN gl.credit
						ELSE 0
					END
				) AS receipt_amount,
				SUM(
					CASE
						WHEN gl.posting_date <= %s
						THEN gl.credit
						ELSE 0
					END
				) AS annual_progressive_receipt,
				SUM(
					CASE
						WHEN gl.posting_date BETWEEN %s AND %s
						THEN gl.debit
						ELSE 0
					END
				) AS remittance_amount,
				SUM(
					CASE
						WHEN gl.posting_date <= %s
						THEN gl.debit
						ELSE 0
					END
				) AS annual_progressive_remittance
			FROM `tabAccount` acc
			JOIN `tabAccount` level2 ON acc.parent_account = level2.name
			JOIN `tabAccount` level1 ON level2.parent_account = level1.name
			JOIN `tabGL Entry` gl
				ON gl.account = acc.name
				AND gl.fiscal_year = %s
				AND gl.posting_date BETWEEN %s AND %s
				AND gl.company = %s
				AND gl.is_cancelled = 0
			WHERE
				level1.account_number = '6'
		"""
		params = [
					from_date,
					to_date,
					to_date,
					from_date,
					to_date,
					to_date,
					fiscal_year,
					from_date,
					to_date,
					company
				]

		if month:
			query += " AND MONTHNAME(gl.posting_date) = %s"
			params.append(month)

		query += """
			GROUP BY
				  level2.account_number,
				acc.account_number,
				acc.account_name
			ORDER BY
					level2.account_number,
				acc.account_number
		"""

		return frappe.db.sql(query, params, as_dict=True)
	elif report_type == "Schedule of Miscellaneous Receipt & Payment":
		query = """
			SELECT
				level2.account_number AS parent_code,
				acc.account_number AS object_code,
				acc.account_name AS object_name,
				SUM(
					CASE
						WHEN gl.posting_date BETWEEN %s AND %s
						THEN gl.debit
						ELSE 0
					END
				) AS receipt_amount,
				SUM(
					CASE
						WHEN gl.posting_date <= %s
						THEN gl.debit
						ELSE 0
					END
				) AS annual_progressive_receipt,
				SUM(
					CASE
						WHEN gl.posting_date BETWEEN %s AND %s
						THEN gl.credit
						ELSE 0
					END
				) AS payment_amount,
				SUM(
					CASE
						WHEN gl.posting_date <= %s
						THEN gl.credit
						ELSE 0
					END
				) AS annual_progressive_remittance
			FROM `tabAccount` acc
			LEFT JOIN `tabAccount` level2 ON acc.parent_account = level2.name
			LEFT JOIN `tabAccount` level1 ON level2.parent_account = level1.name
			LEFT JOIN `tabGL Entry` gl
				ON (gl.account = acc.name)
				AND gl.fiscal_year = %s
				AND gl.posting_date BETWEEN %s AND %s
				AND gl.company = acc.company 
	
			
			WHERE
				level1.account_number = '8'
				AND gl.is_cancelled = 0
				AND gl.company = %s
			
		"""
		params = [
				from_date,
				to_date,
				to_date,
				from_date,
				to_date,
				to_date,
				fiscal_year,
			 	from_date,
			   	to_date,
				company
				]

		if month:
			query += " AND MONTHNAME(gl.posting_date) = %s"
			params.append(month)

		query += """
			GROUP BY
				parent_code,
				acc.account_number,
				acc.account_name
			ORDER BY
				parent_code,
				acc.account_number
		"""

		return frappe.db.sql(query, params, as_dict=True)
	elif report_type == "Schedule of Suspense - PW Advances":
			
		query = """
				SELECT
					CASE
						WHEN a.party_type = 'Supplier' THEN s.supplier_tpn_no
						WHEN a.party_type = 'Employee' THEN e.name
						ELSE NULL
					END AS identity_code,
				    
					gl.party AS name,
					SUM(
						CASE
							WHEN gl.posting_date BETWEEN %s AND %s 
							AND gl.against_voucher_type = "Advance Recoup"
							THEN gl.debit
							ELSE 0
						END
					) AS debit_amount,
					
					SUM(
						CASE
							WHEN gl.posting_date BETWEEN %s AND %s
							AND gl.against_voucher_type = "Advance Recoup"
							THEN gl.credit
							ELSE 0
						END
					) AS credit_amount,
					gl.budget_activity as activity_code,
					SUM(
						CASE
							WHEN gl.against_voucher_type ="Advance"
							
							THEN gl.debit
							ELSE 0
						END
					) AS opening_balance,
					gl.posting_date as date_of_original_advance				
				FROM `tabAccount` acc
				LEFT JOIN `tabAccount` level2 ON acc.parent_account = level2.name
				LEFT JOIN `tabAccount` level1 ON level2.parent_account = level1.name
			
				LEFT JOIN `tabGL Entry` gl
					ON (gl.account = acc.name)
					AND gl.fiscal_year = %s
					AND gl.posting_date BETWEEN %s AND %s
					AND gl.company = acc.company 	
				LEFT JOIN `tabAdvance` a
					ON gl.against_voucher = a.name
					AND gl.against_voucher_type = 'Advance'

				LEFT JOIN `tabSupplier` s
					ON a.party_type = 'Supplier'
					AND a.customer = s.name	
				LEFT JOIN `tabEmployee` e
					ON a.party_type = 'Employee'
					AND a.customer = e.name
				
				WHERE
					level1.account_number = '9'
					AND gl.is_cancelled = 0
					AND gl.company = %s
				
			"""
		params = [
				from_date,
				to_date,
				from_date,
				to_date,
				fiscal_year,
				from_date,
				to_date,
				company
				]

		if month:
			query += " AND MONTHNAME(gl.posting_date) = %s"
			params.append(month)

		# query += """
		# 	GROUP BY
		# 		parent_code,
		# 		acc.account_number,
		# 		acc.account_name
		# 	ORDER BY
		# 		parent_code,
		# 		acc.account_number
		# """

		return frappe.db.sql(query, params, as_dict=True)
	elif report_type == "Schedule of Fund Releases Included in the Monthly Accounts":
		pass
		
		
	return []