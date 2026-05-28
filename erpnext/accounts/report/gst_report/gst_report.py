

import frappe


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters=None):

    account_type = filters.get("account_type") if filters else None

    columns = [
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "Month",
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Voucher Type",
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Cost Center",
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 180
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
            "width": 120
        },
        {
            "label": "Voucher No",
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180
        },
        {
            "label": "Supplier / Customer",
            "fieldname": "supplier_name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "Bill Amount",
            "fieldname": "bill_amount",
            "fieldtype": "Currency",
            "width": 150
        }
    ]

    if account_type == "GST 5% Paid - CDCL":
        columns.append({
            "label": "5% GST Paid",
            "fieldname": "gst_paid",
            "fieldtype": "Currency",
            "width": 150
        })

    else:
        columns.append({
            "label": "5% GST Receive",
            "fieldname": "gst_receive",
            "fieldtype": "Currency",
            "width": 150
        })

    return columns


def get_data(filters):

    account_type = filters.get("account_type")
    month = filters.get("month")
    voucher_type = filters.get("voucher_type")

    values = {
        "account_type": account_type
    }

    month_condition = ""
    voucher_condition = ""

    if month:
        month_condition = " AND MONTHNAME(gl.posting_date) = %(month)s "
        values["month"] = month

    if voucher_type:
        voucher_condition = " AND gl.voucher_type = %(voucher_type)s "
        values["voucher_type"] = voucher_type

    # =========================================================
    # GST RECEIVED
    # =========================================================

    if account_type == "GST 5% Received - CDCL":

        query = f"""

            SELECT
                gl.posting_date,
                MONTHNAME(gl.posting_date) AS month,
                COALESCE( gl.cost_center,si.branch,pji.cost_center,hci.cost_center) AS cost_center,
         
                gl.voucher_type,
                gl.voucher_no,
            


                COALESCE(
                    r.gst_amount,
                    pji.gst_amount,
                    hci.gst_amount,
                    SUM(si_tax.tax_amount)
                ) AS gst_receive,

                NULL AS bill_no,

                COALESCE(
                    si.posting_date,
                    r.posting_date,
                    pji.invoice_date,
                    hci.posting_date
                ) AS bill_date,

                COALESCE(
                    si.customer,
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
                AND si_tax.account_head = %(account_type)s

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

            AND gl.account = %(account_type)s

            AND gl.is_cancelled = 0

            AND COALESCE(
                r.gst_amount,
                pji.gst_amount,
                hci.gst_amount,
                si_tax.tax_amount,
                0
            ) > 0

            {month_condition}
            {voucher_condition}

            GROUP BY gl.voucher_no

            ORDER BY gl.posting_date DESC
        """

        return frappe.db.sql(query, values, as_dict=1)

    # =========================================================
    # GST PAID
    # =========================================================

    elif account_type == "GST 5% Paid - CDCL":

        query = f"""

            SELECT
                gl.posting_date,
                MONTHNAME(gl.posting_date) AS month,
               
                COALESCE(gl.cost_center,pi.cost_center ,pol.cost_center) AS cost_center,
                gl.voucher_type,
                gl.voucher_no,

                COALESCE(
                    pol.gst_amount,
                    SUM(ptc.tax_amount)
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
                AND ptc.account_head = %(account_type)s

            LEFT JOIN `tabPOL Receive` pol
                ON gl.voucher_type = 'POL Receive'
                AND gl.voucher_no = pol.name

            WHERE gl.voucher_type IN (
                'Purchase Invoice',
                'POL Receive',
                'Utility Bill',
                'Imprest Recoup'
            )

            AND gl.account = %(account_type)s

            AND gl.is_cancelled = 0

            AND COALESCE(
                pol.gst_amount,
                ptc.tax_amount,
                0
            ) > 0

            {month_condition}
            {voucher_condition}

            GROUP BY gl.voucher_no

            ORDER BY gl.posting_date DESC
        """

        return frappe.db.sql(query, values, as_dict=1)

    return []