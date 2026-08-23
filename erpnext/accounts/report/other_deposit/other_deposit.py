
import frappe


def execute(filters=None):
    filters = filters or {}

    columns = [
     
        {
            "label": "Party Type",
            "fieldname": "party_type",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Party",
            "fieldname": "party",
            "fieldtype": "Dynamic Link",
            "options": "party_type",
            "width": 200,
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 80,
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
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180,
        },

        
        {
            "label": "Opening Balance",
            "fieldname": "opening_balance",
            "fieldtype": "Currency",
            "width": 180,
        },
        {
            "label": "FY Balance",
            "fieldname": "fy_balance",
            "fieldtype": "Currency",
            "width": 180,
        },
       
  
        {
            "label": "Total Outstanding",
            "fieldname": "total_outstanding",
            "fieldtype": "Currency",
            "width": 120,
        },
    ]

    conditions = [
  
    ]

    values = {}

    if filters.get("company"):
        conditions.append("gl.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date"):
        conditions.append("gl.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("gl.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    if filters.get("account"):
        conditions.append("gl.account = %(account)s")
        values["account"] = filters["account"]

    if filters.get("party_type"):
        conditions.append("gl.party_type = %(party_type)s")
        values["party_type"] = filters["party_type"]

    if filters.get("party"):
        conditions.append("gl.party = %(party)s")
        values["party"] = filters["party"]

    data = frappe.db.sql(
		   f"""
		   SELECT
                gl.name,
                gl.posting_date AS posting_date,
                gl.account AS account,
                gl.party_type AS party_type,
                gl.party AS party,
                gl.voucher_type as voucher_type,
                gl.voucher_no as voucher_no,
                CASE
                    WHEN gl.is_opening = 'Yes' THEN gl.credit - gl.debit
                    ELSE 0
                END AS opening_balance,
                gl.credit as fy_balance,
                gl.credit-gl.debit as total_outstanding
		   FROM `tabGL Entry` gl
		   WHERE {" AND ".join(conditions)}
		   ORDER BY
			   gl.posting_date
		   """,
		   values,
		   as_dict=True,
	   )

    return columns, data
