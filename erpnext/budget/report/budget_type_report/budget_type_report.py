import frappe


def execute(filters=None):
	filters = filters or {}
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	if filters.get('aggregate'):
		return [
            {"label": "Budget Type", "fieldname": "budget_type", "fieldtype": "Data", "width": 120},
            {"label": "Budget Amount", "fieldname": "budget_amount", "fieldtype": "Currency", "width": 150},
            {"label": "Budget Consumed", "fieldname": "consumed_budget", "fieldtype": "Currency", "width": 150},
        ]
	else:
		return [
			("Budget") + ":Link/Budget:180",
			("Cost Center") + ":Link/Cost Center:180",
			("Account") + ":Link/Account:180",
			("Budget Type") + ":Data:120",
			("Budget Amount") + ":Currency:150",
			("Budget Consumed") + ":Currency:150",
			
		]

def get_data(filters=None):
	filters = filters or {}
	conditions = get_conditions(filters)  # Returns string like " AND b.cost_center='X' AND b.company='Y' ..."

	if filters.get("aggregate"):
		# Aggregate query
		query = f"""
			SELECT
				ba.budget_type,
				SUM(ba.budget_amount) AS budget_amount
			FROM `tabBudget` b
			INNER JOIN `tabBudget Account` ba
				ON b.name = ba.parent
			WHERE b.docstatus = 1
			{conditions}
			GROUP BY ba.budget_type
		"""
		data = frappe.db.sql(query, as_dict=True)

		# Add consumed budget per type with filters
		from_date, to_date = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ['year_start_date', 'year_end_date'])

		# for row in data:
		for row in data:
			consumed_query = frappe.db.sql(
				"""
				SELECT SUM(amount) 
				FROM `tabConsumed Budget`
				WHERE company = %s
				AND budget_type = %s
				AND reference_date BETWEEN %s AND %s
				""",
				(filters.company, filters.budget_type, from_date, to_date)
			)

			# frappe.throw(str(consumed_query))
			
			# Add consumed_budget to the row dictionary
			row['consumed_budget'] = float(consumed_query[0][0]) if consumed_query[0][0] else 0
		# frappe.throw(str(data))

	else:
		# Non-aggregate query
		query = f"""
			SELECT
				ba.parent AS budget,
				b.cost_center AS cost_center,
				ba.account,
				ba.budget_type,
				ba.budget_amount
			FROM `tabBudget` b
			INNER JOIN `tabBudget Account` ba
				ON b.name = ba.parent
			WHERE b.docstatus = 1
			{conditions}
		"""
		data = frappe.db.sql(query, as_dict=True)

	return data




def get_conditions(filters):
	conditions = ""

	

	if filters.get("budget_type"):
		conditions += " AND ba.budget_type = '{}'".format(filters.get("budget_type"))
	if filters.get("cost_center"):
		conditions += " AND b.cost_center = '{}'".format(filters.get("cost_center"))
	if filters.get("company"):
		conditions += " AND b.company = {}".format(
			frappe.db.escape(filters.get("company"))
		)


	return conditions
