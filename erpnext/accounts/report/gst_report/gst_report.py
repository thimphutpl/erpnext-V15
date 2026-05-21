import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters=None):

	account_type = filters.get("account_type") if filters else None

	base_columns = [
		{
			"label": "Posting Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label":"Month",
			"fieldname":"month",
			"fieldtype":"Data",
			"width":120

		},
		{
			"label": "Voucher Type",
			"fieldname": "voucher_type",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Cost Center",
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options":"Cost Center",
			"width": 150

		},
		{
			"label": "Bill No",
			"fieldname": "bill_no",
			"fieldtype": "Data",
			"width": 150

		},
		{
			"label": "Bill Date",
			"fieldname": "bill_date",
			"fieldtype": "Date",
			"width": 150

		},
		{
			"label": "Voucher No",
			"fieldname": "voucher_no",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Supplier/Customer",
			"fieldname": "supplier_name",
			"fieldtype": "Data",
			"width": 200
		},
	]

	if account_type == "GST 5% Paid - CDCL":

		base_columns.insert(6, {
			"label": "Bill Amount",
			"fieldname": "bill_amount",
			"fieldtype": "Currency",
			"width": 150
		})
		base_columns.insert(7, {
			"label": "5% GST Paid",
			"fieldname": "gst_paid",
			"fieldtype": "Currency",
			"width": 150
		})
	else:
		base_columns.insert(6, {
			"label": "Bill Amount",
			"fieldname": "bill_amount",
			"fieldtype": "Currency",
			"width": 150
		})
		base_columns.insert(7, {
			"label": "5% GST Receive",
			"fieldname": "gst_receive",
			"fieldtype": "Currency",
			"width": 150
		})

	return base_columns


def get_data(filters):

	account_type = filters.get("account_type")
	month = filters.get("month")
	voucher_type=filters.get("voucher_type")

	conditions = []
	values = []

	if month:
		conditions.append("MONTHNAME(gl.posting_date) = %s")
		values.append(month)
	if account_type:
		conditions.append("gl.account = %s")
		values.append(account_type)
	if voucher_type:
		conditions.append("gl.voucher_type = %s")
		values.append(voucher_type)

	where_clause = " AND ".join(conditions)
	
	if where_clause:
		where_clause = "WHERE " + where_clause

	if account_type == "GST 5% Paid - CDCL" and voucher_type in ["Purchase Invoice", "POL Receive"]:
		query = f"""
			SELECT
				gl.posting_date,
				MONTHNAME(gl.posting_date) as month,
				gl.cost_center,
				gl.voucher_type,
				gl.voucher_no,
				COALESCE(
					pol.gst_amount,
					ptc.tax_amount

					) AS gst_paid,

				COALESCE(
					pol.memo_number,
					pi.bill_no
				) AS bill_no,
				COALESCE(
					pol.posting_date,
					pi.bill_date
				) AS bill_date,
				COALESCE(
					pol.supplier,
					pi.supplier
				) AS supplier_name,
				COALESCE(
					pol.total_amount,
					pi.total
				) AS bill_amount
			FROM `tabGL Entry` gl
			LEFT JOIN `tabPurchase Invoice` pi
				ON gl.voucher_type = 'Purchase Invoice'
				AND gl.voucher_no = pi.name

			LEFT JOIN `tabPurchase Taxes and Charges` ptc
				ON pi.name = ptc.parent
			LEFT JOIN `tabPOL Receive` pol
				ON gl.voucher_type = 'POL Receive'
				AND gl.voucher_no = pol.name
		
			{where_clause}
			AND gl.is_cancelled = 0
			ORDER BY gl.posting_date DESC
		"""
		return frappe.db.sql(query, values, as_dict=1)
	elif account_type == "GST 5% Paid - CDCL" and voucher_type =="Utility Bill":
		query = f"""
			SELECT
			   ub.name as voucher_no,
				ub.posting_date as posting_date,
				 MONTHNAME(ub.posting_date) as month,
				ub.cost_center as cost_center,
				ub.total_gst_amount AS gst_paid,
				ub.posting_date AS bill_date,
				ub.net_payable_amount AS bill_amount,
				"Utility Bill" as voucher_type
			FROM `tabUtility Bill` as ub
			WHERE 
				ub.docstatus = 1
		"""

		values = []
		if month:
			query += " AND MONTHNAME(ub.posting_date) = %s"
			values.append(month)

		query += " ORDER BY ub.posting_date DESC"
		return frappe.db.sql(query,as_dict=1)
	elif account_type == "GST 5% Paid - CDCL" and voucher_type =="Imprest Recoup":
		voucher_type =="Imprest Recoup"
		query = f"""
			SELECT
				ir.name as voucher_no,
				ir.posting_date as posting_date,
				MONTHNAME(ir.posting_date) as month,
				ir.cost_center as cost_center,
				ir.gst_amount AS gst_paid,
				ir.posting_date AS bill_date,
				ir.opening_balance AS bill_amount,
				ir.party as supplier_name,
				"Imprest Recoup" as	voucher_type
				 
			FROM `tabImprest Recoup` as ir
			WHERE 
				ir.docstatus = 1
			"""
		values = []
		if month:
			query += " AND MONTHNAME(ir.posting_date) = %s"
			values.append(month)

		query += " ORDER BY ir.posting_date DESC"
		return frappe.db.sql(query,as_dict=1)
	elif account_type=="GST 5% Received - CDCL" and voucher_type in ["Hire Charge Invoice","Mechanical Payment","Project Invoice","Sales Invoice"]:
		query = f"""
			SELECT
				gl.posting_date,
				MONTHNAME(gl.posting_date) as month,
				gl.cost_center,
				gl.voucher_type,
				gl.voucher_no,
				COALESCE(
					pji.cost_center,
					si.cost_center
				)AS cost_center,
				COALESCE(
					si.posting_date,
					r.posting_date,
					pji.invoice_date
				) AS bill_date,
				COALESCE(
					r.gst_amount,
					pji.gst_amount,
					mpi.gst_amount,
					hci.gst_amount,
					stc.tax_amount
				)AS gst_receive,
				COALESCE(
					r.total_amount,
					pji.gross_invoice_amount,
					mpi.outstanding_amount,
					hci.total_invoice_amount,
					si.total
				) AS bill_amount,
				COALESCE(
					mpi.customer,
					hci.customer,
					pji.party,
					si.customer
				) AS supplier_name
			FROM `tabGL Entry` gl
			LEFT JOIN `tabHire Charge Invoice` hci
				ON gl.voucher_type = 'Hire Charge Invoice'
				AND gl.voucher_no = hci.name
			LEFT JOIN `tabMechanical Payment` mp
				ON gl.voucher_type = 'Mechanical Payment'
				AND gl.voucher_no = mp.name
			LEFT JOIN `tabMechanical Payment Item` mpi 
				ON mp.name=mpi.parent
			LEFT JOIN `tabProject Invoice` pji
				ON gl.voucher_type = 'Project Invoice'
				AND gl.voucher_no = pji.name
			LEFT JOIN `tabRental` r
				 ON gl.voucher_type = 'Rental'
				AND gl.voucher_no = r.name
			LEFT JOIN `tabSales Invoice` si
				ON gl.voucher_type = 'Sales Invoice'
				AND gl.voucher_no = si.name
			LEFT JOIN `tabSales Taxes and Charges` stc
				ON si.name=stc.parent	
			{where_clause}
			AND gl.is_cancelled = 0
			ORDER BY gl.posting_date DESC
		"""

		return frappe.db.sql(query, values, as_dict=1)
	elif account_type == "GST 5% Received - CDCL":

		month_condition = ""
		si_month = ""
		r_month = ""
		pji_month = ""
		hci_month = ""

		if month:
			month_condition = "AND MONTHNAME(gl.posting_date) = %(month)s"
			si_month = "AND MONTHNAME(si.posting_date) = %(month)s"
			r_month = "AND MONTHNAME(r.posting_date) = %(month)s"
			pji_month = "AND MONTHNAME(pji.invoice_date) = %(month)s"
			hci_month = "AND MONTHNAME(hci.posting_date) = %(month)s"

		query = f"""
			SELECT
				gl.posting_date,
				MONTHNAME(gl.posting_date) as month,
				gl.cost_center,
				gl.voucher_type,
				gl.voucher_no,

				COALESCE(
					r.gst_amount,
					pji.gst_amount,
					hci.gst_amount,
					si_tax.tax_amount
				) AS gst_receive,

				NULL as bill_no,

				COALESCE(
					si.posting_date,
					r.posting_date,
					pji.invoice_date,
					hci.posting_date
				) AS bill_date,

				COALESCE(
					si.customer,
					r.customer,
					pji.party,
					hci.customer
				) AS supplier_name,

				COALESCE(
					r.total_amount,
					pji.gross_invoice_amount,
					hci.total_invoice_amount,
					si.total
				) AS bill_amount

			FROM `tabGL Entry` gl

			LEFT JOIN `tabSales Invoice` si
				ON gl.voucher_type = 'Sales Invoice'
				AND gl.voucher_no = si.name

			LEFT JOIN `tabSales Taxes and Charges` si_tax
				ON si.name = si_tax.parent

			LEFT JOIN `tabHire Charge Invoice` hci
				ON gl.voucher_type = 'Hire Charge Invoice'
				AND gl.voucher_no = hci.name

			LEFT JOIN `tabProject Invoice` pji
				ON gl.voucher_type = 'Project Invoice'
				AND gl.voucher_no = pji.name

			LEFT JOIN `tabRental` r
				ON gl.voucher_type = 'Rental'
				AND gl.voucher_no = r.name

			WHERE gl.voucher_type IN (
				'Sales Invoice',
				'Hire Charge Invoice',
				'Project Invoice',
				'Rental',
				'Mechanical Payment'
			)
			AND gl.is_cancelled = 0
			{month_condition}

			ORDER BY gl.posting_date DESC
		"""

		return frappe.db.sql(query, {"month": month}, as_dict=1)
	elif account_type == "GST 5% Paid - CDCL":

		conditions_pi = ""
		conditions_ir = ""
		conditions_ub = ""

		if month:
			conditions_pi = "AND MONTHNAME(gl.posting_date) = %(month)s"
			conditions_ir = "AND MONTHNAME(ir.posting_date) = %(month)s"
			conditions_ub = "AND MONTHNAME(ub.posting_date) = %(month)s"

		query = f"""
			SELECT
				gl.posting_date,
				MONTHNAME(gl.posting_date) as month,
				gl.cost_center,
				gl.voucher_type,
				gl.voucher_no,
				COALESCE(pol.gst_amount, ptc.tax_amount) AS gst_paid,
				COALESCE(pol.memo_number, pi.bill_no) AS bill_no,
				COALESCE(pol.posting_date, pi.bill_date) AS bill_date,
				COALESCE(pol.supplier, pi.supplier) AS supplier_name,
				COALESCE(pol.total_amount, pi.total) AS bill_amount
			FROM `tabGL Entry` gl
			LEFT JOIN `tabPurchase Invoice` pi
				ON gl.voucher_type = 'Purchase Invoice'
				AND gl.voucher_no = pi.name
			LEFT JOIN `tabPurchase Taxes and Charges` ptc
				ON pi.name = ptc.parent
			LEFT JOIN `tabPOL Receive` pol
				ON gl.voucher_type = 'POL Receive'
				AND gl.voucher_no = pol.name
			WHERE gl.voucher_type IN ('Purchase Invoice', 'POL Receive')
			AND gl.is_cancelled = 0
			{conditions_pi}

			UNION ALL

			SELECT
				ir.posting_date,
				MONTHNAME(ir.posting_date) as month,
				ir.cost_center,
				'Imprest Recoup',
				ir.name,
				ir.gst_amount as gst_paid,
				NULL,
				ir.posting_date,
				ir.party,
				ir.opening_balance
			FROM `tabImprest Recoup` ir
			WHERE ir.docstatus = 1
			{conditions_ir}

			UNION ALL

			SELECT
				ub.posting_date,
				MONTHNAME(ub.posting_date) as month,
				ub.cost_center,
				'Utility Bill',
				ub.name,
				ub.total_gst_amount as gst_paid,
				NULL,
				ub.posting_date,
				NULL,
				ub.net_payable_amount
			FROM `tabUtility Bill` ub
			WHERE ub.docstatus = 1
			{conditions_ub}

			ORDER BY posting_date DESC
		"""

		return frappe.db.sql(query, {"month": month}, as_dict=1)
	else:
		return []
		

