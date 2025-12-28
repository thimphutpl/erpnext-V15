import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    # Filter out rows where all monthly values are zero
    filtered_data = [row for row in data if not all_zero(row)]
    return columns, filtered_data

def all_zero(row):
    """Check if all monthly budget values are zero"""
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    return all(float(row.get(month, 0) or 0) == 0 for month in months)

def get_columns():
    return [
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120},
        {"label": _("Cost Center"), "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": _("Fiscal Year"), "fieldname": "fiscal_year", "fieldtype": "Link", "options": "Fiscal Year", "width": 100},
        {"label": _("Parent Account"), "fieldname": "parent_account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"label": _("Account"), "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"label": _("Account Code"), "fieldname": "account_number", "fieldtype": "Data", "width": 100},
        {"label": _("Budget Type"), "fieldname": "budget_type", "fieldtype": "Data", "width": 100},
        {"label": _("Currency"), "fieldname": "account_currency", "fieldtype": "Link", "options": "Currency", "width": 80},
        {"label": _("January"), "fieldname": "january", "fieldtype": "Float", "width": 100},
        {"label": _("February"), "fieldname": "february", "fieldtype": "Float", "width": 100},
        {"label": _("March"), "fieldname": "march", "fieldtype": "Float", "width": 100},
        {"label": _("April"), "fieldname": "april", "fieldtype": "Float", "width": 100},
        {"label": _("May"), "fieldname": "may", "fieldtype": "Float", "width": 100},
        {"label": _("June"), "fieldname": "june", "fieldtype": "Float", "width": 100},
        {"label": _("July"), "fieldname": "july", "fieldtype": "Float", "width": 100},
        {"label": _("August"), "fieldname": "august", "fieldtype": "Float", "width": 100},
        {"label": _("September"), "fieldname": "september", "fieldtype": "Float", "width": 100},
        {"label": _("October"), "fieldname": "october", "fieldtype": "Float", "width": 100},
        {"label": _("November"), "fieldname": "november", "fieldtype": "Float", "width": 100},
        {"label": _("December"), "fieldname": "december", "fieldtype": "Float", "width": 100},
    ]

def get_data(filters):
    conditions = "b.docstatus = 1"
    
    if filters.get("company"):
        conditions += f" AND b.company = '{filters.get('company')}'"
    
    if filters.get("fiscal_year"):
        conditions += f" AND b.fiscal_year = '{filters.get('fiscal_year')}'"
    
    if filters.get("cost_center"):
        conditions += f" AND b.cost_center = '{filters.get('cost_center')}'"
    
    data = frappe.db.sql(f"""
        SELECT 
            b.company,
            b.cost_center,
            b.fiscal_year,
            b.budget_against,
            ba.parent_account,
            ba.account,
            ba.account_number,
            ba.budget_type,
            ba.january,
            ba.february,
            ba.march,
            ba.april,
            ba.may,
            ba.june,
            ba.july,
            ba.august,
            ba.september,
            ba.october,
            ba.november,
            ba.december,
            a.account_currency
        FROM 
            `tabBudget` b
        INNER JOIN 
            `tabBudget Account` ba ON ba.parent = b.name
        LEFT JOIN 
            `tabAccount` a ON ba.account = a.name
        WHERE
            {conditions}
        ORDER BY
            b.company, b.fiscal_year, b.cost_center, ba.account
    """, as_dict=1)
    
    return data