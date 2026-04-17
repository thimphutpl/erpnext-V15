# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import datetime
from frappe.utils import flt, getdate, formatdate, cstr, get_first_day, get_last_day

def execute(filters=None):
    validate_filters(filters)
    from_date, to_date = None, None
    if filters.monthly_budget:
        if filters.month:
            for month_id in range(1, 13):
                month = datetime.date(2013, month_id, 1).strftime("%B")
                if filters.month == month:
                    month_num = str("0")+str(month_id) if month_id < 10 else str(month_id)
                    first_day = filters.fiscal_year + "-" + month_num + "-" + "01"
            from_date = getdate(first_day)
            to_date = get_last_day(from_date)
    if not from_date and not to_date:
        from_date = filters.from_date
        to_date = filters.to_date

    columns = get_columns(filters)
    queries = construct_query(from_date, to_date, filters)
    data = get_data(queries, from_date, to_date, filters)

    extra_data = get_extra_entries(filters, from_date, to_date)
    data.extend(extra_data)
    get_suppl= get_supplementary_items(filters,from_date,to_date)
    data.extend(get_suppl)
    
    return columns, data



def get_extra_entries(filters, from_date, to_date):
    """Get committed/consumed entries that don't have corresponding budget records"""
    data = []
    budget_level = filters.budget_against
    
    committed_conditions = get_committed_conditions(filters)
    committed_query = """
        SELECT DISTINCT account, cost_center, project, budget_activity, 
               budget_sub_activity, source_of_fund
        FROM `tabCommitted Budget`
        WHERE reference_date BETWEEN %s AND %s
        {conditions}
    """.format(conditions=committed_conditions)
    
    committed_params = [from_date, to_date]
    if filters.cost_center:
        committed_params.append(filters.cost_center)
    if filters.project:
        committed_params.append(filters.project)
    if filters.budget_type:
        committed_params.append(filters.budget_type)
        
    committed_entries = frappe.db.sql(committed_query, tuple(committed_params), as_dict=True)
    
    consumed_conditions = get_consumed_conditions(filters)
    consumed_query = """
        SELECT DISTINCT account, cost_center, project, budget_activity, 
               budget_sub_activity, source_of_fund
        FROM `tabConsumed Budget`
        WHERE reference_date BETWEEN %s AND %s
        {conditions}
    """.format(conditions=consumed_conditions)
    
    consumed_params = [from_date, to_date]
    if filters.cost_center:
        consumed_params.append(filters.cost_center)
    if filters.project:
        consumed_params.append(filters.project)
    if filters.budget_type:
        consumed_params.append(filters.budget_type)
        
    consumed_entries = frappe.db.sql(consumed_query, tuple(consumed_params), as_dict=True)
    
    all_entries = committed_entries + consumed_entries
    unique_entries = {(
        entry['account'], 
        entry['cost_center'], 
        entry.get('project'), 
        entry['budget_activity'], 
        entry['budget_sub_activity'], 
        entry['source_of_fund']
    ): entry for entry in all_entries}.values()
    for entry in unique_entries:
        exists_query = """
            SELECT 1 FROM `tabBudget Account` ba
            JOIN `tabBudget` b ON ba.parent = b.name
            WHERE ba.account = %s 
            AND b.cost_center = %s
            AND ba.budget_activity = %s
            AND ba.budget_sub_activity = %s
            AND ba.source_of_fund = %s
            AND b.fiscal_year = %s
            AND b.docstatus = 1
        """
        exists_params = [
            entry['account'],
            entry['cost_center'],
            entry['budget_activity'],
            entry['budget_sub_activity'],
            entry['source_of_fund'],
            filters.fiscal_year
        ]
        # frappe.throw(str(exists_query))
        
        if frappe.db.sql(exists_query, tuple(exists_params)):
            continue  
            
        committed = frappe.db.sql("""
            SELECT SUM(amount) 
            FROM `tabCommitted Budget` 
            WHERE account = %s 
            AND cost_center = %s 
            AND budget_activity = %s 
            AND budget_sub_activity = %s 
            AND source_of_fund = %s 
            AND reference_date BETWEEN %s AND %s
        """, (
            entry['account'],
            entry['cost_center'],
            entry['budget_activity'],
            entry['budget_sub_activity'],
            entry['source_of_fund'],
            from_date,
            to_date
        ))[0][0] or 0
        
        consumed = frappe.db.sql("""
            SELECT SUM(amount) 
            FROM `tabConsumed Budget` 
            WHERE account = %s 
            AND cost_center = %s 
            AND budget_activity = %s 
            AND budget_sub_activity = %s 
            AND source_of_fund = %s 
            AND reference_date BETWEEN %s AND %s
        """, (
            entry['account'],
            entry['cost_center'],
            entry['budget_activity'],
            entry['budget_sub_activity'],
            entry['source_of_fund'],
            from_date,
            to_date
        ))[0][0] or 0
        
        if committed > 0:
            committed -= consumed
            committed = 0 if committed < 0 else committed
            
        current = 0  # Initial Proposed + Adjustment = 0 + 0 = 0
        available = current - consumed  # CHANGED: Available = Current - Consumed
            
        if filters.budget_against != "Project":
            row = {
                "account": entry['account'],
                "cost_center": entry['cost_center'],
                "budget_activity": entry['budget_activity'],
                "budget_sub_activity": entry['budget_sub_activity'],
                "source_of_fund": entry['source_of_fund'],
                "initial": 0,
                "initial_release": 0,
                "supplementary": 0,
                "release_supplementary": 0,
                "adjustment": 0,
                "release_adjustment": 0,
                "current": current,
                "committed": committed,
                "consumed": consumed,
                "available": available,
                "release_available": available,  # Also update release_available to match
            }
        else:
            row = {
                "account": entry['account'],
                "project": entry.get('project'),
                "project_name": frappe.db.get_value("Project", entry.get('project'), "project_name") if entry.get('project') else "",
                "cost_center": entry['cost_center'],
                "initial": 0,
                "initial_release": 0,
                "supplementary": 0,
                "release_supplementary": 0,
                "adjustment": 0,
                "release_adjustment": 0,
                "current": current,
                "committed": committed,
                "consumed": consumed,
                "available": available,
                "release_available": available,  # Also update release_available to match
            }
            
        data.append(row)
    
    return data

def get_committed_conditions(filters):
    conditions = ""
    if filters.cost_center:
        conditions += " AND cost_center = %s"
    if filters.project:
        conditions += " AND project = %s"
    if filters.budget_type:
        conditions += " AND budget_type = %s"
    return conditions

def get_consumed_conditions(filters):
    conditions = ""
    if filters.cost_center:
        conditions += " AND cost_center = %s"
    if filters.project:
        conditions += " AND project = %s"
    if filters.budget_type:
        conditions += " AND budget_type = %s"
    return conditions

def get_data(query, from_date, to_date, filters):
    data = []
    datas = frappe.db.sql(query, as_dict=True)
    budget_level = filters.budget_against
    
    for d in datas:
        if filters.monthly_budget:
            initial_budget = d.monthly_budget
            supplement = flt(frappe.db.sql("""
                select sum(amount)
                from `tabSupplementary Details`
                where month ="{month}"
                and account="{account}"
                and cost_center="{cost_center}"
                and posting_date between '{from_date}' and '{to_date}'
            """.format(month=filters.month, from_date=from_date, to_date=to_date, account=d.account, cost_center=d.cost_center))[0][0], 2)
            
            monthly_received = frappe.db.sql("""
                select sum(amount)
                from `tabReappropriation Details`
                where to_month="{month}"
                and to_account="{account}"
                and to_cost_center="{cost_center}"
            """.format(month=filters.month, account=d.account, cost_center=d.cost_center))[0][0]
            
            monthly_sent = frappe.db.sql("""
                select sum(amount)
                from `tabReappropriation Details`
                where from_month="{month}"
                and from_account="{account}"
                and from_cost_center="{cost_center}"
            """.format(month=filters.month, account=d.account, cost_center=d.cost_center))[0][0]
            
            adjustment = flt(monthly_received, 2) - flt(monthly_sent, 2)
            release_adjustment = 0
            initial_budget_release = 0
            release_supplement = 0
        else:
            initial_budget = d.initial_budget
            initial_budget_release = d.initial_budget_release
            adjustment = flt(d.added) - flt(d.deducted)
            release_adjustment = flt(d.release_added) - flt(d.release_deducted)
            supplement = flt(d.supplement)
            release_supplement = flt(d.release_supplement)
        
        # Current = Initial Proposed + Adjustment
        current = flt(initial_budget_release) + flt(adjustment) + flt(supplement)

        if filters.monthly_budget:
            cost_center = d.cost_center
            committed = frappe.db.sql("""
                select SUM(amount) from `tabCommitted Budget` 
                where cost_center = %s and account = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.cost_center, d.account, d.budget_activity, d.budget_sub_activity, d.source_of_fund, from_date, to_date))[0][0]
            
            consumed = frappe.db.sql("""
                select SUM(amount) from `tabConsumed Budget` 
                where cost_center = %s and account = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.cost_center, d.account, d.budget_activity, d.budget_sub_activity, d.source_of_fund, from_date, to_date))[0][0]
            
        elif filters.group_by_account and filters.budget_against != "Project":
            cost_center = ""
            committed = frappe.db.sql("""
                select SUM(amount) from `tabCommitted Budget` 
                where account = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.account, d.budget_activity, d.budget_sub_activity, d.source_of_fund, filters.from_date, filters.to_date))[0][0]
            
            consumed = frappe.db.sql("""
                select SUM(amount) from `tabConsumed Budget` 
                where account = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.account, d.budget_activity, d.budget_sub_activity, d.source_of_fund, filters.from_date, filters.to_date))[0][0]
            
        elif filters.budget_against == "Project":
            project = filters.project
            committed = frappe.db.sql("""
                select SUM(amount) from `tabCommitted Budget` 
                where cost_center = %s and project = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.cost_center, d.project, d.budget_activity, d.budget_sub_activity, d.source_of_fund, filters.from_date, filters.to_date))[0][0]
            
            consumed = frappe.db.sql("""
                select SUM(amount) from `tabConsumed Budget` 
                where cost_center = %s and project = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.cost_center, d.project, d.budget_activity, d.budget_sub_activity, d.source_of_fund, filters.from_date, filters.to_date))[0][0]
            
        else:
            cost_center = d.cost_center
            committed = frappe.db.sql("""
                select SUM(amount) from `tabCommitted Budget` 
                where cost_center = %s and account = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.cost_center, d.account, d.budget_activity, d.budget_sub_activity, d.source_of_fund, filters.from_date, filters.to_date))[0][0]
            
            consumed = frappe.db.sql("""
                select SUM(amount) from `tabConsumed Budget` 
                where cost_center = %s and account = %s and budget_activity = %s 
                and budget_sub_activity = %s and source_of_fund = %s 
                and reference_date BETWEEN %s and %s
            """, (d.cost_center, d.account, d.budget_activity, d.budget_sub_activity, d.source_of_fund, filters.from_date, filters.to_date))[0][0]

        committed = flt(committed) or 0
        consumed = flt(consumed) or 0

        if committed > 0:
            committed -= consumed
            committed = 0 if committed < 0 else committed

        # CHANGED: Available = Current - Consumed
        available = current - consumed
        release_available = available  # Also set release_available to the same value

        if d.budget_amount > 0:
            if filters.budget_against != "Project":
                row = {
                    "account": d.account,
                    "cost_center": cost_center,
                    "budget_activity": d.budget_activity,
                    "budget_sub_activity": d.budget_sub_activity,
                    "source_of_fund": d.source_of_fund,
                    "initial": flt(initial_budget),
                    "initial_release": flt(initial_budget_release),
                    "supplementary": supplement,
                    "release_supplementary": release_supplement,
                    "adjustment": adjustment,
                    "release_adjustment": release_adjustment,
                    "current": current,
                    "committed": committed,
                    "consumed": consumed,
                    "available": available,
                    "release_available": release_available,
                }
            else:
                row = {
                    "account": d.account,
                    "project": d.project,
                    "project_name": d.project_name,
                    "cost_center": d.cost_center,
                    "initial": flt(initial_budget),
                    "initial_release": flt(initial_budget_release),
                    "supplementary": supplement,
                    "release_supplementary": release_supplement,
                    "adjustment": adjustment,
                    "release_adjustment": release_adjustment,
                    "current": current,
                    "committed": committed,
                    "consumed": consumed,
                    "available": available,
                    "release_available": release_available,
                }

            data.append(row)
    return data

def get_supplementary_items(filters, from_date, to_date):
    """Fetch only 'New Supplementary Budget' items or filtered parent budget"""

    conditions = ["sb.supplementary_type='New Supplementary Budget'"]
    params = []
    if filters.parent_budget:
        conditions.append("sbi.parent=%s")
        params.append(filters.parent_budget)
    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            sb.cost_center,
            sb.company,
            sb.fiscal_year,
            sb.posting_date,
            sbi.account,
            sbi.account_number,
            sbi.amount,
            sbi.budget_activity,
            sbi.budget_sub_activity
        FROM `tabSupplementary Budget` sb
        JOIN `tabSupplementary Budget Item` sbi ON sb.name = sbi.parent
        WHERE {where_clause}
    """

    items = frappe.db.sql(query, tuple(params), as_dict=True)
    data = []

    for d in items:
        committed = flt(frappe.db.sql("""
            SELECT SUM(amount)
            FROM `tabCommitted Budget`
            WHERE account=%s AND budget_activity=%s AND budget_sub_activity=%s
              AND reference_date BETWEEN %s AND %s
        """, (d.account, d.budget_activity, d.budget_sub_activity, from_date, to_date))[0][0] or 0)

        consumed = flt(frappe.db.sql("""
            SELECT SUM(amount)
            FROM `tabConsumed Budget`
            WHERE account=%s AND budget_activity=%s AND budget_sub_activity=%s
              AND reference_date BETWEEN %s AND %s
        """, (d.account, d.budget_activity, d.budget_sub_activity, from_date, to_date))[0][0] or 0)

        available = flt(d.amount) - consumed

        row = {
            "account": d.account,
            "cost_center": d.cost_center,
            "budget_activity": d.budget_activity,
            "budget_sub_activity": d.budget_sub_activity,
            "initial": 0,
            "initial_release": 0,
            "supplementary": flt(d.amount),
            "release_supplementary": 0,
            "adjustment": 0,
            "release_adjustment": 0,
            "current": flt(d.amount),
            "committed": committed,
            "consumed": consumed,
            "release_available": available
        }

        data.append(row)

    return data

# The rest of the functions (construct_query, validate_filters, get_columns) remain the same as in the previous version
def construct_query(from_date, to_date, filters=None):
    condition = ''
    if filters.budget_against == "Cost Center" and filters.cost_center:
        condition += " and b.cost_center = \'" + str(filters.cost_center) + "\' "
        condition += " and br.cost_center = \'" + str(filters.cost_center) + "\' "
        
    if filters.budget_type:
        condition += " and ba.budget_type = \'" + str(filters.budget_type) + "\' "
        condition += " and br.budget_type = \'" + str(filters.budget_type) + "\' "
    
    if filters.cost_center and not filters.group_by_account:
        lft, rgt = frappe.db.get_value("Cost Center", filters.cost_center, ["lft", "rgt"])
        condition += """ and (b.cost_center in (select a.name 
                                        from `tabCost Center` a 
                                        where a.lft >= {1} and a.rgt <= {2}
                                        ) 
                 or b.cost_center = '{0}')
        """.format(filters.cost_center, lft, rgt)
        condition += """ and (br.cost_center in (select a.name 
                                        from `tabCost Center` a 
                                        where a.lft >= {1} and a.rgt <= {2}
                                        ) 
                 or br.cost_center = '{0}')
        """.format(filters.cost_center, lft, rgt)
    if filters.budget_type:
        condition += " and ba.budget_type = \'" + str(filters.budget_type) + "\' "
        condition += " and bra.budget_type = \'" + str(filters.budget_type) + "\' "

    if filters.monthly_budget and filters.month:
        month_field_name = filters.month
        query = """select b.cost_center, ba.account, b.project, ba.budget_activity, ba.budget_sub_activity, ba.source_of_fund,
            (select a.account_number from `tabAccount` a where a.name = ba.account) as account_number, 
            ba.budget_type,
            SUM(ba.approved_budget) as approved_budget,
            SUM(ba.budget_amount) as budget_amount,
            sum(ba.{month_name}) as monthly_budget,
            SUM(ba.initial_budget) as initial_budget, 
            SUM(ba.budget_received) as added, 
            SUM(ba.budget_sent) as deducted, 
            SUM(ba.supplementary_budget) as supplement
        from `tabBudget` b, `tabBudget Account` ba 
        where b.docstatus = 1 
            and b.name = ba.parent 
            and b.fiscal_year = "{fiscal_year}"
        {condition}
        group by ba.account, b.cost_center, ba.budget_activity, ba.budget_sub_activity, ba.source_of_fund order by b.cost_center
        """.format(fiscal_year=filters.fiscal_year, condition=condition, month_name=month_field_name.lower())
    else:
        query = """select b.cost_center, ba.account, b.project, ba.budget_activity, ba.budget_sub_activity, ba.source_of_fund,
            (select a.account_number from `tabAccount` a where a.name = ba.account) as account_number, 
            ba.budget_type,
            SUM(ba.approved_budget) as approved_budget,
            SUM(ba.budget_amount) as budget_amount, 
            SUM(bra.budget_amount) as budget_release_amount, 
            (ba.initial_budget) as initial_budget, 
            SUM(bra.released_budget) as initial_budget_release, 
            SUM(ba.budget_received) as added, 
            SUM(bra.budget_received) as release_added, 
            SUM(ba.budget_sent) as deducted, 
            SUM(bra.budget_sent) as release_deducted, 
            SUM(ba.supplementary_budget) as supplement,
            SUM(bra.supplementary_budget) as release_supplement
        from `tabBudget` b 
        left join `tabBudget Account` ba on ba.parent = b.name 
        left join `tabBudget Release` br on br.budget_id = b.name and br.docstatus = 1 
        left join `tabBudget Release Account` bra on bra.parent = br.name 
            and bra.budget_activity = ba.budget_activity 
            and bra.budget_sub_activity = ba.budget_sub_activity 
            and bra.source_of_fund = ba.source_of_fund 
            and bra.account = ba.account
        where b.docstatus = 1
            and b.fiscal_year = "{fiscal_year}"
        {condition}
        """.format(fiscal_year=filters.fiscal_year, condition=condition)
        
        if filters.group_by_account:
            query += " group by ba.account "
        elif filters.budget_against == "Project":
            query += " group by b.cost_center, b.project"
        else:
            query += " group by ba.account, b.cost_center, ba.budget_activity, ba.budget_sub_activity, ba.source_of_fund order by b.cost_center"
    
    return query

def validate_filters(filters):
    if not filters.fiscal_year:
        frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

    fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
    if not fiscal_year:
        frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
    else:
        filters.year_start_date = getdate(fiscal_year.year_start_date)
        filters.year_end_date = getdate(fiscal_year.year_end_date)

    if not filters.from_date:
        filters.from_date = filters.year_start_date

    if not filters.to_date:
        filters.to_date = filters.year_end_date

    filters.from_date = getdate(filters.from_date)
    filters.to_date = getdate(filters.to_date)

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date"))

    if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
        frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
            .format(formatdate(filters.year_start_date)))
        filters.from_date = filters.year_start_date

    if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
        frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
            .format(formatdate(filters.year_end_date)))
        filters.to_date = filters.year_end_date

def get_columns(filters):
    return [
        {
            "fieldname": "account",
            "label": "Account Head",
            "fieldtype": "Link",
            "options": "Account",
            "width": 200
        },
        {
            "fieldname": "cost_center",
            "label": "Cost Center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 150
        },
        {
            "fieldname": "budget_activity",
            "label": "Budget Activity",
            "fieldtype": "Link",
            "options": "Budget Activity",
            "width": 150
        },
        {
            "fieldname": "budget_sub_activity",
            "label": "Budget Sub Activity",
            "fieldtype": "Link",
            "options": "Budget Sub Activity",
            "width": 150
        },
        {
            "fieldname": "source_of_fund",
            "label": "Source of Fund",
            "fieldtype": "Link",
            "options": "Source of Fund",
            "width": 150
        },
        {
            "fieldname": "initial",
            "label": "Initial Proposed",
            "fieldtype": "Currency",
            "width": 120
        },
        # {
        #     "fieldname": "approved_budget",
        #     "label": "Approved Budget",
        #     "fieldtype": "Currency",
        #     "width": 120
        # },
        {
            "fieldname": "initial_release",
            "label": "Initial Released",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "supplementary",
            "label": "Supplement",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "fieldname": "release_supplementary",
            "label": "Supplement Released",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "fieldname": "adjustment",
            "label": "Adjustment",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "release_adjustment",
            "label": "Released Adjustment",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "current",
            "label": "Current",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "committed",
            "label": "Committed",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "consumed",
            "label": "Consumed",
            "fieldtype": "Currency",
            "width": 120
        },
        # {
        #     "fieldname": "available",
        #     "label": "Available",
        #     "fieldtype": "Currency",
        #     "width": 120
        # },
        {
            "fieldname": "release_available",
            "label": "Available",
            "fieldtype": "Currency",
            "width": 120
        }
    ]


