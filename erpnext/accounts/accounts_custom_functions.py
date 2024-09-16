import frappe

##
#Return all the child cost centers of the current cost center
##
def get_period_date(fiscal_year, period, cumulative=None):
    if not period or not fiscal_year:
        frappe.throw("Either Fiscal Year or Report Period is missing")

    values = ["from_date", "to_date"]
    if cumulative:
        values = ["c_from_date", "c_to_date"]
    from_date, to_date = frappe.db.get_value("Report Period", period, values)
    if from_date and to_date:
        from_date = str(fiscal_year) + str(from_date)
        to_date = str(fiscal_year) + str(to_date)
        return from_date, to_date
    else:
        frappe.throw("Report Period Not Defined Properly")

def get_child_cost_centers(current_cs=None):
    allchilds = allcs = [];
    cs_name = cs_par_name = "";

    if current_cs:
        #Get all cost centers
        allcs = frappe.db.sql("SELECT name, parent_cost_center FROM `tabCost Center`", as_dict=True)
        #get the current cost center name
        query ="SELECT name, parent_cost_center FROM `tabCost Center` where name = \"" + current_cs + "\";"
        current = frappe.db.sql(query, as_dict=True)

        if(current):
            for a in current:
                cs_name = a['name']
                cs_par_name = a['parent_cost_center']

        #loop through the cost centers to search for the child cost centers
        allchilds.append(cs_name)
        for b in allcs:
            for c in allcs:
                if(c['parent_cost_center'] in allchilds):
                    if(c['name'] not in allchilds):
                        allchilds.append(c['name'])

    return allchilds