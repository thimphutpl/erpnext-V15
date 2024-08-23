import frappe
from frappe import _
from collections import defaultdict


def execute(filters=None):
    validate(filters)
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def validate(filters):
    """Validate that to_date_time is greater than or equal to from_date_time."""
    if filters.get('from_date_time') and filters.get('to_date_time'):
        from_date = filters['from_date_time']
        to_date = filters['to_date_time']
        
        if to_date <= from_date:
            frappe.throw(_("To Date Time must be greater than or equal to From Date Time."))

def get_columns(filters):
    if filters.get("hall_item"):
        return [
            {"fieldname": "resource_name", "label": _("Resource Name"),  "width": 150},
            {"fieldname": "resource_type", "label": _("Resource Type"), "fieldtype": "Data", "width": 150},
            {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
            {"fieldname": "from_date_time", "label": _("From Date Time"), "fieldtype": "Datetime", "width": 150},
            {"fieldname": "to_date_time", "label": _("To Date Time"), "fieldtype": "Datetime", "width": 150},
            {"fieldname": "resourcehall", "label": _("Resource"), "fieldtype": "Data", "width": 150},
            {"fieldname": "cost_center", "label": _("Agency"), "fieldtype": "Data", "width": 150},
        ]
    else:
        return [
            {"fieldname": "resource_name", "label": _("Resource Name"), "width": 150},
            {"fieldname": "resource_type", "label": _("Resource Type"), "fieldtype": "Data", "width": 150},
            {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
            {"fieldname": "from_date_time", "label": _("From Date Time"), "fieldtype": "Datetime", "width": 150},
            {"fieldname": "to_date_time", "label": _("To Date Time"), "fieldtype": "Datetime", "width": 150},
            {"fieldname": "cost_center", "label": _("Agency"), "fieldtype": "Data", "width": 150},
        ]

def get_conditions(filters):
    conditions = []

    if filters.get("docstatus"):
        conditions.append("tb.docstatus = '{}'".format(filters.get("docstatus")))

    if filters.get("resource_type"):
        conditions.append("td.resource_type = '{}'".format(filters.get("resource_type")))
    if filters.get("resource"):
        conditions.append("td.name = '{}'".format(filters.get("resource")))
    
    if filters.get("hall_item"):
        #frappe.throw(str(filters.get("hall_item"))
        #hall_items_list = [item.strip() for item in filters.get("hall_item").split(',')]
        hall_items_list=filters.get("hall_item")
        con=""
        for i in range(len(hall_items_list)):
            if i == len(hall_items_list)-1:
                con+=f"ta.resource = '{hall_items_list[i]}'"
            else: 
                con+=f"ta.resource = '{hall_items_list[i]}' OR "

        conditions.append(con)

        # conditions.append("ta.resource = '{}'".format(filters.get("hall_item"))) remarks: previous code
    if filters.get("agency"):
        conditions.append("td.cost_center = '{}'".format(filters.get("agency")))

    
    
    return " AND ".join(conditions) if conditions else "1=1"

def get_data(filters):

    if filters.get('from_date_time') and filters.get('to_date_time'):
        from_date = filters['from_date_time']
        to_date = filters['to_date_time']

        conditions = get_conditions(filters)
        conditions_clause = f"WHERE {conditions}" if conditions else ""
        
        if filters.get("hall_item"):
            query = f'''
                SELECT 
                    td.resource_name, 
                    td.resource_type,
                    tb.requesting_by,
                    tb.from_date_time,
                    tb.to_date_time,
                    ta.resource as resourcehall,
                    td.cost_center,
                    CASE
                        WHEN (tb.from_date_time IS NOT NULL OR tb.to_date_time IS NOT NULL) AND tb.docstatus='1' 
                        THEN 'Booked'
                        ELSE 'Available'
                    END AS status
                FROM 
                    `tabResource Directory` td
                LEFT JOIN 
                    `tabResource Booking` tb 
                    ON td.name = tb.resource 
                    AND (
                        tb.from_date_time BETWEEN %(from_date)s AND %(to_date)s OR
                        tb.to_date_time BETWEEN %(from_date)s AND %(to_date)s OR
                        (tb.from_date_time <= %(from_date)s AND tb.to_date_time >= %(to_date)s)
                    )
                    AND(
                        tb.docstatus='1'
                    )
                LEFT JOIN `tabResource Available` ta ON ta.parent=td.name
                {conditions_clause}
            '''
        else:
            query = f'''
                SELECT 
                    td.resource_name, 
                    td.resource_type,
                    tb.requesting_by,
                    tb.from_date_time,
                    tb.to_date_time,
                    td.cost_center,
                    CASE
                        WHEN (tb.from_date_time IS NOT NULL OR tb.to_date_time IS NOT NULL) AND tb.docstatus='1' 
                        THEN 'Booked'
                        ELSE 'Available'
                    END AS status
                FROM 
                    `tabResource Directory` td
                LEFT JOIN 
                    `tabResource Booking` tb 
                    ON td.name = tb.resource 
                    AND (
                        tb.from_date_time BETWEEN %(from_date)s AND %(to_date)s OR
                        tb.to_date_time BETWEEN %(from_date)s AND %(to_date)s OR
                        (tb.from_date_time <= %(from_date)s AND tb.to_date_time >= %(to_date)s)
                    ) 
                    AND(
                        tb.docstatus='1'
                    )
                {conditions_clause}
                
            '''


        data = frappe.db.sql(query, {'from_date': from_date, 'to_date': to_date}, as_dict=True)
        #frappe.throw(str(data))

        if filters.get("hall_item"):
            aggregated_data = defaultdict(lambda: {
                'resource_type': None, 'requesting_by': None, 'from_date_time': None, 'to_date_time': None, 'cost_center': None, 'status': None, 'resourcehall': set()
            })
            
            for item in data:
                key = item['resource_name']
                aggregated_data[key]['resource_type'] = item['resource_type']
                aggregated_data[key]['requesting_by'] = item['requesting_by']
                aggregated_data[key]['from_date_time'] = item['from_date_time']
                aggregated_data[key]['to_date_time'] = item['to_date_time']
                aggregated_data[key]['cost_center'] = item['cost_center']
                aggregated_data[key]['status'] = item['status']
                aggregated_data[key]['resourcehall'].add(item['resourcehall'])

            # Convert sets to lists for JSON serialization
            for key, values in aggregated_data.items():
                values['resourcehall']= list(values['resourcehall'])

            # Convert aggregated data to a list
            result = [{'resource_name': key, **value} for key, value in aggregated_data.items()]
            #frappe.throw(str(filters.get("hall_item")))

            output=[]
            for row in result:
                limit=0
                for item in filters.get("hall_item"):
                    if item in row["resourcehall"]:
                        limit+=1
                if limit==len(filters.get("hall_item")):
                    row["resourcehall"]=", ".join(row["resourcehall"])
                    output.append(row)
                    

                
            #frappe.throw(str(output))


            
            return output
        else:
            return data
    else:
        return []

